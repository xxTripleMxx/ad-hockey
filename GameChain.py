import pandas as pd
from Game import Game
import configure

gt = "02"
gy = "2017"
# Game 18, 34, 196, 199, 209, 262, 309, 318, 394, 410, 458, 481, 516, 540, 639, 674,
# Game 781, 792, 811, 856, 935, 941, 953, 1001, 1043, 1080, 1101, 1126, 1143
# contain no play by play data
### Throws tricode error which is first attempt at 
for gn in range(1100,1101):
    o = "0"*(4-len(str(gn)))
    gn = o + str(gn)
    try:
        G = Game(game_no=gn, game_type=gt,
                 season_year=gy)
        
    except KeyError:
        print('Unable to process game')
        
    conn = configure.connect_db('hockeydata')
    configure.create_table(G, conn)
    conn.close()