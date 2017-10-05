# -*- coding: utf-8 -*-
import sqlite3
import os
from os import getlogin 
from os_tools import HUD_NAME

SUPPORT_DIR = '/Users/' + getlogin() + \
        '/Library/Application Support/' + HUD_NAME + '/'

if not os.path.isdir(SUPPORT_DIR):
    os.mkdir(SUPPORT_DIR)

hu_conn = sqlite3.connect(SUPPORT_DIR + 'hu_players.db') 
six_conn = sqlite3.connect(SUPPORT_DIR + 'six_m_players.db') 
nine_conn = sqlite3.connect(SUPPORT_DIR + 'nine_m_players.db')
hu_sng_conn = sqlite3.connect(SUPPORT_DIR + 'hu_sng_players.db')
six_sng_conn = sqlite3.connect(SUPPORT_DIR + 'six_sng_players.db')
nine_sng_conn = sqlite3.connect(SUPPORT_DIR + 'nine_sng_players.db')
table_conn = sqlite3.connect(SUPPORT_DIR + 'tables.db') 

for x in [hu_conn, six_conn, nine_conn, table_conn,
        hu_sng_conn, six_sng_conn, nine_sng_conn]:
    x.text_factory = str

COLORS = {"name": "ffffff", "hands": "d0ffd0", "Hands": "d0ffd0",
        "vpip": "709fd0", "pfr": "f04455", 
        "3bet": "ff7bb4", "4bet": "ff5bab", "stl": "818818", 
        "3btf": "ff7bb4", "4btf": "ff5bab", "fts": "818818", 
        "cbet": "ffed11", " cbturn": "ffed11", " cbrivr": "ffed11", 
        "cbtf": "eead11", "fcbturn": "eead11", "fcbrivr": "eead11",
        "VPIP": "709fd0", "PFR": "f04455", 
        "TURN": "ffed11", "RIVR": "ffed11", 
        "3BET": "ff7bb4", "4BET": "ff5bab", "STL": "818818", "STEAL": "818818",
        "3BTF": "ff7bb4", "4BTF": "ff5bab", "FTS": "818818", 
        "CBET": "ffed11", " CBTURN": "ffed11", " CBRIVR": "ffed11", 
        "CBTF": "eead11", "FCBTURN": "eead11", "FCBRIVR": "eead11"}

def init_player_DB(conn, table_name):
    '''
    Args:
        conn (sql db connection): a connection to an sqlite3 database.
        table_name (str): name of table.
    Sides:
        Initialize player database if none exists.
    '''
    conn.execute('''CREATE TABLE IF NOT EXISTS ''' + table_name + '''
                    (UID TEXT PRIMARY KEY NOT NULL,
                    HANDS INT NOT NULL,
                    THREE_BET INT NOT NULL,
                    FOUR_BET INT NOT NULL,
                    C_BET INT NOT NULL,
                    THREE_BET_F INT NOT NULL,
                    FOUR_BET_F INT NOT NULL,
                    C_BET_F INT NOT NULL,
                    VPIP_FREQ INT NOT NULL,
                    PFR_FREQ INT NOT NULL,
                    STEAL_FREQ INT NOT NULL,
                    STEAL_F_FREQ INT NOT NULL,
                    O_THREE_BET INT NOT NULL,
                    O_FOUR_BET INT NOT NULL,
                    O_C_BET INT NOT NULL,
                    O_THREE_BET_F INT NOT NULL,
                    O_FOUR_BET_F INT NOT NULL,
                    O_C_BET_F INT NOT NULL,
                    O_VPIP_FREQ INT NOT NULL,
                    O_PFR_FREQ INT NOT NULL,
                    O_STEAL_FREQ INT NOT NULL,
                    O_STEAL_F_FREQ INT NOT NULL,
                    TURN_CBET INT NOT NULL,
                    RIVER_CBET INT NOT NULL,
                    TURN_CBET_F INT NOT NULL,
                    RIVER_CBET_F INT NOT NULL,
                    O_TURN_CBET INT NOT NULL,
                    O_RIVER_CBET INT NOT NULL,
                    O_TURN_CBET_F INT NOT NULL,
                    O_RIVER_CBET_F INT NOT NULL);''')
    conn.commit()

def init_table_db(conn, table_name):
    '''
    Args:
        conn (sql db connection): a connection to an sqlite3 database.
        table_name (str): name of table.
    Sides:
        Initialize table database if none exists.
    '''
    conn.execute('''CREATE TABLE IF NOT EXISTS ''' + table_name + 
            '''(TID TEXT PRIMARY KEY NOT NULL, 
              SEATS INT NOT NULL, 
              S1 TEXT, 
              S2 TEXT, 
              S3 TEXT, 
              S4 TEXT, 
              S5 TEXT, 
              S6 TEXT, 
              S7 TEXT, 
              S8 TEXT, 
              S9 TEXT, 
              S0 TEXT);''')
    conn.commit()

def add_player_hand_to_DB(data, conn, table_name):
    '''
    Args:
        data (list): tuple of player data to be added to db specified by
            table_name.
        conn: open database connection
        table_name (str): name of database to add tuple to.
    Sides:
        Adds player hand to a database.
    '''
    template = ["UID", "HANDS", "THREE_BET", "FOUR_BET", "C_BET",
            "THREE_BET_F", "FOUR_BET_F", "C_BET_F", 
            "VPIP_FREQ", "PFR_FREQ", "STEAL_FREQ", "STEAL_F_FREQ",
            "O_THREE_BET", "O_FOUR_BET", "O_C_BET",
            "O_THREE_BET_F", "O_FOUR_BET_F", "O_C_BET_F", 
            "O_VPIP_FREQ", "O_PFR_FREQ", "O_STEAL_FREQ", "O_STEAL_F_FREQ",
            "TURN_CBET", "RIVER_CBET", "TURN_CBET_F", "RIVER_CBET_F",
            "O_TURN_CBET", "O_RIVER_CBET", "O_TURN_CBET_F", "O_RIVER_CBET_F"]

    if check_player_data(data[0], conn, table_name):
        updated_data = get_player_data(data[0], conn, table_name)
        for i in range(1, len(data)):
            updated_data[i] += data[i]

        action = ""
        for i in range(1, len(data)):
            action += template[i] + "=" + str(updated_data[i]) + ", "
        action = action[:-2] + " "
        action = "UPDATE " + table_name + " SET " + action + "WHERE UID=?;"
        conn.execute(action, [str(data[0])])
    
    else:
        action = "INSERT INTO " + table_name + " (" + ",".join(template) + \
            ") VALUES (?"
        for i in range(1, len(template)):
            action += ", " + str(data[i])
        action += ");" 
        conn.execute(action, [str(data[0])])

    conn.commit()

def add_table_to_DB(table_data, conn, table_name):
    '''
    Args:
        table_data (list): tuple of table data to be added to tables.db
        conn: open database connection
        table_name (str): name of database table to add tuple to. in this case
            it will always be TABLES, but for sake of modularity want this
            to be flexible.
    Sides:
        Adds table data to a database.
    '''
    template = ["TID", "SEATS", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", \
            "S9", "S0"]
    query = "SELECT TID FROM " + table_name + " WHERE TID=?;"
    cursor = conn.execute(query, [table_data[0]])
    indicator = 0
    
    for row in cursor:
        if row[0] == table_data[0]:
            indicator = 1
    if not indicator:
        # add table_data to db
        query = "INSERT INTO " + table_name + " values " + \
                "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
        cursor = conn.execute(query, table_data)
    else:
        # update the entry that's already in the database.
        query = "UPDATE " + table_name + " SET " + \
                ", ".join(map(lambda x: template[x] + "=\"" + \
                str(table_data[x]) + "\"", \
                range(len(template)))) + " WHERE TID=?;" 
        conn.execute(query, [table_data[0]])
    conn.commit()
                
def check_player_data(player, conn, table_name):
    '''
    Args:
        player (str): name of a player 
        conn: open database connection
        table_name (str): name of database table to search for pre-existing 
            player data
    Returns:
        (bool): true if we found pre-existing player data in the db.
    '''
    cursor = conn.execute("SELECT UID FROM " + table_name + " WHERE UID= ? ;", [player])
    for row in cursor:
        return True
    return False

def get_player_data(player, conn, table_name):
    '''
    Args:
        player (str): name of a player 
        conn: open database connection
        table_name (str): name of database table to search for player data
    Returns:
        output (list): the row of the database describing the player's stats
    '''
    if player == None:
        return []
    cursor = conn.execute("SELECT * FROM " + table_name + \
            " WHERE UID=?;", [player])
    output = []
    for row in cursor:
        for i in range(0, 30):
            output.append(row[i])
    return output

def get_user_label(player, conn, table_name, a, p, c, ct):
    '''
    Args:
        player (str): player uid, in this case it's always USER
        conn: a database connection
        table_name: name of the table we're getting the stats for
        a (bool): auto bool (see main for more on a, p, c, ct)
        p (bool): pro bool
        c (bool): custom bool
        ct (str): custom config string
    Returns:
        (str): formatted and detailed stats for the user. stats dependent on
            user settings as described by a, p, c, and ct.
    The user label should be the most detailed since it's the most important
    and from a UX perspective, it should act as a key/legend for the other
    players' abbreviated labels.
    '''
    # sl = statline, fs = format string
    sl = compute_player_stats(player, conn, table_name)
    if sl != ' ':
        if p == True:
            header = "{0} (Hands: {1})\n"
            fs =  "VPIP {8} PFR {9} STEAL {10} FTS {11}\n"
            fs += "3BET {2} 4BET {3} CBET {4} TURN {12} RIVR {13}\n" 
            fs += "[color=" + COLORS["3btf"] + "]FOLD[/color] {5} "
            fs += "[color=" + COLORS["4btf"] + "]FOLD[/color] {6} "
            fs += "[color=" + COLORS["cbtf"] + "]FOLD[/color] {7} "
            fs += "[color=" + COLORS["cbtf"] + "]FOLD[/color] {14} "
            fs += "[color=" + COLORS["cbtf"] + "]FOLD[/color] {15} "
            print('--------------')
            print(header)
            print(fs)
            print('--------------')
            return colorize_numbers(header + fs).format(*sl)

def get_player_label(player, conn, table_name, h, p, c, ct):
    '''
    Args:
        player (str): player uid.
        conn: a database connection
        table_name: name of the table we're getting the stats for
        h (int): number of hands played, make this -1 if auto isn't checked.
        p (bool): pro bool
        c (bool): custom bool
        ct (str): custom config string
    Returns:
        (str): formatted, abbreviated stats for another player at the
            table. format conditional on user's settings as described
            by a, p, c, and ct.
    '''
    output = compute_player_stats(player, conn, table_name)
    if output != ' ':
        if  p == True:
            # UID + Hands
            # VPIP PFR STL STLF
            # 3BET 4BET CB CBT CBR
            # 3BET 4BET CB CBT CBR (fold)
            return colorize_numbers("{0} ({1})\n{8}/{9}/{10}/{11}\n{2}/{3}/{4}/{12}/{13}\n" + \
                    "{5}/{6}/{7}/{14}/{15}").format(*output)
        elif h >= 0:
            if h < 50:
                return colorize_numbers("{0}\n(hands: {1})\nVPIP: {8}").format(*output)
            elif h in range(50, 100):
                return colorize_numbers("{0} ({1})\n{8} / PFR: {9}").format(*output)
            elif h in range(100, 150):
                return colorize_numbers("{0} ({1})\n{8}/{9}\n3BET: {2}\n" + \
                        "3BTF: {5}").format(*output)
            elif h in range(150, 200):
                return colorize_numbers("{0} ({1})\n{8}/{9}\n{2}/4BET: {3}\n" + \
                        "{5}/4BTF: {6}").format(*output)
            elif h in range(200, 250):
                return colorize_numbers("{0} ({1})\n{8}/{9}\n{2}/{3}/CBET: {4} TURN: {12} RIVR: {13}\n" + \
                        "{5}/{6}/FOLD: {7} FOLD: {14} FOLD: {15}").format(*output)
            elif h in range(250, 300):
                return colorize_numbers("{0} ({1})\n{8}/{9}STL: {10} FTS: {11}\n{2}/{3}/{4}/{12}/{13}\n" + \
                        "{5}/{6}/{7}/{14}/{15}").format(*output)
            else:
                return colorize_numbers("{0} ({1})\n{8}/{9}/{10}/{11}\n{2}/{3}/{4}/{12}/{13}\n" + \
                        "{5}/{6}/{7}/{14}/{15}").format(*output)
        elif c == True:
            custom_dictionary = {"name": output[0], "hands": output[1], 
                    "3bet": output[2], "4bet": output[3], "cbet": output[4], 
                    "3btf": output[5], "4btf": output[6], "cbtf": output[7], 
                    "vpip": output[8], "pfr": output[9], "stl": output[10],
                    "fts": output[11], "cbturn": output[12], 
                    "cbriver": output[13], "fcbturn": output[14], 
                    "fcbriver": output[15]}
            ct = colorize(ct)
            for key in custom_dictionary.keys():
                ct = ct.replace(key, "{" + key + "}")
            return ct.format(**custom_dictionary)
    else:
        return ' '

def colorize_numbers(s):
    # Color in the numerical values of the stats.
    color_map = {"{0}": "[color=" + COLORS["name"] + "]{0}[/color]",
            "{1}": "[color=" + COLORS["hands"] + "]{1}[/color]",
            "{2}": "[color=" + COLORS["3bet"] + "]{2}[/color]",
            "{3}": "[color=" + COLORS["4bet"] + "]{3}[/color]",
            "{4}": "[color=" + COLORS["cbet"] + "]{4}[/color]",
            "{5}": "[color=" + COLORS["3btf"] + "]{5}[/color]",
            "{6}": "[color=" + COLORS["4btf"] + "]{6}[/color]",
            "{7}": "[color=" + COLORS["cbtf"] + "]{7}[/color]",
            "{8}": "[color=" + COLORS["vpip"] + "]{8}[/color]",
            "{9}": "[color=" + COLORS["pfr"] + "]{9}[/color]",
            "{10}": "[color=" + COLORS["stl"] + "]{10}[/color]",
            "{11}": "[color=" + COLORS["fts"] + "]{11}[/color]",
            "{12}": "[color=" + COLORS[" cbturn"] + "]{12}[/color]",
            "{13}": "[color=" + COLORS[" cbrivr"] + "]{13}[/color]",
            "{14}": "[color=" + COLORS["fcbturn"] + "]{14}[/color]",
            "{15}": "[color=" + COLORS["fcbrivr"] + "]{15}[/color]"}
    for key in color_map:
        s = s.replace(key, color_map[key])
    return colorize(s)
        
def colorize(s):
    # Color stat titles (e.g. VPIP, PFR, etc.)
    for key in COLORS.keys():
        s = s.replace(key, "[color=" + COLORS[key] + "]" + key + "[/color]")
    return s

def compute_player_stats(player, conn, table_name):
    '''
    Args:
        player (str): player uid
        conn: a database connection
        table_name: name of the table we're getting data from.
    Returns:
        (list): computed player stats as strings in a list.
    This function computes each statistic and then formats it as a
    2 digit string. The list of these formatted stats is then shipped
    to other functions that organize the stats into nice labels for the
    frontend.
    '''
    # presumably the correct indices for all these stats:
    # TODO: check everything after stlf 
    # 3bet 4bet cbet 3bf 4bf cbf vpip pfr stl stlf cbt cbr cbft cbfr
    #  2    3    4    5   6   7   8    9   10  11   12  13  14   15
    player_data = get_player_data(player, conn, table_name)
    if player_data == []:
        return ' '
   
    # This handles the original stats
    output = []
    for i in range(2, 12):
        if player_data[i + 10] != 0:
            if player_data[i] == player_data[i + 10]:
                output.append('99')
            else:
                output.append(int(100 * player_data[i] / float(player_data[i + 10])))
        else:
            output.append(0)
    # Handle expanded c-bet stats here
    for i in range(22,26):
        if player_data[i + 4] != 0:
            if player_data[i] == player_data[i + 4]:
                output.append('99')
            else:
                output.append(int(100 * player_data[i] / float(player_data[i + 4])))
        else:
            output.append(0)

    # concatenate stats to two digits
    for x in range(len(output)):
        # check if number is 100
        # also do something about this nastiness 
        if len(str(int(round(x)))) == 3:
            output[x] = '99'

    output = map(lambda x: str(x)[0:2], output)

    # zero pad single digit stats
    for i in range(len(output)):
        if len(output[i]) == 1:
            output[i] = "0" + output[i]

    # UID, hands + 
    return map(lambda x: str(x), player_data[0:2]) + output

def get_table_data(tid, conn, table_name):
    '''
    Args:
        tid (str): the table id, which is just the table name as captured by
            a regex expression from the window name. (see main.py)
        conn: a database connection.
        table_name: name of database table to search for table data. in this
            case it's always TABLES.
    Returns:
       (list): row of data corresponding to the given table. 
    '''
    cursor = conn.execute("SELECT * FROM " + table_name +\
            " WHERE TID=?;", [tid])
    for row in cursor:
        return map(lambda x: row[x], range(12))
