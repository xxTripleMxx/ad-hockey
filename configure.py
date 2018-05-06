import sqlite3 as sql

def connect_db(name):
    
    conn = sql.connect(name + '.db')
    
    return conn

def create_table(curs):
    
    events_tbl = ['CREATE TABLE IF NOT EXISTS events(', 
        'event TEXT, game_id TEXT, period NUMERIC, time REAL, x_coord REAL, y_coord REAL, ',
        'team TEXT, p1_type TEXT, p1_id NUMERIC, p2_type TEXT, p2_id NUMERIC, ',
        'poi NUMERIC, distance REAL, angle NUMERIC, type TEXT, event_id REAL,',
        'CONSTRAINT unique_event UNIQUE (game_id, event_id))']
    
    curs.execute("".join(events_tbl))

def update_table(game_object, table, conn):
    
    c = conn.cursor()
    insert_synt = "INSERT INTO " + table + " VALUES ("
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
            
            emap = map(lambda x: str(x), [event, game_id, period, time, x_coord, 
                       y_coord, team, p1_type, p1_id, p2_type, p2_id, poi, 
                       distance, angle, typee, event_id])
            elist = ["'" + x + "'" for x in emap]
            sql_command = insert_synt + ", ".join(elist) + ")"
            c.execute(sql_command)
            print("Added line to TABLE " + table + ": \n", sql_command)
            print("")
            
            conn.commit()