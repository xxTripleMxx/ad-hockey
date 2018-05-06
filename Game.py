import json
import urllib
import statistics as stat
from datetime import timedelta as td
from Players import Goalie, Skater
from Events import *
from Summaries import Summary
from Functionality import Container


class Game(object):
    ''' game_no - # of game as it occurred chronologically that season
        game_type - 01: preseason, 02:regular season, 03:playoffs, 04:All-star
        season_year - 4 digit year'''

    def __init__(self, game_no,  game_type, season_year):

        self.game_args = {"game_no": str(game_no),
                          "game_type": str(game_type),
                          "season_year": str(season_year)}
        self.game_id = str(season_year) + str(game_type) + str(game_no)
        self.json_data = self._set_json()
        self.teams = {'home': self.json_data['gameData']['teams']['home']['triCode'],
                      'away': self.json_data['gameData']['teams']['away']['triCode']}
        self.net_locations = self._net_x()
        self.events_exclude = ["game scheduled", "period ready", "period start",
                               "period end", "period official", "game end",
                               "shootout complete", "game official"]
        
        # Summary object of many summary stats from the game
        self.summary = Summary(self.json_data)
        # Container of all players in the game
        self.players = Container(list(self._populate_players()))
        # Container of all events in the game
        self.events = Container(list(self._populate_events()))
        

    def _set_json(self):
        '''Combine provided game no. season no. and gametype from instantiation
        and create an url to retrieve the relevent JSON data from nhl.com '''

        url_start = "https://statsapi.web.nhl.com/api/v1/game/"
        url_end = "/feed/live"
        full_url = str(url_start + self.game_args["season_year"] +
                       self.game_args["game_type"] +
                       self.game_args["game_no"] + url_end)
        
        try:
            game_url = urllib.request.urlopen(full_url).read()
            game_json = json.loads(game_url)

            if str(game_json["gamePk"]) == (self.game_args["season_year"] +
                                            self.game_args["game_type"] +
                                            self.game_args["game_no"]):
                print("Accessing JSON feed at: " + full_url)
                print("JSON feed for game " + self.game_args["game_no"] +
                      " validated!")
                if len(game_json['liveData']['plays']['allPlays']) < 5:
                    raise Exception("No live data available for game no. " +
                                    self.game_args['game_no'])
                else:
                    # set class attribute json_data to loaded data
                    return game_json
            else:
                print(self.game_args["season_year"] +
                      self.game_args["game_type"] +
                      self.game_args["game_no"] +
                      " does not equal " + game_json['gamePk'])
                print("Url game ID and ID did not match")

        except urllib.error.HTTPError as err:

            if err.code == 404:
                print("404 ERROR")
                print("Unable to load specified Live Game Data feed at:")
                print(full_url)

    def _net_x(self):
        '''retrieves the json data pertaining to the corresponding side
        of the ice for each team's net throughout the game (left or right).
        Then assign's accurate x coordinates to each.'''
        
        try:
            net_dict = {}
            for p in self.json_data['liveData']['linescore']['periods']:
                for loc in ['home', 'away']:
                    team = self.json_data['gameData']['teams'][loc]['abbreviation']
                    net_dict[team+str(p['num'])] = [89 if p[loc]['rinkSide']
                                                    == 'left' else -89][0]
        
        except KeyError:
            net_dict = {x+str(n):[] for x in self.teams.values() for n in range(1,5)}
            for x in self.json_data['liveData']['plays']['allPlays']:
                try:
                    if x['result']['event'].lower() == 'shot':
                        net_dict[x['team']['triCode']+str(x['about']['period'])].append(int(x['coordinates']['x']))
                except KeyError:
                    pass
            
            net_dict = {t:stat.mean(nl) for t,nl in net_dict.items() if len(nl) > 0}
            
        return net_dict
        

    # Event Factory
    def _populate_events(self):

        jsn = self.json_data
        plays_list = jsn['liveData']['plays']['allPlays']

        def classify_event(pl, n):
            '''Retrieves the name, period and time of an event and instantiates
            the corresponding object with the event data.'''
            event = pl[n]['result']['event'].lower()
            period = pl[n]['about']['period']
            t = pl[n]['about']['periodTime'].split(':')
            time = td(minutes=int(t[0]), seconds=int(t[1])).total_seconds()

            '''checks retrieved event string against the exclusions list
            in Game.exclude_list'''
            if event in self.events_exclude:
                # << create a proper warning here >>
                print('WARNING: ' + event +
                      ' not classified due to deliberate' +
                      'exclusion (see event exclusion list)')
                return

            ''' this dictionary is the master classification dictionary for
            events. Each value contains a tuple, 0th index being event
            names as processed from the JSON then lowered, the 1th index
            corresponding to that event string's master object.'''
            e_cls_dict = {0: (["shot", "goal", "missed shot"], OffensivePuck),
                          1: (['puck frozen', 'blocked shot'], DefensivePuck),
                          2: (['faceoff'], FaceOff),
                          3: (['stoppage'], Stoppage),
                          4: (['takeaway', 'giveaway'], PuckTransfer),
                          5: (["hit"], Hit),
                          6: (["penalty"], Penalty),
                          7: (["player injury"], Injury)}

            '''attribute dictionary used to instantiate correct event subobject
            '''
            attributes = {'event': event, 'period': period, 
                          'time': time}

            for flt in range(0, 9):
                if flt == 8:
                    return Event(attributes, pl, n)
                    print("WARNING: Failed to classify event: " +
                          attributes['event'])
                elif attributes['event'] in e_cls_dict[flt][0]:
                    if flt == 0:
                        return e_cls_dict[flt][1](attributes, pl, n,
                                                  self.net_locations)
                    else:
                        return e_cls_dict[flt][1](attributes, pl, n)
                    break

        ''' iterates through the events list provided by the JSON data in
        sequential order with cnt. Then checks that event was properly
        instantiated and increments cnt upon confirmation, yielding
        newly classified event.'''
        
        '''Evaluates for penalty time and assigns a man advantage differential
        to each event based one wether that event occurred while a penalty was
        was active.'''
        
        
        '''Use a mix of in and out scope elements to determine 
        balance between teams regarding on ice players for each event'''
        def man_advantage(ev):
            if ev.event == 'penalty':
                active_penalty[ev.team].append((ev.period, ev.time, ev.end_time))
                man_count[ev.team] = 5 - len(active_penalty[ev.team])
            elif 'team' in ev.__dict__:
                if (len(active_penalty[ev.team]) > 0):
                    for pen in active_penalty[ev.team]: 
                        if ((ev.time > pen[1]) and
                            (ev.time < pen[2]) and
                            (ev.period == pen[0])):
                            pass
                        elif ev.time > pen[2]:
                            active_penalty[ev.team].remove(pen) 
                            man_count[ev.team] = 5 - len(active_penalty[ev.team])
                opp_team = [x for x in man_count.keys() if x != ev.team].pop()
                ev.poi = man_count[ev.team] - man_count[opp_team]
            return ev
        
        cnt = 0
        man_count = {x: 5 for x in self.teams.values()}
        active_penalty = {x: [] for x in self.teams.values()}
        for n in range(0, len(plays_list)):
            event = classify_event(plays_list, n)
            if isinstance(event, Event):
                event = man_advantage(event)
                cnt += 1
                yield event

    # Player Factory
    def _populate_players(self):

        for loc in ['home', 'away']:
            teams = self.json_data['liveData']['boxscore']['teams']
            # Player non-game specific information
            plyr_global = self.json_data['gameData']['players']
            # Player game specific information
            plyr_game = teams[loc]['players']
            # Team abbreviation
            team = teams[loc]['team']['triCode'].upper()

            for plyr_id in plyr_game.keys():
                position = plyr_game[plyr_id]['position']['abbreviation'].upper()
                if position == 'G':
                    yield Goalie(position, team, plyr_id,
                                 plyr_global, plyr_game)
                elif position == 'N/A' and plyr_game[plyr_id]['stats'] == {}:
                    continue
                else:
                    yield Skater(position, team, plyr_id,
                                 plyr_global, plyr_game)
