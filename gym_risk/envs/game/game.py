from gym_risk.envs.game.player import Player
from gym_risk.envs.game.display import Display, CursesDisplay, PygameDisplay
from gym_risk.envs.game.territory import World
from gym_risk.envs.game.world import CONNECT, AREAS, MAP, KEY, Action_map, Reversed_Action_map
from gym_risk.envs.game.ai.fixed_drafting_random import FixedDraftingRandomAI
from gym_risk.envs.game.ai.user_profiles.P1 import P1
from gym_risk.envs.game.ai.user_profiles.P2 import P2
from gym_risk.envs.game.ai.user_profiles.P3 import P3
from gym_risk.envs.game.ai.user_profiles.P4 import P4
from gym_risk.envs.game.ai.user_profiles.P5 import P5
from gym_risk.envs.game.ai.user_profiles.P6 import P6
from gym_risk.envs.game.ai.user_profiles.P7 import P7
from gym_risk.envs.game.ai.user_profiles.P8 import P8
from gym_risk.envs.game.deployment_maps import HUMAN_SELECTIONS
from gym import logger
import random
import logging
import time
from copy import deepcopy

LOG = logging.getLogger("pyrisk")

SMALL_DELAY = 0.1
MEDIUM_DELAY = 0.1
LONG_DELAY = 10

"""
Setting reward to none in return statement because we use custom reward function in risk_env
"""

class Game(object):
    """
    This class represents an individual game, and contains the main game logic.
    """

    defaults = {
        "pygame": False, #whether to use pygame map display
        "curses": False, #whether to use ncurses for map display
        "color": True, #whether to use color with ncurses
        "delay": 0.1, #seconds to sleep after each (ncurses) display update
        "screen": None, #a curses.window (for use with the curses.wrapper function)
        "round": None, #the round number
        "wait": False, #whether to pause and wait for a keypress after each event
        "history": {}, #the win/loss history for each player, for multiple rounds
        "deal": False, #deal out territories rather than let players choose
        "state": 0, #decide which initial state representation to use
        "fast": True, #decide whether to execute debugging delays
        'messages_on':True #decide whether logging messages should print
    }

    def __init__(self, **options):
        self.options = self.defaults.copy()
        self.options.update(options)
        self.fast = self.options['fast']
        self.messages_on = self.options['messages_on']


        self.world = World()
        self.world.load(AREAS, CONNECT)
        self.connect = CONNECT

        #update in the create gamestate function
        #uses the territory indices recorded in ActionMap
        self.empty_territories = []
        self.agent_territories = []
        self.opponent_territories = []

        self.empty_territory_names = []
        self.agent_territory_names = []
        self.opponent_territory_names = []

        self.players = {}
        self.live_players = 0
        self.init_troops = 0
        self.phase = 'init'

        self.turn = 0
        self.turn_order = []
        self.agent_turn_number = 0

        self.remaining = {}
        self.drafting = False
        self.finished = False
        self.agent_name = None

        self.initial_state = None #stores the initial game state for reset
        self.troops_remaining = 0 #store the state variable, since storing it in the player class messes things up and I can't figure out why
        self.human_locations = None
        self.human_reinforcment_amounts = None
        if self.options['map'] is not 'RANDOM':
            random_selection = random.randint(0, 2)
            self.human_locations = list(HUMAN_SELECTIONS[self.options['map']][random_selection].keys())
            self.human_reinforcment_amounts = HUMAN_SELECTIONS[self.options['map']][random_selection]

        self.game_state = [{},{},{}] #dict 0 - territory control #dict 1: area control  #dict 2: assorted information
        if self.options['curses']:
            self.display = CursesDisplay(self.options['screen'], self,
                                         MAP, KEY,
                                         self.options['color'], self.options['wait'])
        elif self.options['pygame']:
            self.display = PygameDisplay(self,
                                         self.options['map'])
        else: #need this to prevent bugs when curses is disabled
            self.display = Display()
            
    def add_player(self, name, ai_class, **kwargs):
        assert name not in self.players
        assert len(self.players) <= 5
        player = Player(name, self, ai_class, **kwargs)
        self.players[name] = player

    @property
    def player(self):
        """Property that returns the correct player object for this turn."""
        return self.players[self.turn_order[self.turn % len(self.players)]]


    def event(self, msg, territory=None, player=None):
        """
        Record any game action.
        `msg` is a tuple describing what happened.
        `territory` is a list of territory objects to be highlighted, if any
        `player` is a list of player names to be highlighted, if any
        
        Calling this method triggers the display to be updated, and any AI
        players that have implemented event() to be notified.
        """
        
        self.display.update(msg, territory=territory, player=player)
        for p in self.players.values():
            if not p.ai == None: 
                p.ai.event(msg)

    def message_event(self, msg):
        if type(self.display) == CursesDisplay:
            self.display.add_infopad_msg(msg)
        else:
            pass

    def create_game_state(self, state):
        self.empty_territories = []
        self.agent_territories = []
        self.opponent_territories = []

        self.empty_territory_names = []
        self.agent_territory_names = []
        self.opponent_territory_names = []

        for t_name, territory in state.territories.items():
            self.game_state[0][t_name] = {}
            if state.territories[t_name].owner == None: 
                self.game_state[0][t_name]['owner'] = 'None'
                self.game_state[0][t_name]['troops'] = 0 
                self.empty_territories.append(Reversed_Action_map[t_name])
                self.empty_territory_names.append(t_name)
            else:
                self.game_state[0][t_name]['owner'] = state.territories[t_name].owner.name
                self.game_state[0][t_name]['troops'] = state.territories[t_name].forces
                if state.territories[t_name].owner.name == self.agent_name:
                    self.agent_territories.append(Reversed_Action_map[t_name])
                    self.agent_territory_names.append(t_name)
                else:
                    self.opponent_territories.append(Reversed_Action_map[t_name])
                    self.opponent_territory_names.append(t_name)
        for area in state.areas:
            self.game_state[1][area] = {}
            if state.areas[area].owner == None: 
                self.game_state[1][area]['owner'] = 'None'  
            else:    
                self.game_state[1][area]['owner'] = state.areas[area].owner.name
        self.game_state[2]['reinforcements_remaining'] = self.troops_remaining
        self.game_state[2]['num_players_alive'] = self.live_players
        self.game_state[2]['round_number'] = self.agent_turn_number

    def load_game_state(self, state):
        self.empty_territories = []
        self.agent_territories = []
        self.opponent_territories = []

        self.empty_territory_names = []
        self.agent_territory_names = []
        self.opponent_territory_names = []

        territories = state[0]
        areas = state[1]
        assorted = state[2]
        for t_name, t_info in territories.items():
            if t_info['owner'] != 'None':
                self.world.territories[t_name].owner = self.players[t_info['owner']]
                self.world.territories[t_name].forces = t_info['troops']
                if self.world.territories[t_name].owner == self.agent_name:
                    self.agent_territories.append(Reversed_Action_map[t_name])
                    self.agent_territory_names.append(t_name)
                else:
                    self.opponent_territories.append(Reversed_Action_map[t_name])
                    self.opponent_territory_names.append(t_name)
            else:
                self.world.territories[t_name].owner = None
                self.world.territories[t_name].forces = 0
                self.empty_territories.append(Reversed_Action_map[t_name])
                self.empty_territory_names.append(t_name)


        self.game_state[2]['reinforcements_remaining'] = assorted['reinforcements_remaining']
        self.game_state[2]['num_players_alive'] = assorted['num_players_alive']
        self.game_state[2]['round_number'] = assorted['round_number']


    def warn(self, msg):
        """
        Record any game action.
        """
        if self.messages_on:
            logger.warn(str(msg))

    def aiwarn(self, *args):
        """Generate a warning message when an AI player tries to break the rules."""
        if self.messages_on:
            logging.getLogger("pyrisk.player.%s" % self.player.ai.__class__.__name__).warn(*args)

    def delay_wrapper(self, delay=SMALL_DELAY):
        """Wraps all delay functions, allowing them to easily be turned off when not debugging simulation"""
        if self.fast:
            pass
        else:
            time.sleep(delay)
            

    def init(self):
        self.turn_order = list(self.players)
        random.shuffle(self.turn_order)
        for i, name in enumerate(self.turn_order):
            self.players[name].color = i + 1
            self.players[name].ord = ord('\/-|+*'[i])
            self.players[name].ai.start()
        self.event(("start", ))
        live_players = len(self.players)
        
        self.message_event("Before initial_placement function")
        self.delay_wrapper(MEDIUM_DELAY)
        self.initial_placement()
        self.delay_wrapper(MEDIUM_DELAY)
        self.turn = 0
        # Add ego-player
        self.add_player("ALPHA", None)
        self.agent_name = "ALPHA"
        self.players[self.agent_name].color = len(self.players)
        self.players[self.agent_name].ord = ord('\/-|+*'[len(self.players)-1])
        self.live_players = len(self.players)
        self.turn_order = list(self.players)
        # Randomize turn order after adding the agent
        random.shuffle(self.turn_order)
        alpha_i = self.turn_order.index(self.agent_name)
        self.turn_order[0], self.turn_order[alpha_i] = self.turn_order[alpha_i], self.turn_order[0]
        self.message_event("Agent starts playing")
        self.troops_remaining = 14

        self.create_game_state(self.world)
        #saves initial state for use in fast reset   
        self.initial_state = deepcopy(self.game_state)         
        return ("drafting", False, self.game_state), None, False, {}

    def fast_reset(self):
        self.load_game_state(self.initial_state)
        self.finished = False
        self.init_troops = 0
        self.phase = 'init'
        self.turn = 0
        self.agent_turn_number = 0  
        self.create_game_state(self.world)
        self.message_event('Finished fast reset')
        return ("drafting", False, self.game_state), None, False, {}

    '''
    Takes a turn in the RISK Game 
    
    return -  observation - It further contains three things 
                                next_phase - The next phase for the player,
                                phase_done - If the phase is completed succesfully ,
                                full_state - Current state of the game,
              reward - overriden in the risk_env step function,
              done - If the game over ,
              info - Any additional info
    '''
    def step(self, action, phase = 'init', human_drafting=False):
        self.delay_wrapper(MEDIUM_DELAY)
        # ensure that live_player count is always accurate
        self.live_players = len([p for p in self.players.values() if p.alive])
        if self.player.ai == None:
            if self.phase == 'init':
                self.message_event(f"In drafting stage, Reinforcements remaining {self.player.remaining_troops}")
                if not action[0] == 0: #flag to specify initialisation is already specified
                    print("Initialization specified")
                    #if the agent doesn't take the deploy action in the deploy phase, make it lose the game
                    self.message_event("Incorrect action taken in drafting phase - lose")
                    self.create_game_state(self.world)
                    return ("loss", True, self.game_state), None, True, {}
                else:
                    if self.player.forces < 14:
                        """
                        Human Drafting variable is used to draft based on human selections when set True, 
                        otherwise drafting is done by the agent
                        """
                        if not human_drafting or self.human_locations is None or self.human_reinforcment_amounts is None:
                            t = self.world.territory(Action_map[action[1]])
                            if not t.owner == None and not t.owner.name == self.agent_name: 
                                self.message_event("Tried to select opponent territory during draft - lose")
                                #self.delay_wrapper(LONG_DELAY)
                                self.aiwarn("draft opposition owned territory during draft %s", t.name)
                                self.create_game_state(self.world)
                                return ("drafting", False, self.game_state), None, True, {}
                            t.owner = self.player
                            #check that action doesn't try to add more troops than available
                            if t.forces + action[3] > 14:
                                self.message_event("Tried to draft more troops than available - lose")
                                self.delay_wrapper(LONG_DELAY)
                                return ("drafting", False, self.game_state), None, True, {}
                            else:
                                num_troops = action[3]
                                t.forces += action[3]
                                self.troops_remaining -= num_troops

                            self.event(("reinforce", self.player, t, num_troops), territory=[t], player=[self.player])
                            #self.delay_wrapper(LONG_DELAY)
                            
                        else :
                            t = self.world.territory(self.human_locations[0])
                            t.owner = self.player
                            num_troops = self.human_reinforcment_amounts[self.human_locations[0]]
                            t.forces += self.human_reinforcment_amounts[self.human_locations[0]]
                            self.troops_remaining -= num_troops
                            self.human_locations.remove(self.human_locations[0])
                            self.event(("reinforce", self.player, t, num_troops), territory=[t], player=[self.player])
                            #self.delay_wrapper(LONG_DELAY)

                        if self.player.forces == 14:
                            self.agent_turn_number += 1
                            self.player.remaining_troops = self.player.reinforcements
                            self.troops_remaining = self.player.reinforcements

                            #set phase variable in the class/world to play
                            self.message_event("Changing game phase to reinforcement")
                            self.delay_wrapper(MEDIUM_DELAY)
                            self.phase = 'reinforce'
                            self.create_game_state(self.world)
                            return ("drafting", True, self.game_state), None, False, {}
                        self.create_game_state(self.world)
                        return ("drafting", False, self.game_state), None, False, {}
                    else:
                        self.message_event("Tried to draft when all troops placed - lose")
                        self.delay_wrapper(LONG_DELAY)
                        return ("drafting", False, self.game_state), None, True, {}


            elif self.phase == 'reinforce':
                self.troops_remaining = self.player.remaining_troops
                self.message_event(f"In reinforcement stage, Reinforcements remaining {self.player.remaining_troops}")
                self.delay_wrapper(MEDIUM_DELAY)
                if not action[0] == 1:
                    #Add event message
                    self.message_event("Didn't reinforce during reinforcement - lose")
                    self.delay_wrapper(LONG_DELAY)
                    self.create_game_state(self.world)
                    return ("reinforce", True, self.game_state), None, True, {}

                t = self.world.territory(Action_map[action[1]])
                f = action[3]

                self.message_event("Didn't reinforce during reinforcement - lose")

                if t is None:
                    self.aiwarn("reinforce invalid territory")
                    self.create_game_state(self.world)
                    self.message_event("Picked no territory during reinforcement - lose")
                    self.delay_wrapper(LONG_DELAY)
                    return ("reinforce", False, self.game_state), None, True, {}
                if t.owner != self.player:
                    self.aiwarn("reinforce unowned territory %s", t.name)
                    self.create_game_state(self.world)
                    self.message_event("Picked other player's territory during reinforcement - lose")
                    self.delay_wrapper(LONG_DELAY)
                    return ("reinforce", False, self.game_state), None, True, {}
                if f < 1:
                    self.aiwarn("reinforce invalid count %s", f)
                    self.create_game_state(self.world)
                    self.message_event("Tried to reinforce with fewer than 1 troop - lose")
                    self.delay_wrapper(LONG_DELAY)
                    return ("reinforce", False, self.game_state), None, True, {}
                if action[3] > self.player.remaining_troops:
                    self.message_event("Tried to reinforce with more troops than available- lose")
                    self.delay_wrapper(LONG_DELAY)
                    # diff_troops = f - self.player.remaining_troops    
                    # t.forces += diff_troops
                    # self.player.remaining_troops -= diff_troops
                    # self.event(("reinforce", self.player, t, diff_troops), territory=[t], player=[self.player])
                    # self.phase = 'attack'
                    #Add code to reinforce remainign troops and return true
                    self.create_game_state(self.world)
                    return ("reinforce", False, self.game_state), None, True, {}
                t.forces += f
                self.player.remaining_troops -= f
                self.troops_remaining -= f

                self.event(("reinforce", self.player, t, f), territory=[t], player=[self.player])
                self.create_game_state(self.world)
                if self.player.remaining_troops > 0:
                    self.message_event("More troops left to deploy")
                    return ("reinforce", False, self.game_state), None, False, {}
                else:
                    self.phase = 'attack'
                    self.message_event("Finished deploying troops")
                    self.delay_wrapper(MEDIUM_DELAY)
                    return ("reinforce", True, self.game_state), None, False, {} #move to the attack phase since no more troops to deploy
                #Add reward return statmeent

            elif self.phase == 'attack':
                self.message_event('In attack phase')
                self.delay_wrapper(MEDIUM_DELAY)
                if not action[0] == 2 and not action[0] == 3: #if agents 
                    self.message_event("Didn't attack or freemove during attack - lose")
                    self.delay_wrapper(LONG_DELAY)
                    self.create_game_state(self.world)
                    return ("attack", False, self.game_state), None, True, {}

                if action[0] == 2:
                    self.message_event('Attack action taken')
                    # self.delay_wrapper(MEDIUM_DELAY)

                    st = self.world.territory(Action_map[action[1]])
                    tt = self.world.territory(Action_map[action[2]])
                    if st is None:
                        self.aiwarn("attack invalid src")
                        self.message_event("attack invalid src None")
                        self.delay_wrapper(LONG_DELAY)
                        return ("attack", False, self.game_state), None, True, {}
                    if tt is None:
                        self.aiwarn("attack invalid target")
                        self.message_event("attack invalid target none")
                        self.delay_wrapper(LONG_DELAY)
                        return ("attack", False, self.game_state), None, True, {}
                    if st.owner != self.player:
                        self.aiwarn("attack from unowned src %s", st.name)
                        self.message_event(f"attack from unowned src {st.name}")
                        self.delay_wrapper(LONG_DELAY)
                        return ("attack", False, self.game_state), None, True, {}
                    if tt.owner == self.player:
                        self.aiwarn("attacking owned target %s", tt.name)
                        self.message_event(f"attacking owned target {tt.name}")
                        self.delay_wrapper(LONG_DELAY)
                        return ("attack", False, self.game_state), None, True, {}
                    if tt not in st.connect:
                        self.aiwarn("attack unconnected %s %s", st.name, tt.name)
                        self.message_event(f"attack unconnected {st.name} {tt.name}")
                        self.delay_wrapper(LONG_DELAY)
                        return ("attack", False, self.game_state), None, True, {}
                    if st.forces == 1:
                        self.aiwarn("Invalid attack; only one troop on %s", st.name)
                        self.message_event(f"Invalid attack; only one troop on {st.name}")
                        self.delay_wrapper(MEDIUM_DELAY)
                        return ("attack", False, self.game_state), None, True, {}
                    initial_forces = (st.forces, tt.forces)
                    move = action[3]
                    if tt.forces == 0:
                        victory = self.player_combat(st, tt, move)
                        final_forces = (st.forces, tt.forces)    
                        self.event(("conquer" if victory else "defeat", self.player, 'Empty', st, tt, initial_forces, final_forces), territory=[st, tt], player=[self.player.name, 'Empty'])
                    else:
                        opponent = tt.owner
                        victory = self.player_combat(st, tt, move)
                        final_forces = (st.forces, tt.forces)
                        self.event(("conquer" if victory else "defeat", self.player, opponent, st, tt, initial_forces, final_forces), territory=[st, tt], player=[self.player.name, tt.owner.name])
                    self.create_game_state(self.world)
                    return ("attack", False, self.game_state), None, False, {}
                elif action[0] == 3:
                    self.message_event('freemove action taken')
                    self.delay_wrapper(MEDIUM_DELAY)

                    src, target, count = action[1], action[2], action[3] 
                    st = self.world.territory(Action_map[src])
                    tt = self.world.territory(Action_map[target])
                    f = int(count)
                    if st is None:
                        self.aiwarn("freemove invalid src %s", src)
                        self.message_event(f"freemove invalid src None")
                        self.delay_wrapper(LONG_DELAY)
                        return ("freemove", False, self.game_state), None, True, {}
                    if tt is None:
                        self.aiwarn("freemove invalid target None")
                        self.message_event(f"freemove invalid target None")
                        self.delay_wrapper(LONG_DELAY)
                        return ("freemove", False, self.game_state), None, True, {}
                    if st.owner != self.player:
                        self.aiwarn("freemove unowned src %s", st.name)
                        self.message_event(f"freemove unowned src {st.name}")
                        self.delay_wrapper(LONG_DELAY)
                        return ("freemove", False, self.game_state), None, True, {}
                    if tt.owner != self.player:
                        self.aiwarn("freemove unowned target %s", tt.name)
                        self.message_event(f"freemove unowned target {tt.name}")
                        self.delay_wrapper(LONG_DELAY)
                        return ("freemove", False, self.game_state), None, True, {}
                    if not 0 <= f:
                        self.aiwarn("freemove invalid count %s", f)
                        self.message_event(f"freemove invalid count {f}")
                        self.delay_wrapper(LONG_DELAY)
                        return ("attack", False, self.game_state), None, True, {}
                    if self.no_player_path(self.player, st, tt):
                        self.aiwarn("freemove territories not connected")
                        self.message_event(f"freemove territories not connected: {st.name}, {tt.name}")
                        self.delay_wrapper(LONG_DELAY)
                        return ("freemove", False, self.game_state), None, True, {}
                    else: #valid start and end 
                        if f >= st.forces:
                            count = st.forces - 1
                        st.forces -= count
                        tt.forces += count
                        self.agent_turn_number += 1
                        self.event(("move", self.player, st, tt, count), territory=[st, tt], player=[self.player.name])
                        self.turn += 1
                        self.phase = 'reinforce'
                        self.troops_remaining = self.player.reinforcements #have to set before we transition to reinforcement so troops are included in state
                        self.player.remaining_troops = self.player.reinforcements
                        self.create_game_state(self.world)
                        self.delay_wrapper(MEDIUM_DELAY)

        if self.player.ai != None: #will only occur after the reinforcement phase has completed
            #UPDATE REMAINING TROOPS FOR THE AGENT PLAYER AT THE END OF THE TURN
            while self.player.ai != None: #continue taking turns until turn gets back to the player
                self.play()
                agent = self.players[self.agent_name]
                self.turn += 1
                #uncomment this section if we want the game to keep playing after the agent loses
                # elif self.live_players == 1: #or there is only one player left alive
                #     self.finished = True
                #     winner = [p for p in self.players.values() if p.alive][0]
                #     self.event(("victory", winner))
                #     for p in self.players.values():
                #         if p.ai is not None:
                #             p.ai.end()
                #     reward = 100 if winner.ai is None else -100
                #     #this should never be reached, since the game will end when the agent is eliminated
                #     #leaving in just in case
                #     self.create_game_state(self.world)
                #     return ("win" if reward == 100 else "loss", False, self.game_state), reward, True, {}
                self.create_game_state(self.world)
                #update the number of reinforcements that the player will get on their turn at the end of each opponent's turn
                agent.remaining_troops = agent.reinforcements 
                self.troops_remaining = agent.reinforcements

                self.live_players = len([p for p in self.players.values() if p.alive])

                agent = self.players[self.agent_name]
                if not agent.alive:
                    self.message_event(f"Agent lost after {self.turn} turns")
                    self.delay_wrapper(LONG_DELAY)
                    self.create_game_state(self.world)
                    return ("loss", False, self.game_state), None, True, {}
                elif self.live_players == 1:
                    self.finished = True
                    winner = [p for p in self.players.values() if p.alive][0]
                    self.event(("victory", winner))
                    for p in self.players.values():
                        if p.ai is not None:
                            p.ai.end()
                    reward = 100 if winner.ai is None else -100
                    self.create_game_state(self.world)
                    self.message_event(f"Agent won after {self.turn} turns")
                    self.delay_wrapper(LONG_DELAY)
                    return ("win" if reward == 100 else "loss", False, self.game_state), None, True, {}
        #occurs after all AIs have taken their turns without ending the game
        #turn counter should be reset to player
        #the last action the player took was freemove, so that's listed as the phase
        self.create_game_state(self.world)
        return ("freemove", True, self.game_state), None, False, {}

    def play(self):
        '''
        Simulate game for AI agents
        Loop through reinforce, attack and move phases and execute action based on the heuristic for the agent.
        :return:
        '''
        if self.player.ai is not None:
            self.message_event(f"Playing opponent turn: {self.player}")
            self.delay_wrapper(MEDIUM_DELAY)
            if self.player.alive:
                choices = self.player.ai.reinforce(self.player.reinforcements)
                assert sum(choices.values()) == self.player.reinforcements
                for tt, ff in choices.items():
                    t = self.world.territory(tt)
                    f = int(ff)
                    if t is None:
                        self.aiwarn("reinforce invalid territory %s", tt)
                        continue
                    if t.owner != self.player:
                        self.aiwarn("reinforce unowned territory %s", t.name)
                        continue
                    if f < 0:
                        self.aiwarn("reinforce invalid count %s", f)
                        continue
                    t.forces += f
                    self.event(("reinforce", self.player, t, f), territory=[t], player=[self.player.name])
                
                for src, target, attack, move in self.player.ai.attack():
                    st = self.world.territory(src)
                    tt = self.world.territory(target)
                    if st is None:
                        self.aiwarn("attack invalid src %s", src)
                        continue
                    if tt is None:
                        self.aiwarn("attack invalid target %s", target)
                        continue
                    if st.owner != self.player:
                        self.aiwarn("attack unowned src %s", st.name)
                        continue
                    if tt.owner == self.player:
                        self.aiwarn("attack owned target %s", tt.name)
                        continue
                    if tt not in st.connect:
                        self.aiwarn("attack unconnected %s %s", st.name, tt.name)
                        continue
                    if st.forces == 1:
                        self.aiwarn("Invalid attack; only one troop on %s", st.name)
                        continue
                    if tt.forces == 0 and st.forces == 1:
                        self.aiwarn("Not enough troops to conquer %s from %s", tt.name, st.name)
                        continue
                    initial_forces = (st.forces, tt.forces)
                    if tt.forces == 0:
                        victory = self.combat(st, tt, None, move)
                        final_forces = (st.forces, tt.forces)    
                        self.event(("conquer" if victory else "defeat", self.player, 'Empty', st, tt, initial_forces, final_forces), territory=[st, tt], player=[self.player.name, 'Empty'])
                    else:
                        opponent = tt.owner
                        victory = self.combat(st, tt, None, move)
                        final_forces = (st.forces, tt.forces)
                        self.event(("conquer" if victory else "defeat", self.player, opponent, st, tt, initial_forces, final_forces), territory=[st, tt], player=[self.player.name, tt.owner.name])
                freemove = self.player.ai.freemove()
                if freemove:
                    src, target, count = freemove
                    st = self.world.territory(src)
                    tt = self.world.territory(target)
                    f = int(count)
                    valid = True
                    if st is None:
                        self.aiwarn("freemove invalid src %s", src)
                        valid = False
                    if tt is None:
                        self.aiwarn("freemove invalid target %s", target)
                        valid = False
                    if st.owner != self.player:
                        self.aiwarn("freemove unowned src %s", st.name)
                        valid = False
                    if tt.owner != self.player:
                        self.aiwarn("freemove unowned target %s", tt.name)
                        valid = False
                    if not 0 <= f < st.forces:
                        self.aiwarn("freemove invalid count %s", f)
                        valid = False
                    if valid:
                        st.forces -= count
                        tt.forces += count
                        self.event(("move", self.player, st, tt, count), territory=[st, tt], player=[self.player.name])
                self.create_game_state(self.world)
                live_players = len([p for p in self.players.values() if p.alive])

    def player_combat(self, src, target, f_move):
        '''
        This function executes player combat between an attacking and defending territory once an attack has been declared.
        The entire attack is split up into 3v2 battles with the attacking player being given 3 troops
        During combat each player rolls a number of die equivalent to the number of troops involved in each attack
        These dice rolls are sorted in decreasing order, and each pair of attacking and defending rolls are compared.
        If the attacker has a higher roll, the defending country loses a troop.
        If not, the attacking territory loses a troop.
        This combat is repeated until the attacker has exhausted all but one of their troops or the defending territory has no troops remaining.
        Following combat, if the attacking player won, they can move 'f_move' troops to the conquered territory.
        If they have less than 'f_move' troops remaining they move as many troops as they can (all but one).
        :param src: Source country to attack from
        :param target: Target country for the attack
        :param f_move: Number of troops to move following the attack
        :return:
        '''
        n_atk = src.forces
        n_def = target.forces

        while n_atk > 1 and n_def > 0:
            atk_dice = min(n_atk - 1, 3)
            atk_roll = sorted([random.randint(1, 6) for i in range(atk_dice)], reverse=True)
            def_dice = min(n_def, 2)
            def_roll = sorted([random.randint(1, 6) for i in range(def_dice)], reverse=True)

            for a, d in zip(atk_roll, def_roll):
                if a > d:
                    n_def -= 1
                else:
                    n_atk -= 1
        
        if n_def == 0:
            if f_move == None: 
                move = n_atk - 1
            else:
                move = f_move
            min_move = min(n_atk - 1, 1)
            max_move = n_atk - 1
            if move < min_move:
                self.aiwarn("combat invalid move request %s (%s-%s)", move, min_move, max_move)
                move = min_move
            if move > max_move:
                self.aiwarn("combat invalid move request %s (%s-%s)", move, min_move, max_move)
                move = max_move
            src.forces = n_atk - move
            target.forces = move
            target.owner = src.owner
            return True
        else:
            src.forces = n_atk
            target.forces = n_def
            return False

    #for AI. We pass none for f_atk to keep it same as player combat. This was giving unfair advantage to AI
    def combat(self, src, target, f_atk, f_move):
        n_atk = src.forces
        n_def = target.forces

        if f_atk is None:
            f_atk = lambda a, d: True
        if f_move is None:
            f_move = lambda a: a - 1
        while n_atk > 1 and n_def > 0 and f_atk(n_atk, n_def):
            atk_dice = min(n_atk - 1, 3)
            atk_roll = sorted([random.randint(1, 6) for i in range(atk_dice)], reverse=True)
            def_dice = min(n_def, 2)
            def_roll = sorted([random.randint(1, 6) for i in range(def_dice)], reverse=True)

            for a, d in zip(atk_roll, def_roll):
                if a > d:
                    n_def -= 1
                else:
                    n_atk -= 1

        if n_def == 0:
            move = f_move(n_atk)
            min_move = min(n_atk - 1, 3)
            max_move = n_atk - 1
            if move < min_move:
                self.aiwarn("combat invalid move request %s (%s-%s)", move, min_move, max_move)
                move = min_move
            if move > max_move:
                self.aiwarn("combat invalid move request %s (%s-%s)", move, min_move, max_move)
                move = max_move
            src.forces = n_atk - move
            target.forces = move
            target.owner = src.owner
            return True
        else:
            src.forces = n_atk
            target.forces = n_def
            return False

    def initial_placement(self):
        '''
        Draft troops for the two opposing players at the start of the game.
        If the agents are of the "FixedDrafting" type, then the agents will draft troops based on the specified map
            The map is specified as one of the maps within our Risk Language dataset
        If the agents are not of the "FixedDrafting" type, then the agents will either be randomly assigned troops or will be
        allowed to select their troops based on their AI heuristic.
        :return: None
        '''
        self.message_event("In initial_placement function")
        if self.options['state'] == 0:
            empty = list(self.world.territories.values())
            available = 14
            remaining = {p: available for p in self.players}
            AI = [FixedDraftingRandomAI, P1, P2, P3, P4, P5, P6, P7, P8]

            if type(self.players[list(self.players.keys())[0]].ai) in AI:
                self.message_event('Using fixed drafting AI')
                self.delay_wrapper(MEDIUM_DELAY)
                while remaining:
                    choice = self.player.ai.initial_placement(empty, remaining[self.player.name])
                    t = self.world.territory(choice)
                    t.forces += 1
                    t.owner = self.player
                    remaining[self.player.name] -= 1
                    self.event(("claim", self.player, t), territory=[t], player=[self.player.name])
                    if t in empty:
                        empty.remove(t)
                    if remaining[self.player.name] == 0:
                        remaining.pop(self.player.name)
                    self.turn += 1
            else:
                self.message_event('Using normal AI')
                self.delay_wrapper(MEDIUM_DELAY)

                if self.options['deal']:
                    # Assign troops randomly
                    #Incomplete
                    self.message_event("Dealing")
                    random.shuffle(empty)
                    while empty and (len(list(self.players['BRAVO'].territories)) < 7 or len(list(self.players['CHARLIE'].territories)) < 7):
                        t = empty.pop()
                        t.forces += 1
                        remaining[self.player.name] -= 1
                        t.owner = self.player
                        self.event(("deal", self.player, t), territory=[t], player=[self.player.name])
                        self.turn += 1
                else:
                    # Allow agents to use their heuristic to place their troops
                    self.players['BRAVO'].flag = False
                    self.players['CHARLIE'].flag = False                
                    self.message_event("Not Dealing")
                    
                    while empty:
                        # LOG.info(len(self.players['CHARLIE'].territories))
                        # self.aiwarn("reinforce invalid count %s", f)
                        if self.players['BRAVO'].flag and self.players['CHARLIE'].flag:
                            break
                        if self.player.flag == True:
                            self.turn += 1
                            continue
                        choice = self.player.ai.initial_placement(empty, remaining[self.player.name])
                        self.message_event(f"Choice {choice}")
                        if choice:
                            t = self.world.territory(choice)
                            if t is None:
                                self.aiwarn("invalid territory choice %s", choice)
                                self.turn += 1
                                continue
                            if t not in empty:
                                self.aiwarn("initial invalid empty territory %s", t.name)
                                self.turn += 1
                                continue
                            t.forces += 1
                            t.owner = self.player
                            remaining[self.player.name] -= 1
                            empty.remove(t)
                            self.event(("claim", self.player, t), territory=[t], player=[self.player.name])
                            if len(list(self.player.territories)) == 7:
                                self.player.flag = True
                            self.turn += 1
                        else:
                            #handles the case where one player selects None as their choice

                            # checks that the next player has at least 1 territory
                            #if they do, stop gaining new territories
                            #if they don't let them try to select again
                            # effect is that both players will on average, select far fewer than 7 territories

                            #uncommnent this section to let AIs select under 7 territories
                            # self.message_event("We are in the weird if statement")
                            if remaining[self.player.name] == 14:                     
                                self.turn += 1
                                continue
                            else:
                                self.player.flag = True
                                self.turn += 1

                            #uncomment this section to let AIs pick up to 7 territories
                            # self.turn += 1
                            # continue
                while sum(remaining.values()) > 0:
                    #check that the current player still has troops left
                    if remaining[self.player.name] > 0:
                        # choice = self.player.ai.initial_placement(None, remaining[self.player.name])
                        # Add AI drafting function
                        #select random territory from the territories that the ai controls
                        choice = random.choice(list(self.player.territories))
                        t = self.world.territory(choice)
                        # self.message_event(f"{self.player.name} reinforces {t}")
                        #I don't think that it is possible for the agent to hit 
                        if t is None:
                            self.aiwarn("initial invalid territory %s", choice)
                            self.turn += 1
                            continue
                        if t.owner != self.player:
                            self.aiwarn("initial unowned territory %s", t.name)
                            self.turn += 1
                            continue
                        t.forces += 1
                        remaining[self.player.name] -= 1
                        self.event(("reinforce", self.player, t, 1), territory=[t], player=[self.player.name])
                    self.turn += 1

    def no_player_path(self, player, st, tt):
        '''
        check whether which territories can be reached from a start territory controlled by player
        used to check freemove legality
        :param player: player who is attempting freemove
        :param st: Source territory
        :param tt: Target territory
        :return: True/False
        '''
        if st not in player.territories or tt not in player.territories:
            return True


        player_territory_names = [t.name for t in list(player.territories)]

        t_queue = self.connect[st.name].copy()
        t_accessible = [st.name]
        while t_queue:
            t = t_queue.pop(0)
            if t in player_territory_names:
                t_accessible.append(t)
                for pt in self.connect[t]:
                    if pt not in t_accessible and pt not in t_queue:
                        t_queue.append(pt)

        if tt.name in t_accessible:
            return False
        else:
            return True
            