import kivy
kivy.require('1.9.1') 

# stuff i wrote
import dbs
import proc_hands
import os_tools

# this must proceed other imports
from kivy.config import Config
Config.set('graphics', 'position', 'custom')
Config.set('graphics', 'left', 0)
Config.set('graphics', 'top', 0)
Config.set('graphics', 'width', os_tools.get_screen_dimensions()[0])
Config.set('graphics', 'height', os_tools.get_screen_dimensions()[1])
Config.set('graphics', 'resizable', 0)
Config.set('graphics', 'borderless', 1)

# kivy imports
from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics import Rectangle
from kivy.uix.widget import Widget
from kivy.uix.layout import Layout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.checkbox import CheckBox
from kivy.core.text.text_layout import layout_text
from kivy.core.window import Window
from kivy.graphics.context_instructions import Color
from kivy.animation import Animation
from kivy.properties import ListProperty 
from kivy.properties import BooleanProperty 
from kivy.properties import StringProperty 
from kivy.properties import NumericProperty 
from kivy.properties import ObjectProperty 

# external packages
import sqlite3, re, os, string

# Constants
HU_DB = "HU_PLAYERS"
SIX_DB = "SIX_MAX_PLAYERS"
NINE_DB = "NINE_MAX_PLAYERS"
TABLE_DB = "TABLES"

# Determines how quickly 'bump' animations play in settings menu
BUMP_TIME = 0.08

# Player DataBase List
# As a convention, sng tournament tables are identified w/ the number of
# seats minus 1 (e.g. the heads up sng db is given by the key "1"
PDBL = {"2": (dbs.hu_conn, HU_DB), \
        "6": (dbs.six_conn, SIX_DB), \
        "9": (dbs.nine_conn, NINE_DB), \
        "1": (dbs.hu_sng_conn, HU_DB), \
        "5": (dbs.six_sng_conn, SIX_DB), \
        "8": (dbs.nine_sng_conn, NINE_DB)}

# Color Constants
COLORS = dbs.COLORS

class Tracker(FloatLayout):
    # table data, auxillary table data, menu properties
    tab_d = ListProperty([])
    tab_d_aux = ListProperty([])
    mp = ListProperty([])
    # checkbox booleans
    auto_bool = BooleanProperty()
    pro_bool = BooleanProperty()
    custom_bool = BooleanProperty()
    custom_text = StringProperty()
    # custom config text
    custom_instructions = StringProperty()
    # properties for animations
    bump_controller = ObjectProperty(None)
    bump_controller2 = ObjectProperty(None)
    bc_layout_t = ObjectProperty(None)
    bc_path_t = ObjectProperty(None)
    layout_save_button = ObjectProperty(None)
    hh_save_button = ObjectProperty(None)
    saved_hh_path = ObjectProperty(None)
    saved_layout = ObjectProperty(None)
    quit = ObjectProperty(None)

    def __init__(self):
        # kv file only recognizes stuff initialized before super init is called
        self.tab_d = ['loading'] * 12
        self.tab_d_aux = ['loading'] * 6
        self.mp = [None] * 4
        self.auto_bool = True
        self.pro_bool = False
        self.custom_bool = False 
        self.custom_text = ''
        self.load_settings()
        self.auto_hints = self.load_hints()
        self.custom_instructions = self.colorize("" + \
                "HUD customization 101:\n" + \
                "To customize your HUD, punch in a template here. The " + \
                "keywords name, hands, vpip, pfr, 3bet, 3btf, 4bet, " + \
                "4btf, stl, fts, cbet, cbturn, cbrivr, cbtf, fcbturn, " + \
                "and fcbrivr will all be swapped out with the stats they " + \
                "represent, e.g:\n    name/(hands)/vpip\nwill look " + \
                "something like:\n    ") + \
                "[color=" + COLORS["name"] + "]neverfoldmyhand94[/color]/" + \
                "([color=" + COLORS["hands"] + "]" + \
                "210[/color])/[color=" + COLORS["vpip"] + "]65[/color]"

        # get username from hh_path
        folders = self.load_hh_path()
        if folders != None:
            folders = folders.split('/')
            self.user = folders[len(folders) - 1]

        # databases
        dbs.init_player_DB(dbs.hu_conn, HU_DB)
        dbs.init_player_DB(dbs.six_conn, SIX_DB)
        dbs.init_player_DB(dbs.nine_conn, NINE_DB)
        dbs.init_player_DB(dbs.hu_sng_conn, HU_DB)
        dbs.init_player_DB(dbs.six_sng_conn, SIX_DB)
        dbs.init_player_DB(dbs.nine_sng_conn, NINE_DB)
        dbs.init_table_db(dbs.table_conn, TABLE_DB)

        # if you don't override this size defaults to screen resolution
        # for some reason.
        self.size_hint = (None, None)

        # screen dimensions according to AppKit
        self.scr_d = os_tools.get_screen_dimensions()
        # screen dimensions according to kivy Window class
        self.win_scale = [Window.size[0] / float(self.scr_d[0]), \
                Window.size[1] / float(self.scr_d[1])]

        # TODO: Get rid of this stuff? i don't think it does anything anymore
        # menu position (0), size (1), text (2), total screen dimensions (3)
        self.mp[3] = self.scale(self.scr_d)
        self.mp[1] = map(lambda x: 0.7 * x, self.mp[3])
        self.mp[0] = map(lambda x: x/2, self.scale(self.scr_d))
        self.mp[0] = map(lambda i: self.mp[0][i] - (self.mp[1][i]/2), range(2))
        self.mp[2] = 'Settings\n\n'

        self.front_end_update()
        self.back_end_update()
        super(Tracker, self).__init__()

    # add markup color data to keywords. make sure this only gets
    # called *once* wherever you use it.
    def colorize(self, s):
        for key in COLORS.keys():
            s = s.replace(key, "[color=" + COLORS[key] + "]" + key + "[/color]")
        return s

    # update internal state of hud config
    def hud_label_toggle(self, pressed):
        if pressed == 'auto':
            self.auto_bool = True
            self.pro_bool = False
            self.custom_bool = False
        elif pressed == 'pro':
            self.auto_bool = False
            self.pro_bool = True
            self.custom_bool = False
        elif pressed == 'custom':
            self.auto_bool = False
            self.pro_bool = False
            self.custom_bool = True

    # update custom hud config text
    def text_update(self, text):
        self.custom_text = text

    def save_hh_path(self, text):
        support_dir = '/Users/' + os.getlogin() + \
                '/Library/Application Support/' + os_tools.HUD_NAME + '/'
        if not os.path.isdir(support_dir):
            os.mkdir(support_dir)
        if os.path.exists(support_dir + 'hh_path'):
            with open(support_dir + 'hh_path', 'w') as hh_path:
                hh_path.write(text)
                folders = text.split('/')
                self.user = folders[len(folders) - 1]
        else:
            with open(support_dir + 'hh_path', 'w') as f:
                f.write(text)
        # save animation
        anim = Animation(color = [1,1,0.8,1], duration = BUMP_TIME * 3)
        anim += Animation(color = [1,1,0.8,1], duration = BUMP_TIME * 3)
        anim += Animation(color = [1,1,1,0], duration = BUMP_TIME * 3)
        anim.start(self.saved_hh_path)
        # set self.user
        if text != None:
            self.user = folders[len(folders) - 1]

    def load_hh_path(self):
        support_dir = '/Users/' + os.getlogin() + \
                '/Library/Application Support/' + os_tools.HUD_NAME + '/'
        if not os.path.isdir(support_dir):
            os.mkdir(support_dir)
        if os.path.exists(support_dir + 'hh_path'):
            with open(support_dir + 'hh_path', 'r') as hh_path:
                return hh_path.readlines()[0]
        else:
            with open(support_dir + 'hh_path', 'w') as f:
                f.write('/')

    def save_settings(self):
        support_dir = '/Users/' + os.getlogin() + \
                '/Library/Application Support/' + os_tools.HUD_NAME + '/'
        if not os.path.isdir(support_dir):
            os.mkdir(support_dir)
        with open(support_dir + 'user_config', 'w') as config:
            settings = str(self.auto_bool) + '\n' + \
                str(self.pro_bool) + '\n' + \
                str(self.custom_bool) + '\n' + \
                self.custom_text
            config.write(str(settings))
        anim = Animation(color = [1,1,0.8,1], duration = BUMP_TIME * 3)
        anim += Animation(color = [1,1,0.8,1], duration = BUMP_TIME * 3)
        anim += Animation(color = [1,1,1,0], duration = BUMP_TIME * 3)
        anim.start(self.saved_layout)

    def load_settings(self):
        support_dir = '/Users/' + os.getlogin() + \
                '/Library/Application Support/' + os_tools.HUD_NAME + '/'
        if os_tools.config_exists():
            with open(support_dir + 'user_config', 'r') as config:
                settings = config.readlines()
                i = settings.index('True\n')
                self.auto_bool = False
                self.pro_bool = False
                self.custom_bool = False
                if i == 0:
                    self.auto_bool = True
                elif i == 1:
                    self.pro_bool = True
                else:
                    self.custom_bool = True
                if len(settings) == 4:
                    self.custom_text = settings[3]
                else:
                    self.custom_text = ''

    def load_hints(self):
        with open('auto_hints', 'r') as f:
            hints = reduce(lambda x, y: x + y, f.readlines()).split('~')
            # remove new line characters since text will scale to its container.
            tbl = string.maketrans('^', '\n')
            hints =  map(lambda x: x.translate(tbl, '\n'), hints)
            return map(lambda x: self.colorize(x), hints)

    def scale(self, tup):
        return (int(tup[0] * self.win_scale[0]), \
                int(tup[1] * self.win_scale[1]))

    def cpt_size(self):
        size_arr = []
        for table in self.tables:
            w = table['kCGWindowBounds']['Width']
            h = table['kCGWindowBounds']['Height']
            size_arr.append(self.scale((w, h)))
        self.size_arr = size_arr
        self.size = self.size_arr[0]

    def cpt_pos(self):
        pos_arr = []
        for table in self.tables:
            x = table['kCGWindowBounds']['X']
            y = self.scr_d[1] \
                - table['kCGWindowBounds']['Y'] \
                - table['kCGWindowBounds']['Height']
            pos_arr.append(self.scale((x, y)))
        self.pos_arr = pos_arr
        self.pos = pos_arr[0]

    def update_tables(self):
        # never run cpt_pos or cpt_size w/o setting self.tables
        self.tables = os_tools.get_tables()
        if len(self.tables) > 0:
            self.mp[3] = self.scale(self.scr_d)
        else:
            self.mp[3] = (0, 0)

    def front_end_update(self, *args):
        # cheap stuff
        self.update_tables()
        if len(self.tables) > 0:
            self.cpt_size()
            self.cpt_pos()

    def back_end_update(self, *args):
        # expensive stuff
        hands = os_tools.get_hands() 
        for hand in hands:
            h = proc_hands.proc_hand(hand)
            t = proc_hands.proc_table(hand)
            dbs.add_table_to_DB(t, dbs.table_conn, TABLE_DB)
            if t[1] == 8:
                for player in h:
                    dbs.add_player_hand_to_DB(player, dbs.nine_sng_conn, NINE_DB)
            elif t[1] == 5:
                for player in h:
                    dbs.add_player_hand_to_DB(player, dbs.six_sng_conn, SIX_DB)
            elif t[1] == 1:
                for player in h:
                    dbs.add_player_hand_to_DB(player, dbs.hu_sng_conn, HU_DB)
            elif t[1] == 9:
                for player in h:
                    dbs.add_player_hand_to_DB(player, dbs.nine_conn, NINE_DB)
            elif t[1] == 6:
                for player in h:
                    dbs.add_player_hand_to_DB(player, dbs.six_conn, SIX_DB)
            elif t[1] == 2:
                for player in h:
                    dbs.add_player_hand_to_DB(player, dbs.hu_conn, HU_DB)
      
        if len(self.tables) > 0:
            t_name = os_tools.id_table(self.tables[0]['kCGWindowName'])
        else:
            t_name = None
            self.tab_d = ['loading'] * 12
            self.tab_d_aux = ['loading'] * 6
        hu_villain = ''
        if t_name != None:
            temp_tab_d = dbs.get_table_data(t_name, dbs.table_conn, TABLE_DB)
            if temp_tab_d != None:
                self.tab_d = temp_tab_d
                if self.user == self.tab_d[3]:
                    hu_villain = self.tab_d[2]
                else:
                    hu_villain = self.tab_d[3]
        if self.tab_d != None and t_name != None:
            for i in range(2, 12):
                if self.tab_d[i] != 'loading':
                    if (self.auto_bool):
                        h = dbs.get_player_data(self.user,
                            PDBL[str(self.tab_d[1])][0], 
                            PDBL[str(self.tab_d[1])][1])[1]
                    else:
                        h = -1
                    self.tab_d[i] = dbs.get_player_label(self.tab_d[i], 
                            PDBL[str(self.tab_d[1])][0], 
                            PDBL[str(self.tab_d[1])][1],
                            h,
                            self.pro_bool,
                            self.custom_bool,
                            self.custom_text) 
            c_i = self.tab_d[1] 
            if c_i in [1, 5, 8]:
                c_i += 1
            if c_i == 'loading':
                return
            for i in range(2, 12):
                if self.user in self.tab_d[i]:
                    self.tab_d = self.tab_d[0:2] + \
                            self.tab_d[i: c_i + 2] + \
                            self.tab_d[2:i] + self.tab_d[c_i + 2:]
                    # Expect self.user's data to be in self.tab_d[2]
                    # ud_t: User data, temporary 
                    ud_t = dbs.get_user_label(self.user, 
                            PDBL[str(self.tab_d[1])][0], 
                            PDBL[str(self.tab_d[1])][1],
                            self.auto_bool,
                            self.pro_bool,
                            self.custom_bool,
                            self.custom_text) 
                    self.tab_d[2] = ud_t
                    if self.auto_bool and h > -1:
                        self.tab_d[11] = self.get_auto_hint(h)
            if self.tab_d[1] in [5, 6]:
                self.tab_d_aux[0] = self.tab_d[2]
                self.tab_d_aux[1] = self.tab_d[3]
                self.tab_d_aux[2] = self.tab_d[4]
                # TODO: flatten top label
                self.tab_d_aux[3] = self.tab_d[5]
                self.tab_d_aux[4] = self.tab_d[6]
                self.tab_d_aux[5] = self.tab_d[7]
                for i in range(3,11):
                    self.tab_d[i] = ' '
            if self.tab_d[1] in [1, 2]:
                # TODO: make opponent label detailed in HU
                self.tab_d_aux[3] = self.tab_d[3]
                self.tab_d_aux[3] = dbs.get_user_label(hu_villain,
                            PDBL[str(self.tab_d[1])][0], 
                            PDBL[str(self.tab_d[1])][1],
                            self.auto_bool,
                            self.pro_bool,
                            self.custom_bool,
                            self.custom_text) 
                for i in range(3,11):
                    self.tab_d[i] = ' '
                for i in [0,1,2,4,5]:
                    self.tab_d_aux[i] = ' '
            if self.tab_d[1] in [8, 9]:
                self.tab_d_aux = [' '] * 6

    def collides(self, point, box):
        return (box[0] < point[0] < box[1]) and (box[2] < point[1] < box[3])
        
    # compute bump for interactive settings menu elements
    def cpt_bump(self, *args):
        # if a table is active, the settings menu is offscreen so don't do
        # any laborious computations. This is the same test performed in HUD.kv
        # to check if a table is on screen.
        if self.tab_d[2] not in [None, 'loading']:
            return
        # buffer zone to trigger animation
        buf = 0.005
        hh_menu_coll = [0.165 - buf, 0.165 + 0.385 + buf,
                0.1 - buf, 0.1 + 0.385 + buf]
        layout_menu_coll = [0.165 - buf, 0.165 + 0.385 + buf,
                0.52 - buf, 0.52 + 0.265 + buf]
        hh_button_coll = [0.2 - buf, 0.2 + 0.33 + buf,
                0.1 - buf, 0.1 + 0.035 + buf]
        layout_button_coll = [0.3175 + 0.0125 - buf, 0.3175 + 0.0125 + 0.2 + buf,
                0.495 + 0.025 - buf, 0.495 + 0.025 + 0.03 + buf]
        quit_button_coll = [0.7 - buf, 0.7 + 0.1 + buf,
                0.18 - buf, 0.18 + 0.1 + buf]

        if self.bump_controller != None and len(self.bump_controller.mouse_coords) == 2:
            x = self.bump_controller.mouse_coords[0]
            y = self.bump_controller.mouse_coords[1]
            cursor = (x / self.scr_d[0]), (y / self.scr_d[1]) 
            if self.collides(cursor, hh_menu_coll):
                if self.bump_controller.size[0] == self.bump_controller.min_size[0]:
                    self._bump_hh_menu_up()
                    self._bump_layout_menu_down()
                if self.collides(cursor, hh_button_coll):
                    self._highlight_button('hh')
            elif self.collides(cursor, layout_menu_coll):
                if self.bump_controller2.size[0] == self.bump_controller2.min_size[0]:
                    self._bump_layout_menu_up()
                    self._bump_hh_menu_down()
                if self.collides(cursor, layout_button_coll):
                    self._highlight_button('layout')
            elif self.collides(cursor, quit_button_coll):
                self._highlight_button('quit')
            else:
                if self.bump_controller.size[0] == self.bump_controller.max_size[0]:
                    self._bump_hh_menu_down()
                if self.bump_controller2.size[0] == self.bump_controller2.max_size[0]:
                    self._bump_layout_menu_down()
            if not self.collides(cursor, layout_button_coll):
                self._lowlight_button('layout')
            if not self.collides(cursor, hh_button_coll):
                self._lowlight_button('hh')
            if not self.collides(cursor, quit_button_coll):
                self._lowlight_button('quit')


    def _lowlight_button(self, bid): 
        if bid == 'layout':
            color = self.layout_save_button.color_passive
            anim = Animation(button_color = color, duration = BUMP_TIME / 2)
            anim.start(self.layout_save_button)
        elif bid == 'hh':
            color = self.hh_save_button.color_passive
            anim = Animation(button_color = color, duration = BUMP_TIME / 2)
            anim.start(self.hh_save_button)
        elif bid == 'quit':
            color = self.hh_save_button.color_passive
            anim = Animation(button_color = color, duration = BUMP_TIME / 2)
            anim.start(self.quit)

    def _highlight_button(self, bid): 
        if bid == 'layout':
            color = self.layout_save_button.color_active
            anim = Animation(button_color = color, duration = BUMP_TIME / 2)
            anim.start(self.layout_save_button)
        elif bid == 'hh':
            color = self.hh_save_button.color_active
            anim = Animation(button_color = color, duration = BUMP_TIME / 2)
            anim.start(self.hh_save_button)
        elif bid == 'quit':
            color = self.hh_save_button.color_active
            anim = Animation(button_color = color, duration = BUMP_TIME / 2)
            anim.start(self.quit)

    def _bump_layout_menu_up(self):
        # bump menu box
        bump_pos = self.bump_controller2.max_pos
        bump_size = self.bump_controller2.max_size
        anim = Animation(pos = bump_pos, duration = BUMP_TIME)
        anim &= Animation(size = bump_size, duration = BUMP_TIME)
        anim.start(self.bump_controller2)
        # bump label
        la = Animation(x = self.bc_layout_t.xa, duration = BUMP_TIME)
        la &= Animation(y = self.bc_layout_t.ya, duration = BUMP_TIME)
        la.start(self.bc_layout_t)

    def _bump_hh_menu_up(self):
        bump_pos = self.bump_controller.max_pos
        bump_size = self.bump_controller.max_size
        anim = Animation(pos = bump_pos, duration = BUMP_TIME)
        anim &= Animation(size = bump_size, duration = BUMP_TIME)
        anim.start(self.bump_controller)
        la = Animation(x = self.bc_path_t.xa, duration = BUMP_TIME)
        la &= Animation(y = self.bc_path_t.ya, duration = BUMP_TIME)
        la.start(self.bc_path_t)

    def _bump_hh_menu_down(self):
        bump_pos = self.bump_controller.min_pos
        bump_size = self.bump_controller.min_size
        anim = Animation(pos = bump_pos, duration = BUMP_TIME)
        anim &= Animation(size = bump_size, duration = BUMP_TIME)
        anim.start(self.bump_controller)
        la = Animation(x = self.bc_path_t.xn, duration = BUMP_TIME)
        la &= Animation(y = self.bc_path_t.yn, duration = BUMP_TIME)
        la.start(self.bc_path_t)

    def _bump_layout_menu_down(self):
        bump_pos = self.bump_controller2.min_pos
        bump_size = self.bump_controller2.min_size
        anim = Animation(pos = bump_pos, duration = BUMP_TIME)
        anim &= Animation(size = bump_size, duration = BUMP_TIME)
        anim.start(self.bump_controller2)
        la = Animation(x = self.bc_layout_t.xn, duration = BUMP_TIME)
        la &= Animation(y = self.bc_layout_t.yn, duration = BUMP_TIME)
        la.start(self.bc_layout_t)

    def get_auto_hint(self, h):
        # get the current auto mode hint based on no. of hands played
        if (h / 50) < len(self.auto_hints):
            return self.auto_hints[h / 50]
        return self.auto_hints[len(self.auto_hints) - 1]


class HUD(App):
    mouse_position = ListProperty([])
    def build(self):
        # bind mouse position to on_mouse
        Window.bind(mouse_pos=self.on_mouse)
        player = Tracker()
        # backend update is more intensive, do it less often
        fps = 60
        Clock.schedule_interval(player.front_end_update, 1 / float(fps))
        Clock.schedule_interval(player.back_end_update, 5)
        # set cpt_bump calls to lower frame rate to avoid jittery animations
        Clock.schedule_interval(player.cpt_bump, 3 / float(fps))
        return player

    def on_mouse(self, w, p):
        self.mouse_position = [p[0], p[1]]

if __name__ == '__main__':
    HUD().run()
