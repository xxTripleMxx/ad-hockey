import re

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