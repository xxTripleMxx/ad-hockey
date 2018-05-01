import json
import urllib
import math
import re
from datetime import datetime as dt


class Game(object):
    ''' game_no - # of game as it occurred chronologically that season
        game_type - 01: preseason, 02:regular season, 03:playoffs, 04:All-star
        season_year - 4 digit year'''

    def __init__(self, game_no,  game_type, season_year):

        self.game_args = {"game_no": str(game_no),
                          "game_type": str(game_type),
                          "season_year": str(season_year)}
        self.json_data = self._set_json()
        self.net_locations = self._net_x()
        self.events_exclude = ["game scheduled", "period ready", "period start",
                               "period end", "period official", "game end",
                               "shootout complete", "game official"]

        # Container of all players in the game
        self.players = Container(list(self._populate_players()))
        # Container of all events in the game
        self.events = Container(list(self._populate_events()))
        # Summary object of many summary stats from the game
        self.summary = Summary(self.json_data)

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
        net_dict = {}
        for p in self.json_data['liveData']['linescore']['periods']:
            for loc in ['home', 'away']:
                team = self.json_data['gameData']['teams'][loc]['abbreviation']
                net_dict[team+str(p['num'])] = [89 if p[loc]['rinkSide']
                                                == 'left' else -89][0]

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
            time = pl[n]['about']['periodTime']

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
            attributes = {'event': event, 'period': period, 'time': time}

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
        cnt = 0
        for n in range(0, len(plays_list)):
            event = classify_event(plays_list, n)
            if isinstance(event, Event):
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


class Summary(object):

    def __init__(self, json_data):

        time = json_data['gameData']['datetime']
        self.start_time = dt.strptime(time['dateTime'], '%Y-%m-%dT%H:%M:%SZ')
        self.end_time = dt.strptime(time['endDateTime'], '%Y-%m-%dT%H:%M:%SZ')
        self.venue = json_data['gameData']['venue']['name']
        self.team_metrics = list(self._populate_metrics(json_data))

    def __repr__(self):
        teams = [x.abbr for x in self.team_metrics]
        return teams[0]+' vs '+teams[1]

    class Team(object):

        def __init__(self, summary_dict):

            for k, v in summary_dict.items():
                setattr(self, k, v)

        def __repr__(self):
            return self.abbr

    def _populate_metrics(self, json_data):

        bx = json_data['liveData']['boxscore']['teams']
        gm = json_data['gameData']['teams']

        for l in ['away', 'home']:

            t = self.Team(bx[l]['teamStats']['teamSkaterStats'])
            t.abbr = gm[l]['abbreviation']
            t.loc = l
            t.conf = gm[l]['conference']['name']
            t.div = gm[l]['division']['name']
            t.tz = gm[l]['venue']['timeZone']['tz']
            t.tz_offset = gm[l]['venue']['timeZone']['offset']

            yield t


class Container(object):

    def __init__(self, wrapped_list):

        self._wl = wrapped_list

    def __repr__(self):
        return self._wl[0].__class__.__bases__[0].__name__ + 'Container'

    def __call__(self):
        return self._wl

    # allow no filtering
    # remove keys where entire value list is nans
    def to_dict(self,  attributes='all', filts='all'):

        filt_dict = {d: [] for x in self._wl for d in (x.__dict__.keys())}
        if (attributes != 'all') and (filts != 'all'):
            types = {e[attributes] for e in self._wl}

        for x in self._wl:
            if (filts != 'all') and (str(filts) in types or
                                     set(filts).issubset(set(types))):
                if (x[attributes] != filts and x[attributes] not in filts):
                    pass
                else:
                    for k in filt_dict.keys():
                        try:
                            filt_dict[k].append(x.__dict__[k])
                        except KeyError:
                            filt_dict[k].append(float('nan'))
            elif (filts == 'all') and (attributes == 'all'):
                for k in filt_dict.keys():
                        try:
                            filt_dict[k].append(x.__dict__[k])
                        except KeyError:
                            filt_dict[k].append(float('nan'))

        return filt_dict


class Event(object):

    def __getitem__(cls, x):
        return getattr(cls, x)

    def __init__(self, attribute_dictionary, json_data, ind):

        for k, v in attribute_dictionary.items():
            setattr(self, k, v)
        self._set_attributes(json_data, ind)

    def __repr__(self):
        return self.__class__.__name__

    def _set_attributes(self, json_data, ind):
        j = json_data[ind]
        # see if there are x and y coordinates anywhere
        attr_dict = {'x_coord': lambda: j['coordinates']['x'],
                     'y_coord': lambda: j['coordinates']['y'],
                     'team': lambda: j['team']['triCode'],
                     'p1_name': lambda: j['players'][0]['player']['fullName'].lower(),
                     'p1_type': lambda: j['players'][0]['playerType'].lower(),
                     'p1_id': lambda: j['players'][0]['player']['id'],
                     'p2_name': lambda: j['players'][1]['player']['fullName'].lower(),
                     'p2_type': lambda: j['players'][1]['playerType'].lower(),
                     'p2_id': lambda: j['players'][1]['player']['id']
                     }

        for k, v in attr_dict.items():
            try:
                setattr(self, k, v())
            # except if attribute is not provided in json
            except (IndexError, KeyError):
                pass


class OffensivePuck(Event):

    def __init__(self, attribute_dictionary, json_data, ind, net):
        super().__init__(attribute_dictionary, json_data, ind)
        self._dist_angle(net)
        if self.event == 'shot':
            self.type = json_data[ind]['result']['secondaryType']

    def _dist_angle(self, net_positions):

        if str(self.team)+str(self.period) in net_positions.keys():
            tkey = self.team+str(self.period)
            x_dist = net_positions[tkey] - self.x_coord
            y_dist = self.y_coord

            # set distance and angle of a shot
            self.distance = round(math.hypot(y_dist, x_dist), 5)
            self.angle = round(math.degrees(math.asin(y_dist /
                                                      self.distance)), 5)
        else:
            self.distance = float('nan')
            self.angle = float('nan')


class DefensivePuck(Event):

    def __init__(self, attribute_dictionary, json_data, ind):
        super().__init__(attribute_dictionary, json_data, ind)


class FaceOff(Event):

    def __init__(self, attribute_dictionary, json_data, ind):
        super().__init__(attribute_dictionary, json_data, ind)


class Stoppage(Event):

    def __init__(self, attribute_dictionary, json_data, ind):
        super().__init__(attribute_dictionary, json_data, ind)
        self.event = json_data[ind]['result']['description'].lower()
        self._set_specific(json_data, ind)

    def _set_specific(self, json_data, ind):
        if self.event == "goalie stopped":
            try:
                '''try to pull player data from the stoppage play'''
                p = json_data[ind-1]['players'][1]
                self.p1_name = p['player']['fullName'].lower()
                self.p1_type = p['playerType'].lower()
                self.p1_id = p['player']['id']
            except (KeyError, IndexError):
                pass


class PuckTransfer(Event):

    def __init__(self, attribute_dictionary, json_data, ind):
        super().__init__(attribute_dictionary, json_data, ind)


class Hit(Event):

    def __init__(self, attribute_dictionary, json_data, ind):
        super().__init__(attribute_dictionary, json_data, ind)


class Penalty(Event):

    def __init__(self, attribute_dictionary, json_data, ind):
        super().__init__(attribute_dictionary, json_data, ind)
        self._set_specific(json_data, ind)

    def _set_specific(self, json_data, ind):
        self.type = json_data[ind]['result']['secondaryType'].lower()


class Injury(Event):

    def __init__(self, attribute_dictionary, json_data, ind):
        super().__init__(attribute_dictionary, json_data, ind)


class Challenge(Event):

    def __init__(self, attribute_dictionary, json_data, ind):
        super().__init__(attribute_dictionary, json_data, ind)


class Player(object):

    def __getitem__(cls, x):
        return getattr(cls, x)

    def __init__(self, position, team, plyr_id,
                 plyr_career_json, plyr_game_json):

        self.team = team
        self.position = position
        self.name = plyr_game_json[plyr_id]['person']['fullName']
        self.number = plyr_game_json[plyr_id]['jerseyNumber']
        self.birthday = plyr_career_json[plyr_id]['birthDate']
        self.homecountry = plyr_career_json[plyr_id]['nationality'].lower()
        self.height = re.findall(r'(?=\d*)(\d{1,2})',
                                 plyr_career_json[plyr_id]['height'])
        self.height = round(((int(self.height[0]) * 12) +
                             int(self.height[1])) * 2.54, 2)
        self.weight = round(plyr_career_json[plyr_id]['weight'] * 0.453592, 2)
        self.hand = plyr_game_json[plyr_id]['person']['shootsCatches'].upper()

    def __repr__(self):
        return self.position + ": " + self.name


class Skater(Player):

    def __init__(self, position, team, plyr_id,
                 plyr_career_json, plyr_game_json):
        super().__init__(position, team, plyr_id,
                         plyr_career_json, plyr_game_json)

        json = plyr_game_json[plyr_id]['stats']['skaterStats']

        self.toi = json['timeOnIce']
        self.shots = json['shots']
        self.assists = json['assists']
        self.goals = json['goals']
        self.hits = json['hits']
        self.pp_goals = json['powerPlayGoals']
        self.pp_assists = json['powerPlayAssists']
        self.penalty_min = json['penaltyMinutes']
        self.fo_wins = json['faceOffWins']
        self.fo_taken = json['faceoffTaken']
        self.takeaways = json['takeaways']
        self.giveaways = json['giveaways']
        self.sh_goals = json['shortHandedGoals']
        self.sh_assists = json['shortHandedAssists']
        self.blocked = json['blocked']
        self.e_toi = json['evenTimeOnIce']
        self.pp_toi = json['powerPlayTimeOnIce']
        self.sh_toi = json['shortHandedTimeOnIce']
        self.id = plyr_id


class Goalie(Player):

    def __init__(self, position, team, plyr_id,
                 plyr_career_json, plyr_game_json):
        super().__init__(position, team, plyr_id,
                         plyr_career_json, plyr_game_json)

        gl = plyr_game_json[plyr_id]['stats']['goalieStats']

        self.toi = gl['timeOnIce']
        self.shots = gl['shots']
        self.saves = gl['saves']
        self.pp_saves = gl['powerPlaySaves']
        self.sh_saves = gl['shortHandedSaves']
        self.e_saves = gl['evenSaves']
        self.sh_shots = gl['shortHandedShotsAgainst']
        self.e_shots = gl['evenShotsAgainst']
        self.pp_shots = gl['powerPlayShotsAgainst']
        self.id = plyr_id


gn = "0009"
gt = "02"
gy = "2017"

G = Game(game_no=gn, game_type=gt,
         season_year=gy)
