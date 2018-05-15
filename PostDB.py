import sqlite3 as sql
import pandas as pd
import numpy as np

conn = sql.connect('hockeydata.db')

def team_game_differences(conn):
    tg_df = pd.read_sql_query('SELECT * FROM team_games', conn)
    tg_df = tg_df.set_index(['game_id', 'abbr', 'loc'])
    
    away_tg_diff = tg_df.groupby(level=0).diff()
    home_tg_diff = tg_df.groupby(level=0).diff(periods=-1)
    
    send_df = away_tg_diff.fillna(home_tg_diff)
    
    return send_df

tg_diff = team_game_differences(conn)
tg_diff.to_sql('team_games_diff', conn, if_exists='replace')