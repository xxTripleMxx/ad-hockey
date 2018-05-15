import sqlite3 as sql
import Functionality as f

def connect_db(name):
    
    conn = sql.connect(name + '.db')
    
    return conn

def create_table(game_object, conn):

    curs = conn.cursor()
    game_id = game_object.game_id
    
    def ordered_fields(field_str):
        
        fields = [x for x in str(field_str).split(",")]
        fields = list(map(lambda x: x.replace('\n',"").strip().split(" ")[0], fields))
        fields = list(filter(lambda x: len(x) > 1, fields))
        return fields
    
    def populate(tbl_name, sql_tuple, curs, conn, con_dict):

        for n in range(0, len(container())):
            sql_insert = ['"' + str(con_dict[field][n]) + '"' for field in sql_tuple[1]]
            sql_update = [field + ' = "' + str(con_dict[field][n]) + '"' for field in sql_tuple[1]]
            try:
                insert_start = "INSERT INTO " + tbl_name + " VALUES ("
                sql_command = insert_start + ", ".join(sql_insert) + ")"
                curs.execute(sql_command)
                conn.commit()
                
                print(sql_command)

            except sql.IntegrityError as e:
                print(e)
                update_start = "UPDATE " + tbl_name + " "
                update_set = 'SET ' + ", ".join(sql_update) + " "
                update_where = "WHERE (" + " AND ".join(sql_update) + ")"
                sql_command = update_start + update_set + update_where
                curs.execute(sql_command)
                conn.commit()
                
                print(sql_command)

    # create game table and set primary key as game_id
    etbl_create = 'CREATE TABLE IF NOT EXISTS events('
    etbl_fields = '''event TEXT NOT NULL, game_id TEXT NOT NULL, period NUMERIC NOT NULL, 
                    time REAL NOT NULL, x_coord REAL, y_coord REAL, 
                    team TEXT, p1_type TEXT, p1_id NUMERIC, p2_type TEXT, p2_id NUMERIC, 
                    poi NUMERIC, distance REAL, angle NUMERIC, type TEXT, event_id NUMERIC NOT NULL, 
                    length_seconds NUMERIC, end_time NUMERIC, '''
    etbl_foreign = 'FOREIGN KEY(p1_id, p2_id) REFERENCES players(id, id), '
    etbl_constraint = 'CONSTRAINT unique_event UNIQUE (event_id))'
    
    etbl = etbl_create + etbl_fields + etbl_constraint
    etbl_fields = ordered_fields(etbl_fields)
    
    # player id as primary key
    ptbl_create = 'CREATE TABLE IF NOT EXISTS players('
    ptbl_fields = '''name TEXT, team TEXT, number NUMERIC, birthday TEXT, 
                     homecountry TEXT, height NUMERIC, weight REAL, hand TEXT, 
                     id NUMERIC UNIQUE, '''
    ptbl_primary = 'PRIMARY KEY (id))'
    
    ptbl = ptbl_create + ptbl_fields + ptbl_primary
    ptbl_fields = ordered_fields(ptbl_fields)

    # set foreign key with player id and game id
    sktr_create = 'CREATE TABLE IF NOT EXISTS skater_summary('
    sktr_fields = '''id NUMERIC NOT NULL UNIQUE, toi NUMERIC, shots NUMERIC,
                   assists NUMERIC, goals NUMERIC, hits NUMERIC,
                   pp_goals NUMERIC, pp_assists NUMERIC,
                   penalty_time NUMERIC, fo_wins NUMERIC,
                   fo_taken NUMERIC, takeaways NUMERIC, giveaways NUMERIC,
                   sh_goals NUMERIC, sh_assists NUMERIC, blocked NUMERIC, 
                   e_toi NUMERIC, pp_toi NUMERIC, sh_toi NUMERIC, 
                   game_id NUMERIC, position TEXT, '''
    sktr_foreign = 'FOREIGN KEY (id) REFERENCES players(id), '
    sktr_constraint = 'CONSTRAINT unique_skater UNIQUE (id, game_id))'
    
    sktr = sktr_create + sktr_fields + sktr_constraint
    sktr_fields = ordered_fields(sktr_fields)
    
    # set foreign key with player id and game id
    gl_create = 'CREATE TABLE IF NOT EXISTS goalie_summary('
    gl_fields = '''id NUMERIC NOT NULL UNIQUE, toi NUMERIC, shots NUMERIC, 
                   saves NUMERIC, pp_saves NUMERIC, sh_saves NUMERIC, 
                   e_saves NUMERIC, sh_shots NUMERIC, e_shots NUMERIC,
                   pp_shots NUMERIC, game_id NUMERIC, position TEXT, '''
    gl_foreign = 'FOREIGN KEY (id) REFERENCES players(id), '
    gl_constraint = 'CONSTRAINT unique_goalie UNIQUE (id, game_id))'
    
    gl = gl_create + gl_fields + gl_constraint
    gl_fields = ordered_fields(gl_fields)
    
    # game table
    game_create = 'CREATE TABLE IF NOT EXISTS games('
    game_fields = '''game_id NUMERIC NOT NULL UNIQUE, date TEXT NOT NULL, 
                     start_time TEXT NOT NULL, end_time TEXT NOT NULL, 
                     venue TEXT NOT NULL, '''
    game_primary = 'PRIMARY KEY (game_id), '
    game_constraint = 'CONSTRAINT unique_gameid UNIQUE (game_id))'
    
    game = game_create + game_fields + game_primary + game_constraint
    game_fields = ordered_fields(game_fields)
    
    # team game summary table
    team_game_create = "CREATE TABLE IF NOT EXISTS team_games("
    team_game_fields = '''game_id NUMERIC NOT NULL, abbr TEXT NOT NULL,
                          goals NUMERIC, pim NUMERIC, shots NUMERIC, 
                          powerPlayPercentage REAL, powerPlayGoals NUMERIC,
                          faceOffWinPercentage REAL, blocked NUMERIC, takeaways NUMERIC,
                          giveaways NUMERIC, hits NUMERIC, loc TEXT, '''
    team_game_foreign = 'FOREIGN KEY (game_id) REFERENCES games(game_id), '
    team_game_constraint = 'CONSTRAINT unique_game_team UNIQUE (abbr, game_id))'
    
    team_game = team_game_create + team_game_fields + team_game_constraint
    team_game_fields = ordered_fields(team_game_fields)
    
    # table groups
    tbls_dict = {'events': (etbl, etbl_fields), 
                 'players':
                 {'players':(ptbl, ptbl_fields),
                  'goalie_summary': (gl, gl_fields), 
                  'skater_summary': (sktr, sktr_fields)
                 },
                 'games':{'games':(game, game_fields), 
                         'team_games':(team_game, team_game_fields)
                        }
                }

    for k,v in tbls_dict.items():
        
        if k == 'events':
            container = game_object.events
            curs.execute(v[0])
            con_dict = container.to_dict()
            con_dict['game_id'] = [game_id] * len(container())
            populate(k, v, curs, conn, con_dict)
            
        elif k == 'players':
            
            for tbl, vals in v.items():
                curs.execute(vals[0])
                if tbl == 'players':
                    container = game_object.players
                    con_dict = container.to_dict()
                    con_dict['game_id'] = [game_id] * len(container())
                    populate(tbl, vals, curs, conn, con_dict)
                    
                elif tbl == 'goalie_summary':
                    container = game_object.players
                    goalie_filt = container.to_dict(attributes='position', filts='G')['id']
                    container = f.Container([obj for obj in container() if obj.id in goalie_filt])
                    con_dict = container.to_dict()
                    con_dict['game_id'] = [game_id] * len(container())
                    populate(tbl, vals, curs, conn, con_dict)
                    
                elif tbl == 'skater_summary':
                    container = game_object.players
                    goalie_filt = container.to_dict(attributes='position', filts='G')['id']
                    container = f.Container([obj for obj in container() if obj.id not in goalie_filt])
                    con_dict = container.to_dict()
                    con_dict['game_id'] = [game_id] * len(container())
                    populate(tbl, vals, curs, conn, con_dict)
                    
        elif k == 'games':
                
            for tbl, vals in v.items():
                curs.execute(vals[0])
                if tbl == 'games':
                    game_id = game_object.game_id
                    smry = game_object.summary
                    start_time = smry.start_time
                    date = smry.date
                    end_time = smry.end_time
                    venue = smry.venue
                    
                    l1 = [game_id, date, start_time, end_time, venue]
                    con_dict = {k:[v] for k,v in dict(zip(game_fields,l1)).items()}
                    container = f.Container('a') # this is hacky and wrong
                    populate(tbl, vals, curs, conn, con_dict)
                    
                elif tbl == 'team_games':
                    game_id = game_object.game_id
                    tm = game_object.summary.team_metrics
                    con_dict = {k:[] for x in tm for k in x.__dict__.keys()}
                    for team in tm:
                        for k,v in team.__dict__.items():
                            con_dict[k].append(v)

                    con_dict['game_id'] = [game_id]*2
                    container = f.Container([1,2]) # this is hacky and wrong
                    populate(tbl, vals, curs, conn, con_dict)