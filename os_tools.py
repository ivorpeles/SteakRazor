from Quartz import kCGWindowListOptionOnScreenOnly, kCGNullWindowID, CGWindowListCopyWindowInfo
from AppKit import NSScreen
import os, re

HUD_NAME = 'Steak Razor'
HH_BACKUP_PATH = '/Users/' + os.getlogin() + '/Library/Application Support/' + \
        HUD_NAME + '/' + 'BACKUP'
# DEBUG: for debug purposes, TextEdit is in the client list.
POKER_CLIENTS = ['PokerStars', 'TextEdit']

def load_hh_path():
    support_dir = '/Users/' + os.getlogin() + \
            '/Library/Application Support/' + HUD_NAME + '/'
    if not os.path.isdir(support_dir):
        os.mkdir(support_dir)
    if os.path.exists(support_dir + 'hh_path'):
        with open(support_dir + 'hh_path', 'r') as hh_path:
            return hh_path.readlines()[0]
    else:
        with open(support_dir + 'hh_path', 'w') as f:
            f.write('/')

def get_hands():
    '''
    Sides: Deletes everything in the directory indicated by HH_FOLDER_PATH
    Returns:
        hand_list (str): string concatenation of all txt files in directory
        specified by HH_FOLDER_PATH.
    '''
    folder_path = load_hh_path()
    tables = map(lambda f: folder_path + '/' + f, os.listdir(folder_path))
    hand_list = ''
    for f in tables:
        if ('HandHistory' not in f) or (os.path.isdir(f)):
            return []
        with open(f, 'r') as fo:
            hand_list += fo.read() + '\n'

        # if backup doesn't exist make one
        if not os.path.isdir(HH_BACKUP_PATH):
            os.mkdir(HH_BACKUP_PATH)
        # to backup the file, save name of txtfile
        # rfind finds last occurence of a character in a string
        backup = HH_BACKUP_PATH + f[f.rfind('/'):]
        # if a txt file already exists for this table & date, append to it.
        if os.path.exists(backup):
            with open(backup, 'a') as fo:
                for hand in hand_list:
                    fo.write(hand)
        # otherwise make it
        else:
            os.rename(f, backup)
        # make sure no processed hands are left in pokerstars' HH folder.
        if os.path.exists(f):
            os.remove(f)

    # split by multiple new lines and filter 'trivial' hands
    hand_list = filter(lambda x: len(x) > 1, re.split('\n\n(\n)*', hand_list))

    return hand_list 

def get_tables():
    tables = []
    # kCGWindowListOptionOnScreenOnly should ensure that windows
    # are displayed in order, i.e. tables[0] will be the front-most
    # table.
    windows = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly,
            kCGNullWindowID)
    for window in windows:
        # this is redundant, we can merge these lists and simplify the 
        # check below. 
        blocked_windows = ['PokerStars Lobby', 'PokerStars', 'Focus Proxy']
        blocked_tables = ['Spin', 'Lobby', 'Rematch', 'Auto Rebuy', 'Buy-in']
        # check for key before trying to access it
        if 'kCGWindowName' in window:
            conditions = [window['kCGWindowOwnerName'] in POKER_CLIENTS,
                    window['kCGWindowName'] not in blocked_windows,
                    not any([t in window['kCGWindowName'] for t in blocked_tables])]
            if all(conditions):
                tables.append(window)
    return tables

def id_table(window_name):
    # identify a table by its kCGWindowName
    table_rx = re.compile("([a-zA-Z0-9]+\s*[a-zA-Z0-9]*) -")
    m = table_rx.match(window_name)
    if m:
        return m.group(1)
    ante_rx = re.compile("([a-zA-Z0-9]+\s*[a-zA-Z0-9]*) Ante -")
    m = ante_rx.match(window_name)
    if m:
        return m.group(1)
    tourney_rx = re.compile(".* - Tournament ([0-9]+) Table ([0-9]+)")
    m = tourney_rx.match(window_name)
    if m:
        return m.group(1) + " " + m.group(2)

def get_screen_dimensions():
    return (int(NSScreen.mainScreen().frame()[1].width), \
            int(NSScreen.mainScreen().frame()[1].height))

def config_exists():
    support_dir = '/Users/' + os.getlogin() + \
            '/Library/Application Support/' + HUD_NAME + '/'
    return os.path.isfile(support_dir + 'user_config')
