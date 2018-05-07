import sqlite3 as sql

def connect_db(name):
    
    conn = sql.connect(name + '.db')
    
    return conn

def create_table(curs):
    
    events_tbl = ['CREATE TABLE IF NOT EXISTS events(', 
        'event TEXT, game_id TEXT, period NUMERIC, time REAL, x_coord REAL, y_coord REAL, ',
        'team TEXT, p1_type TEXT, p1_id NUMERIC, p2_type TEXT, p2_id NUMERIC, ',
        'poi NUMERIC, distance REAL, angle NUMERIC, type TEXT, event_id NUMERIC,',
        'length_seconds NUMERIC, end_time NUMERIC,',
        'CONSTRAINT unique_event UNIQUE (game_id, event_id))']
    
    # player id as primary key
    players_tbl = ['CREATE TABLE IF NOT EXISTS players(',
                   'name TEXT, position TEXT, team TEXT, number NUMERIC, ',
                   'birthday TEXT, homecountry TEXT, height NUMERIC, ',
                   'weight REAL, hand TEXT)']
    
    # create one to many with position player id to player table
    player_position_tbl = ['CREATE TABLE IF NOT EXISTS positions(',
                           'abbrev TEXT, position TEXT, player_id TEXT)']
    
    # set foreign key with player id and game id
    skater_game_summary_tbl = ['CREATE TABLE IF NOT EXISTS skater_summary(',
                               'player_id NUMERIC, toi NUMERIC, shots NUMERIC,',
                               'assists NUMERIC, goals NUMERIC, hits NUMERIC,',
                               'pp_goals NUMERIC, pp_assists NUMERIC,',
                               'penalty_time NUMERIC fo_wins NUMERIC,',
                               'fo_taken NUMERIC, takeaways NUMERIC giveaways NUMERIC,',
                               'sh_goals NUMERIC, sh_assists NUMERIC, blocked NUMERIC,',
                               'e_toi NUMERIC, pp_toi NUMERIC, sh_toi NUMERIC,',
                               'game_id NUMERIC)']
    
    # set foreign key with player id and game id
    goalie_game_summary_tbl = ['CREATE TABLE IF NOT EXISTS goalie_summary(',
                               'player_id NUMERIC, toi NUMERIC, shots NUMERIC, ',
                               'saves NUMERIC, pp_saves NUMERIC, sh_saves NUMERIC,',
                               'e_saves NUMERIC, sh_shots NUMERIC, e_shots NUMERIC,',
                               'pp_shots NUMERIC)']
    
    tbls_list = [events_tbl, players_tbl, player_position_tbl, 
                 skater_game_summary_tbl, goalie_game_summary_tbl]
    for tbl in tbls_list:
        curs.execute("".join(tbl))

def update_table(game_object, table, conn):
    
    c = conn.cursor()

    if table == 'events':
        container = game_object.events
        e = container.to_dict()
        for n in range(0, len(container())):
            "need to maintain order for feeding into sql syntax ... grumble grumble"
            event = e['event'][n]
            game_id = game_object.game_id
            period = e['period'][n]
            time = e['time'][n]
            x_coord = e['x_coord'][n]
            y_coord = e['y_coord'][n]
            team = e['team'][n]
            p1_type = e['p1_type'][n]
            p1_id = e['p1_id'][n]
            p2_type = e['p2_type'][n]
            p2_id = e['p2_id'][n]
            poi = e['poi'][n]
            distance = e['distance'][n]
            angle = e['angle'][n]
            typee = e['type'][n]
            event_id = e['event_id'][n]
            length_seconds = e['length_seconds'][n]
            end_time = e['end_time'][n]
            
            emap = map(lambda x: str(x), [event, game_id, period, time, x_coord, 
                       y_coord, team, p1_type, p1_id, p2_type, p2_id, poi, 
                       distance, angle, typee, event_id, length_seconds, end_time])
            elist = ["'" + x + "'" for x in emap]
            
            try:
                insert_start = "INSERT INTO " + table + " VALUES ("
                sql_command = insert_start + ", ".join(elist) + ")"
                c.execute(sql_command)

            except:
                updates = [k + " = " + "'" + str(v[n]) + "'" for k,v in e.items() if "name" not in k]
                update_start = "UPDATE " + table + " "
                update_set = 'SET ' + ", ".join(updates) + " "
                update_where = "WHERE game_id = " + "'" + str(game_id) + "'" + " AND event_id = " + "'" + str(event_id) + "'"
                sql_command = update_start + update_set + update_where
                print(sql_command)
                c.execute(sql_command)
                
            
            print("Added line to TABLE " + table + ": \n", sql_command)
            print("")
            
            conn.commit()
        
    elif table == 'players':
        container = game_object.players
        p = container.to_dict()
        for n in range(0, len(container())):
            team
            

