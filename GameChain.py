from Game import Game

gn = "0009"
gt = "02"
gy = "2017"

G = Game(game_no=gn, game_type=gt,
         season_year=gy)

G.players.to_dict()