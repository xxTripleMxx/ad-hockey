import re
import datetime as dt


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
        self.homecountry = plyr_career_json[plyr_id]['nationality'].upper()
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
        
        toi = json['timeOnIce'].split(':')
        toi = dt.timedelta(minutes=int(toi[0]), seconds=int(toi[1]))
        self.toi = toi.total_seconds()
        self.shots = json['shots']
        self.assists = json['assists']
        self.goals = json['goals']
        self.hits = json['hits']
        self.pp_goals = json['powerPlayGoals']
        self.pp_assists = json['powerPlayAssists']
        pm = dt.timedelta(minutes=int(json['penaltyMinutes']))
        self.penalty_time = pm.total_seconds()
        self.fo_wins = json['faceOffWins']
        self.fo_taken = json['faceoffTaken']
        self.takeaways = json['takeaways']
        self.giveaways = json['giveaways']
        self.sh_goals = json['shortHandedGoals']
        self.sh_assists = json['shortHandedAssists']
        self.blocked = json['blocked']
        e = json['evenTimeOnIce'].split(':')
        e = dt.timedelta(minutes=int(e[0]), seconds=int(e[1]))
        self.e_toi = e.total_seconds()
        pp = json['powerPlayTimeOnIce'].split(':')
        pp = dt.timedelta(minutes=int(pp[0]), seconds=int(pp[1]))
        self.pp_toi = pp.total_seconds()
        sh = json['shortHandedTimeOnIce'].split(':')
        sh = dt.timedelta(minutes=int(sh[0]), seconds=int(sh[1]))
        self.sh_toi = sh.total_seconds()
        self.id = int(plyr_id.replace("ID", ""))


class Goalie(Player):

    def __init__(self, position, team, plyr_id,
                 plyr_career_json, plyr_game_json):
        super().__init__(position, team, plyr_id,
                         plyr_career_json, plyr_game_json)

        gl = plyr_game_json[plyr_id]['stats']['goalieStats']
        toi = gl['timeOnIce'].split(':')
        toi = dt.timedelta(minutes=int(toi[0]), seconds=int(toi[1]))
        self.toi = toi.total_seconds()
        self.shots = gl['shots']
        self.saves = gl['saves']
        self.pp_saves = gl['powerPlaySaves']
        self.sh_saves = gl['shortHandedSaves']
        self.e_saves = gl['evenSaves']
        self.sh_shots = gl['shortHandedShotsAgainst']
        self.e_shots = gl['evenShotsAgainst']
        self.pp_shots = gl['powerPlayShotsAgainst']
        self.id = int(plyr_id.replace("ID", ""))