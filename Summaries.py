from datetime import datetime as dt

class Summary(object):

    def __init__(self, json_data):

        time = json_data['gameData']['datetime']
        self.start_time = dt.strptime(time['dateTime'], '%Y-%m-%dT%H:%M:%SZ').strftime("%H:%M:%S")
        self.end_time = dt.strptime(time['endDateTime'], '%Y-%m-%dT%H:%M:%SZ').strftime("%H:%M:%S")
        self.date = dt.strptime(time['endDateTime'], '%Y-%m-%dT%H:%M:%SZ').strftime("%Y-%m-%d")
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
