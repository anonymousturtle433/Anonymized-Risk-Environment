import collections
import logging
LOG = logging.getLogger("pyrisk")
import curses
import time
import sys
import os
import pygame
from pygame.locals import *
from gym_risk.envs.game.display_utils.func import DisplayFunc
import gym_risk.envs.game.display_utils.constants_new as constants
from gym_risk.envs.game.display_utils.graph import WeightedDirectedGraph

class LogQueue(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self, level=logging.DEBUG)
        self.queue = []
    def emit(self, record):
        self.queue.append(record)

class Display(object):

    def update(self, msg, player=None, territory=None):
        pass

class PygameDisplay(Display):
    def __init__(self, game, map_name):
        '''
        Class for PyGame display for risk domain
        :param game: game object
        :param map_name: Map name for initializing specific map setup from the dataset
        '''

        self.game = game
        self.t_coords = collections.defaultdict(list)
        self.d_func = DisplayFunc()
        self.t_centre = {}
        self.map_name = map_name
        self.logqueue = LogQueue()

        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        self.risk_map = WeightedDirectedGraph()
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        filename = "/display_utils/risk-map-study.txt"
        # Populate risk_map variable based on risk-map-study file
        with open(cur_dir + filename) as file:
            for line in file:  # Variable 'line' loops over each line in the file
                line = line.strip()  # Remove trailing newline character
                # Process the line here
                line = line.split(',')
                if line[0] == 'V':  # add vertex
                    self.risk_map.add_vertex(line[1])
                elif line[0] == 'E':  # add add_edge
                    self.risk_map.add_edge(line[1], line[2], line[3])

        # Set all territories to neutral
        for territory in self.d_func.TERRITORIES:
            territory["Color"] = constants.LIGHT_GREY
            territory["Player"] = 3
            territory["Infantry"] = 0

        self.d_func.text1 = "Initializing..."
        print("Setup complete")
        self.d_func.refresh()

    def player_to_color(self, player):
        '''
        Return grey or black based on the player number
        :param player: 0/1
        :return:
        '''
        if player == 0:
            return 'grey'
        elif player == 1:
            return 'black'

    def convert_owner(self, name):
        '''
        Convert player name to numbers
        2 corresponds to the ego-player
        [0,1] corresponds to the two opponents
        3 corresponds to neutral
        :param name:
        :return:
        '''
        if name == 'ALPHA':
            return 2
        elif name == 'BRAVO':
            return 0
        elif name == 'CHARLIE':
            return 1
        else:
            return 3

    def owner_color(self, owner):
        '''
        Color to be displayed for a country given the owner of the country
        :param owner: player number [0,1,2,3]
        :return:
        '''
        if owner == 0:
            return constants.ORANGE
        elif owner == 1:
            return constants.PINK
        elif owner == 2:
            return constants.TEAL
        else:
            return constants.LIGHT_GREY

    def update(self, msg, territory=None, player=None, extra=None, modal=False):
        '''
        Update display based on the new game state
        Loop through all territories, and update the d_func object
        :param msg: Message containing information regarding action taken
        :param territory:
        :param player:
        :param extra:
        :param modal:
        :return:
        '''
        for name, t in self.game.world.territories.items():
            for terr in self.d_func.TERRITORIES:
                if terr["Name"] == t.name:
                    break
            if t.owner:
                owner = self.convert_owner(t.owner.name)
            else:
                owner = 3
            self.risk_map.set_owner(t.name, owner)
            color = self.owner_color(owner)
            terr['Color'] = color
            terr['Infantry'] = t.forces
            terr['Player'] = owner
            self.risk_map.set_armies(t.name, t.forces)
        self.d_func.text1 = self.format(msg)
        for i, name in enumerate(self.game.players):
            p = self.game.players[name]

            if p.name is "ALPHA":
                self.d_func.at = p.territory_count
                self.d_func.af = p.forces
                self.d_func.ar = p.reinforcements
            elif p.name is "BRAVO":
                self.d_func.bt = p.territory_count
                self.d_func.bf = p.forces
                self.d_func.br = p.reinforcements
            elif p.name is "CHARLIE":
                self.d_func.ct = p.territory_count
                self.d_func.cf = p.forces
                self.d_func.cr = p.reinforcements
        self.d_func.refresh()
        self.d_func.current_player = player

        ## You have to press a button to go to the next move
        b = True
        while b:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    b = False

    def format(self, msg):
        '''
        Format msg object into message to be displayed on the screen
        :param msg:
        :return:
        '''
        if msg[0] == 'start':
            return "Game begins"
        elif msg[0] == 'victory':
            return "Victory to %s" % msg[1].name
        elif msg[0] == 'reinforce':
            _, player, t, f = msg
            return "%s reinforces %s with %d (total %d)" % (player.name, t.name, f, t.forces)
        elif msg[0] == 'conquer':
            _, player, oppfor, st, tt, init, final = msg
            if oppfor == 'Empty':
                return "%s conquers %s in %s from %s (lost %da, %dd)" % (player.name, 'Empty', tt.name, st.name, init[0]-final[0]-final[1], init[1])
            else:
                return "%s conquers %s in %s from %s (lost %da, %dd)" % (player.name, oppfor.name, tt.name, st.name, init[0]-final[0]-final[1], init[1])
        elif msg[0] == 'defeat':
            _, player, oppfor, st, tt, init, final = msg
            return "%s defeated by %s in %s from %s (lost %da, %dd)" % (player.name, oppfor.name, tt.name, st.name, init[0]-final[0], init[1]-final[1])
        elif msg[0] == 'move':
            _, player, st, tt, f = msg
            return "%s moves %d from %s to %s (total %d)" % (player.name, f, st.name, tt.name, tt.forces)
        elif msg[0] == 'claim':
            _, player, t = msg
            return "%s claims %s" % (player.name, t.name)
        elif msg[0] == 'deal':
            _, player, t = msg
            return "%s dealt %s" % (player.name, t.name)
        else:
            return msg
            # raise

class CursesDisplay(Display):
    EMPTY = ord(' ')
    UNCLAIMED = ord(':')
    ix = 80
    iy = 20
    def __init__(self, screen, game, cmap, ckey, color, wait):
        self.screen = screen
        self.game = game
        self.t_coords = collections.defaultdict(list)
        self.t_centre = {}
        self.color = color
        self.wait = wait
        self.logqueue = LogQueue()
        self.highest_open_logline = len(self.game.turn_order) + 4
        LOG.addHandler(self.logqueue)

        self.wx = 0
        self.wy = 0
        for j, line in enumerate(cmap.strip('\n').split('\n')):
            self.wy += 1
            self.wx = max(self.wx, len(line))
            for i, char in enumerate(line):
                if char in ckey:
                    self.t_coords[ckey[char]] += [(i, j)]

        for t, ijs in self.t_coords.items():
            sum_i = sum(i[0] for i in ijs)
            sum_j = sum(i[1] for i in ijs)
            self.t_centre[t] = (sum_j//len(ijs), sum_i//len(ijs))
        
        self.sy, self.sx = self.screen.getmaxyx()    
        curses.noecho()
        if self.color:
            for i in range(1, 8):
                curses.init_pair(i, i, curses.COLOR_BLACK)
        
        self.worldpad = curses.newpad(self.wy, self.wx)
        self.infopad = curses.newpad(self.iy, self.ix)


    def format(self, msg):
        if msg[0] == 'start':
            return "Game begins"
        elif msg[0] == 'victory':
            return "Victory to %s" % msg[1].name
        elif msg[0] == 'reinforce':
            _, player, t, f = msg
            return "%s reinforces %s with %d (total %d)" % (player.name, t.name, f, t.forces)
        elif msg[0] == 'conquer':
            _, player, oppfor, st, tt, init, final = msg
            if oppfor == 'Empty':
                return "%s conquers %s in %s from %s (lost %da, %dd)" % (player.name, 'Empty', tt.name, st.name, init[0]-final[0]-final[1], init[1])
            else:    
                return "%s conquers %s in %s from %s (lost %da, %dd)" % (player.name, oppfor.name, tt.name, st.name, init[0]-final[0]-final[1], init[1])
        elif msg[0] == 'defeat':
            _, player, oppfor, st, tt, init, final = msg
            return "%s defeated by %s in %s from %s (lost %da, %dd)" % (player.name, oppfor.name, tt.name, st.name, init[0]-final[0], init[1]-final[1])
        elif msg[0] == 'move':
            _, player, st, tt, f = msg
            return "%s moves %d from %s to %s (total %d)" % (player.name, f, st.name, tt.name, tt.forces)
        elif msg[0] == 'claim':
            _, player, t = msg
            return "%s claims %s" % (player.name, t.name)
        elif msg[0] == 'deal':
            _, player, t = msg
            return "%s dealt %s" % (player.name, t.name)
        else:
            return msg

    def update(self, msg, territory=None, player=None, extra=None, modal=False):
        if not territory:
            territory = []  
        if not player:
            player = []
        self.worldpad.clear()
        self.last_logline = 3
        for name, t in self.game.world.territories.items():
            if t.owner:
                attrs = curses.color_pair(t.owner.color)
                if self.color:
                    char = t.ord
                else:
                    char = t.owner.ord
            else:
                attrs = curses.COLOR_WHITE
                if self.color:
                    char = t.ord
                else:
                    char = self.UNCLAIMED
            # LOG.info(territory)
            ####################################################
            if t in territory:
                attrs |= curses.A_BOLD
            for i, j in self.t_coords[name]:
                self.worldpad.addch(j, i, char, attrs)
            if t.owner:
                self.worldpad.addstr(self.t_centre[name][0], 
                                     self.t_centre[name][1], 
                                     str(t.forces), attrs)
            ###################################################

        self.infopad.clear()
        info = "TURN " + str(self.game.turn//len(self.game.players)) + ": " + self.format(msg)
        if self.game.options['round']:
            info = ("ROUND %d/%d " % self.game.options['round']) + info
        self.infopad.addstr(0, 0, info, curses.COLOR_WHITE | curses.A_BOLD)
        self.infopad.addstr(2, 0, 
                            "NAME    AI      WINS    TERR    FORCES  +FORCES AREA", 
                            curses.COLOR_WHITE | curses.A_BOLD)
        for i, name in enumerate(self.game.turn_order):
            p = self.game.players[name]
            attrs = curses.color_pair(p.color)
            if name in player:
                attrs |= curses.A_BOLD
            if not p.alive:
                attrs |= curses.A_DIM
            info = [p.name, p.ai.__class__.__name__[:-2], 
                    str(self.game.options['history'].get(p.name, 0)), 
                    str(p.territory_count), str(p.forces), 
                    str(p.reinforcements)]
            info = "".join(s.ljust(8)[:8] for s in info) + " ".join(a.name for a in p.areas)
            self.infopad.addstr(3+i, 0, info, attrs)

        self.highest_open_logline = len(self.game.turn_order) + 4
        for i, record in enumerate(self.logqueue.queue):
            if self.highest_open_logline == self.iy - 4 and i < len(self.logqueue.queue) - 1:
                self.infopad.addstr(self.highest_open_logline+1, 0, "(%d more suppressed)" % (len(self.logqueue.queue) - i), curses.A_NORMAL)
                break
            else:
                self.infopad.addstr(self.highest_open_logline, 0, record.getMessage()[:self.ix-1], curses.A_NORMAL)
            self.highest_open_logline += 1
        
        delay = self.game.options['delay']
        if any(r.levelno > logging.WARN for r in self.logqueue.queue):
            delay *= 5
                
        self.logqueue.queue = []
        

        self.worldpad.overwrite(self.screen, 0, 0, 1, 1, 
                                min(self.sy-1, self.wy), min(self.sx-1, self.wx-1))
        self.infopad.overwrite(self.screen, 0, 0, min(self.wy+2, self.sy-1), 0, 
                               min(self.sy-1, self.wy + self.iy+1), min(self.ix-1, self.sx-1))
        self.screen.refresh()
        if self.wait or modal:
            self.screen.getch()
        else:
            time.sleep(delay)


    def add_infopad_msg(self, msg):
        self.infopad.addstr(1, 0, " "*100, curses.A_NORMAL) #replaces the previous content with spaces
        self.infopad.addstr(1, 0, msg, curses.A_NORMAL)
        self.infopad.overwrite(self.screen, 0, 0, min(self.wy+2, self.sy-1), 0, 
                               min(self.sy-1, self.wy + self.iy+1), min(self.ix-1, self.sx-1))
        self.screen.refresh()

