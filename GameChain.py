from Game import Game

gn = "0022"
gt = "02"
gy = "2017"

G = Game(game_no=gn, game_type=gt,
         season_year=gy)

# Keep working on timedelta for penalties
G.events.to_dict(attributes='event', filts='penalty')['time']


