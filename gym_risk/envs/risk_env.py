import gym
import random
from gym_risk.envs.game import Game
from gym_risk.envs.game.ai.fixed_drafting_random import FixedDraftingRandomAI
from gym_risk.envs.game.ai.user_profiles.P8 import P8
from gym_risk.envs.game.world import CONNECT, Action_map
from gym import spaces
from copy import deepcopy
import numpy as np
import logging
LOG = logging.getLogger("pyrisk")
import time

import gym_risk.envs.reward_functions as rewards_functions

class RiskEnv(gym.Env):
    """
    3 players Risk with two Random AI to compete against
    """
    # todo different AIs to compete against
    # todo env space
    metadata = {'render.modes': ['human']}

    def __init__(self):
        self.game = None
        self.players = []
        self.turn = 0
        self.turn_order = []
        self.action_space = spaces.Box(
            low=np.array([0, 0, 0, 0]), high=np.array([3, 20, 20, 100]), dtype=np.int16)

        self.observation_space = spaces.Box(
            low=np.array([0, 0]), high=np.array([20, 100]), dtype=np.int16)
        self.NUM_TERRITORIES = 21

        self.NUM_AREAS = 5
        self.NUM_ASSORTED_FEATURES = 7
        self.NUM_PHASES = 4
        self.MAX_CONNECTIONS = 4
        self.PLAYER_NAME_TO_CODE = {'None':0,'ALPHA':1, 'BRAVO':2, 'CHARLIE':3}
        self.AGENT_NAME = 'ALPHA'
        self.MAPS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N','O']
        self.MAP = 'RANDOM' #default to random
        self.reward_function_name = 'default'
        self.reward_config = None
        self.prev_obs = None
        self.hard_reset = False #allows games to be created from scratch without options being passed (uses most recent arguments)
        self.game_options = {'curses': False, 
                             'color': True, 
                             'delay': 0.1, 
                             'wait': False, 
                             'deal': False, 
                             'state': 0, 
                             'fast':True, 
                             'screen':None,
                             'messages_on':False,
                             'reward_function_name':'default',
                             'reward_config': None,
                             'hard_reset':False,
                             }
        self.fast = True
        self.round_number_scaling = 25
        self.player_alive_scaling = 3
    def seed(self, seed=None):
        # todo improve with gym.utils.seeding
        random.seed(seed)

    def reset(self, **options):
        # note that this option can only be changed through a call to env or envs.reset. It cannot not be passed in subprocvec envs.step
        #if options are provided, update game options
        for key, value in options.items():
            self.game_options[key] = value
        if 'reward_function_name' in options.keys():
            self.reward_function_name = options['reward_function_name']
        if 'reward_config' in options.keys():
            self.reward_config = options['reward_config']
        if 'hard_reset' in options.keys() and options['hard_reset']: 
            self.hard_reset = True
        if 'map' in options.keys():
            self.MAP = options['map']
        if 'fast' in options.keys():
            self.fast = options['fast']

        if self.game is None or self.hard_reset:
            self.game = Game(**self.game_options)
            self.prev_obs = None
            self.game.add_player("BRAVO", P8, map_name=self.MAP, corresponding_color='grey')
            self.game.add_player("CHARLIE", FixedDraftingRandomAI, map_name=self.MAP, corresponding_color='black')
            self.players.append('ALPHA') #assume that the RL agent will be named alpha
            self.players.append('BRAVO')
            self.players.append('CHARLIE')
            return self.game.init()
        else: # does not currently work with the legal moves agent - messes up the legal move list calculation. For now, use only hard reset for this agent type
            self.prev_obs = None
            return self.game.fast_reset()

    #updated step that works with random resetting in a multiprocessing environment
    def step(self, action, human_drafting=False):
        """
        The step function executes the action within the environment and returns the new state and the reward.
        Parameters
        ----------
        - action : [int, int, int, int]
            A 4x1 array where each index represents the phase, start country, end country and number of troops respectively
        Returns
        -------
        - observation: A tuple consisting of (phase_name, phase_done, game_state)
            phase_name is a string with the name of the current phase of the game, i.e. "drafting"
            phase_done is a boolean indicating whether or not the phase has been completed after taking the action
            game_state is a parameter of the Game() class indicating the game state after taking an action
        - Reward: int
            The reward observed after taking the action. return custom rewards, not from step
        - done: bool
            A boolean indicating whether the game is complete
        - info: dict
            A dictionary with any relevant information regarding completion of an action
            **Should be empty**
        """
        obs, _, done, info = self.game.step(action, human_drafting = human_drafting)
        # note - with this set up, the phase in obs corresponds to the action that was just taken
        # whereas the phase in the prev_obs corresponds to the phase of the prior action
        reward = self._get_reward(obs, self.prev_obs, done, self.reward_config)
        self.prev_obs = deepcopy(obs)
        return obs, reward, done, info

    # todo render, curses and so on
    def render(self, delay=0.1):
        for player_name, player in self.game.players.items():
            logging_string = ''
            if player.alive:
                logging_string += player.name + '\n'
                logging_string += f'\t Territory Count: {player.territory_count}' + '\n'
                territory_string = "\t Territories: "
                for territory in player.territories:
                    territory_string += territory.name + f' ({territory.forces})' + ', '
                logging_string += territory_string[:-2] + '\n'
                area_string = "\t Areas: "
                for area in player.areas:
                    area_string += area.name + ' ,'
                if area_string != "Areas: ":
                    area_string = area_string[:-2]
                else:
                    area_string = area_string + 'None'
                logging_string += area_string + '\n'
                logging_string += f"\t Forces: {player.forces}" + '\n'
                logging_string += f"\t Reinforcements: {player.reinforcements}" + '\n'

                LOG.info(logging_string)

        if not self.fast:
            time.sleep(delay)


    def _get_obs(self, agent, world):
        #Create function to convert the current world state into the observation space.
        return NotImplementedError

    def _get_reward(self, obs, prev_obs, done, reward_config):
        # Calculate reward for the change in the state of the world.
        return getattr(rewards_functions, self.reward_function_name)(obs, prev_obs, done, reward_config)

    #note - observations come from the previous step action. This means that the phase
    #is the phase that the previous action was taken in.

    #assume receiving full observation - currently: (p, phase_done, full_state)
    def obs_to_feat(self, observation, obs_type=None):
        if obs_type == 'one_hot':
            return self.one_hot_obs_to_feat(observation)
        elif obs_type == 'normed_one_hot':
            return self.normed_one_hot_obs_to_feat(observation)
        elif obs_type == 'explicit_normed_one_hot':
            return self.normed_one_hot_explicit_state_obs_to_feat(observation)
        elif obs_type == 'normed_normal':
            return self.normed_normal_obs_to_feat(observation)
        elif obs_type == 'connections':
            return self.connections_one_hot_obs_to_feat(observation)
        else:
            return self.normal_obs_to_feat(observation)

    #Area order: Yellow, Blue, Green, Purple, Red (subject to change)
    #features [0 to NUM_TERRITORIES) = player that controls the territory (0 if none, 1 if agent, 2, 3, ... if other agent)
    #features [NUM_TERRITORIES to NUM_TERRITORIES*2) = number of forces on the corresponding terriory
    #features [NUM_TERRITORIES*2 to NUM_TERRITORIES*2 + NUM_AREAS) = which player controls each continent (0 if none, 1 if agent, etd)
    #feature NUM_TERRITORIES*2 + NUM_AREAS = Total number of player troops
    #feature NUM_TERRITORIES*2 + NUM_AREAS + 1 = Total number of player controlled areas
    #feature NUM_TERRITORIES*2 + NUM_AREAS + 2 = Player drafting troops left (0 except in drafting phase)
    #feature NUM_TERRITORIES*2 + NUM_AREAS + 3 = Player reinforcements troops left (0 except in reinforcement phase)
    #feature NUM_TERRITORIES*2 + NUM_AREAS + 4 = Total number of players alive in the game
    #feature NUM_TERRITORIES*2 + NUM_AREAS + 5 = Round number
    #feature NUM_TERRITORIES*2 + NUM_AREAS + 6 = Is player turn?
    #number of features = 54


    def normal_obs_to_feat(self, observation):
        # self.state_size = self.NUM_TERRITORIES*2 + self.NUM_AREAS + 6
        p, phase_done, full_state = observation
        territory_states = full_state[0]
        area_states = full_state[1]
        assorted_info = full_state[2]
        num_player_troops = 0
        num_player_areas = 0


        state = np.zeros(self.NUM_TERRITORIES*2 + self.NUM_AREAS + self.NUM_ASSORTED_FEATURES)
        for i, territory in enumerate(territory_states):
            if territory_states[territory]['owner'] == 'None':
                state[i] = 0
                state[i + self.NUM_TERRITORIES] = 0
            else:
                state[i] = self.PLAYER_NAME_TO_CODE[territory_states[territory]['owner']]
                state[i + self.NUM_TERRITORIES] = territory_states[territory]['troops']

            if territory_states[territory]['owner'] == self.AGENT_NAME:
                num_player_troops += territory_states[territory]['troops']
            
        for i, area in enumerate(area_states):
            if area_states[area]['owner'] == 'None':
                state[self.NUM_TERRITORIES*2 + i] = 0
            else:
                state[self.NUM_TERRITORIES*2 + i] = self.PLAYER_NAME_TO_CODE[area_states[area]['owner']]

            if area_states[area]['owner'] == self.AGENT_NAME:
                num_player_areas += 1

        
        assorted_info_start = self.NUM_TERRITORIES*2 + self.NUM_AREAS
        state[assorted_info_start]     = num_player_troops
        state[assorted_info_start + 1] = num_player_areas
        
        rein_rem = assorted_info['reinforcements_remaining']
        if  p == 'drafting': #else leave as 0
            state[assorted_info_start + 2] = rein_rem
        if p == 'reinforce': #else leave as 0
            state[assorted_info_start + 3] = rein_rem

        state[assorted_info_start + 4] = assorted_info['num_players_alive']
        state[assorted_info_start + 5] = assorted_info['round_number']
        if p != 'opp move':
            state[assorted_info_start + 6] = 1

        return state
    
    def normed_normal_obs_to_feat(self, observation, norming_constant=14):
        state = self.normal_obs_to_feat(observation)
        assorted_info_start = self.NUM_TERRITORIES*2 + self.NUM_AREAS
        state[assorted_info_start]     = state[assorted_info_start]/norming_constant
        state[assorted_info_start + 1] = state[assorted_info_start + 1]/(norming_constant/3)
        state[assorted_info_start + 2] = state[assorted_info_start + 2]/norming_constant
        state[assorted_info_start + 3] = state[assorted_info_start + 3]/norming_constant
        state[assorted_info_start + 4] = state[assorted_info_start + 4]/self.round_number_scaling
        state[assorted_info_start + 5] = state[assorted_info_start + 5]/self.player_alive_scaling

        return state

    #features  [0 to NUM_TERRITORIES) = 1 if no pplayer control territory, 0 otherwise
    #Area order: Yellow, Blue, Green, Purple, Red (subject to change)
    #features [NUM_TERRITORIES to 2*NUM_TERRITORIES) = 1 if agent controls territory, 0 otherwise
    #features [2*NUM_TERRITORIES to 3*NUM_TERRITORIES) = 1 if oppoenet 1 controls territory, 0 otherwise
    #features [3*NUM_TERRITORIES to 4*NUM_TERRITORIES) = 1 if opponent 2 controlls territory, 0 otherwise
    #features [4*NUM_TERRITORIES to 5*NUM_TERRITORIES) = number of forces on the corresponding terriory
    #features [5*NUM_TERRITORIES to 5*NUM_TERRITORIES + NUM_AREAS) = 1 if no player controls continent
    #features [5*NUM_TERRITORIES + NUM_AREAS to NUM_TERRITORIES*5 + 2*NUM_AREAS) = 1 if agent controls continent
    #features [5*NUM_TERRITORIES + 2*NUM_AREAS to NUM_TERRITORIES*5 + 3*NUM_AREAS) = 1 if oppoenet 1 controls continent
    #features [5*NUM_TERRITORIES + 3*NUM_AREAS to NUM_TERRITORIES*5 + 4*NUM_AREAS) = 1 if oppoenet 2 controls continent
    #Area order: Yellow, Blue, Green, Purple, Red (subject to change)
    #feature NUM_TERRITORIES*5 + 4*NUM_AREAS = Total number of player troops
    #feature NUM_TERRITORIES*5 + 4*NUM_AREAS + 1 = Total number of player controlled areas
    #feature NUM_TERRITORIES*5 + 4*NUM_AREAS + 2 = Player drafting troops left (0 except in drafting phase)
    #feature NUM_TERRITORIES*5 + 4*NUM_AREAS + 3 = Player reinforcements troops left (0 except in reinforcement phase)
    #feature NUM_TERRITORIES*5 + 4*NUM_AREAS + 4 = Total number of players alive in the game
    #feature NUM_TERRITORIES*5 + 4*NUM_AREAS + 5 = Round number
    #feature NUM_TERRITORIES*5 + 4*NUM_AREAS + 6 = Is player turn?
    #number of features = 132
    def one_hot_obs_to_feat(self, observation): 
        # self.state_size = self.NUM_TERRITORIES*5 + 4*self.NUM_AREAS + 6
        p, phase_done, full_state = observation
        territory_states = full_state[0]
        area_states = full_state[1]
        assorted_info = full_state[2]
        num_player_troops = 0
        num_player_areas = 0


        num_territory_vals = len(self.PLAYER_NAME_TO_CODE)
        state = np.zeros(self.NUM_TERRITORIES*5 + self.NUM_AREAS*4 + self.NUM_ASSORTED_FEATURES)
        for i, territory in enumerate(territory_states):
            player_code = self.PLAYER_NAME_TO_CODE[territory_states[territory]['owner']]
            state[i + player_code*self.NUM_TERRITORIES] = 1
            state[i + num_territory_vals*self.NUM_TERRITORIES] = territory_states[territory]['troops']
            if territory_states[territory]['owner'] == self.AGENT_NAME:
                num_player_troops += territory_states[territory]['troops']
            
        for i, area in enumerate(area_states):
            player_code = self.PLAYER_NAME_TO_CODE[area_states[area]['owner']]
            state[i + (num_territory_vals+1)*self.NUM_TERRITORIES + player_code*self.NUM_AREAS] = 1
            if area_states[area]['owner'] == self.AGENT_NAME:
                num_player_areas += 1            

        assorted_info_start = self.NUM_TERRITORIES*5 + 4*self.NUM_AREAS
        state[assorted_info_start]     = num_player_troops
        state[assorted_info_start + 1] = num_player_areas
        
        rein_rem = assorted_info['reinforcements_remaining']
        if  p == 'drafting' and not phase_done: #else leave as 0
            state[assorted_info_start + 2] = rein_rem
        if  (p == 'drafting' and  phase_done) or (p == 'reinforce'and not phase_done) or (p == 'freemove'and phase_done): #else leave as 0
            state[assorted_info_start + 3] = rein_rem

        state[assorted_info_start + 4] = assorted_info['num_players_alive']
        state[assorted_info_start + 5] = assorted_info['round_number']
        if p != 'opp move':
            state[assorted_info_start + 6] = 1

        return state


#features  [0 to NUM_TERRITORIES) = 1 if no pplayer control territory, 0 otherwise
    #features [NUM_TERRITORIES to 2*NUM_TERRITORIES) = 1 if agent controls territory, 0 otherwise
    #features [2*NUM_TERRITORIES to 3*NUM_TERRITORIES) = 1 if oppoenet 1 controls territory, 0 otherwise
    #features [3*NUM_TERRITORIES to 4*NUM_TERRITORIES) = 1 if opponent 2 controlls territory, 0 otherwise
    #features [4*NUM_TERRITORIES to 5*NUM_TERRITORIES) = number of forces on the corresponding terriory
    #features [5*NUM_TERRITORIES to 5*NUM_TERRITORIES + NUM_AREAS) = 1 if no player controls continent
    #features [5*NUM_TERRITORIES + NUM_AREAS to NUM_TERRITORIES*5 + 2*NUM_AREAS) = 1 if agent controls continent
    #features [5*NUM_TERRITORIES + 2*NUM_AREAS to NUM_TERRITORIES*5 + 3*NUM_AREAS) = 1 if oppoenet 1 controls continent
    #features [5*NUM_TERRITORIES + 3*NUM_AREAS to NUM_TERRITORIES*5 + 4*NUM_AREAS) = 1 if oppoenet 2 controls continent
    #Area order: Yellow, Blue, Green, Purple, Red (subject to change)
    #feature NUM_TERRITORIES*5 + 4*NUM_AREAS = Total number of player troops
    #feature NUM_TERRITORIES*5 + 4*NUM_AREAS + 1 = Total number of player controlled areas
    #feature NUM_TERRITORIES*5 + 4*NUM_AREAS + 2 = Player drafting troops left (0 except in drafting phase)
    #feature NUM_TERRITORIES*5 + 4*NUM_AREAS + 3 = Player reinforcements troops left (0 except in reinforcement phase)
    #feature NUM_TERRITORIES*5 + 4*NUM_AREAS + 4 = Total number of players alive in the game
    #feature NUM_TERRITORIES*5 + 4*NUM_AREAS + 5 = Round number
    #feature NUM_TERRITORIES*5 + 4*NUM_AREAS + 6 = Is player turn?
    #number of features = 132

    #same as regular one hot, except all real valued spaces are divided by the norming constant to make them more similar to the 
    #the scale of the one hot vectors.
    def normed_one_hot_obs_to_feat(self, observation, norming_constant=14): 

        num_territory_vals = len(self.PLAYER_NAME_TO_CODE)        
        state = self.one_hot_obs_to_feat(observation)
        assorted_info_start = self.NUM_TERRITORIES*5 + self.NUM_AREAS*4
        state[assorted_info_start]     = state[assorted_info_start]/norming_constant
        state[assorted_info_start + 1] = state[assorted_info_start + 1]/(norming_constant/3)
        state[assorted_info_start + 2] = state[assorted_info_start + 2]/norming_constant
        state[assorted_info_start + 3] = state[assorted_info_start + 3]/norming_constant
        state[assorted_info_start + 4] = state[assorted_info_start + 4]/self.round_number_scaling
        state[assorted_info_start + 5] = state[assorted_info_start + 5]/self.player_alive_scaling

        return state


    #same as normed_one_hot but with explicit one hot vectors for encoding the current game phase, and removing the
    #is player turn feauture (since code changes have rendered that irrelevent)
    #feature NUM_TERRITORIES*5 + 4*NUM_AREAS + 6 =   current phase is draft
    #feature NUM_TERRITORIES*5 + 4*NUM_AREAS + 7 =   current phase is reinforce
    #feature NUM_TERRITORIES*5 + 4*NUM_AREAS + 8 =   current phase is attack
    #freemove phase is not possible since it happens in the same 'phase' as attack
    #opp move doesn't need to be considered since the agent will neever take actions when the state is opponent move
    #full state size = 134

    def normed_one_hot_explicit_state_obs_to_feat(self, observation, norming_constant=14): 
        p, phase_done, full_state = observation
        territory_states = full_state[0]
        area_states = full_state[1]
        assorted_info = full_state[2]
        num_player_troops = 0
        num_player_areas = 0


        num_territory_vals = len(self.PLAYER_NAME_TO_CODE)
        state = np.zeros(self.NUM_TERRITORIES*5 + self.NUM_AREAS*4 + (self.NUM_ASSORTED_FEATURES - 1) + (self.NUM_PHASES - 1))
        intermediate_state = self.normed_one_hot_obs_to_feat(observation, norming_constant)
        state[:self.NUM_TERRITORIES*5 + self.NUM_AREAS*4 + 5] = intermediate_state[:self.NUM_TERRITORIES*5 + self.NUM_AREAS*4 + 5]        
        assorted_info_start = self.NUM_TERRITORIES*5 + self.NUM_AREAS*4
        if p == 'drafting' and not phase_done:
            state[assorted_info_start + 6] = 1
        if  (p == 'drafting' and  phase_done) or (p == 'reinforce'and not phase_done) or (p == 'freemove'and phase_done): #transition from drafting, continue reinforcement, transition from attack
            state[assorted_info_start + 7] = 1
        if (p == 'reinforce'and phase_done) or (p == 'attack'and not phase_done): #transition from reinforcement
            state[assorted_info_start + 8] = 1

        return state

    #features  [0 to NUM_TERRITORIES) = 1 if no pplayer control territory, 0 otherwise
    #features [NUM_TERRITORIES to 2*NUM_TERRITORIES) = 1 if agent controls territory, 0 otherwise
    #features [2*NUM_TERRITORIES to 3*NUM_TERRITORIES) = 1 if oppoenet 1 controls territory, 0 otherwise
    #features [3*NUM_TERRITORIES to 4*NUM_TERRITORIES) = 1 if opponent 2 controlls territory, 0 otherwise
    #features [4*NUM_TERRITORIES to 5*NUM_TERRITORIES) = number of forces on the corresponding terriory
    #features [5*NUM_TERRITORIES to 5*NUM_TERRITORIES + NUM_AREAS) = 1 if no player controls continent
    #features [5*NUM_TERRITORIES + NUM_AREAS to NUM_TERRITORIES*5 + 2*NUM_AREAS) = 1 if agent controls continent
    #features [5*NUM_TERRITORIES + 2*NUM_AREAS to NUM_TERRITORIES*5 + 3*NUM_AREAS) = 1 if oppoenet 1 controls continent
    #features [5*NUM_TERRITORIES + 3*NUM_AREAS to NUM_TERRITORIES*5 + 4*NUM_AREAS) = 1 if oppoenet 2 controls continent
    #Area order: Yellow, Blue, Green, Purple, Red (subject to change)
    #feature NUM_TERRITORIES*5 + 4*NUM_AREAS = Total number of player troops
    #feature NUM_TERRITORIES*5 + 4*NUM_AREAS + 1 = Total number of player controlled areas
    #feature NUM_TERRITORIES*5 + 4*NUM_AREAS + 2 = Player drafting troops left (0 except in drafting phase)
    #feature NUM_TERRITORIES*5 + 4*NUM_AREAS + 3 = Player reinforcements troops left (0 except in reinforcement phase)
    #feature NUM_TERRITORIES*5 + 4*NUM_AREAS + 4 = Total number of players alive in the game
    #feature [NUM_TERRITORIES*5 + 4*NUM_AREAS + 5 to NUM_TERRITORIES*5 + 4*NUM_AREAS + 5 + MAX_CONNECTIONS*NUM_AREAS) = for each territory, can it attack its adjacent territories
    #feature [NUM_TERRITORIES*5 + 4*NUM_AREAS + 5 + MAX_CONNECTIONS*NUM_AREAS to NUM_TERRITORIES*5 + 4*NUM_AREAS + 5 + 2*MAX_CONNECTIONS*NUM_AREAS] for each territory, can it freemove to adjacent territory
    
    #number of features = 298

    #using normed, but not putting it in the name since they're getting unwieldy
    #explicitly providing information about where agent can attack from and to
    #explicitly providing information about where agent can freemove from and to (but only handling direct adjacency right now)
    def connections_one_hot_obs_to_feat(self, observation, norming_constant=14): 
        p, phase_done, full_state = observation
        territory_states = full_state[0]

        state = np.zeros(self.NUM_TERRITORIES*5 + 4*self.NUM_AREAS + 5 + 2*self.MAX_CONNECTIONS*self.NUM_TERRITORIES)        

        intermediate_state = self.normed_one_hot_obs_to_feat(observation, norming_constant)
        state[:self.NUM_TERRITORIES*5 + self.NUM_AREAS*4 + 4] = intermediate_state[:self.NUM_TERRITORIES*5 + self.NUM_AREAS*4 + 4]        
        
        attack_connections_start = self.NUM_TERRITORIES*5 + self.NUM_AREAS*4 + 5
        freemove_connections_start = attack_connections_start + self.NUM_TERRITORIES*self.MAX_CONNECTIONS
        for i in range(self.NUM_TERRITORIES):
            s =  Action_map[i]
            s_connect = CONNECT[s]
            for j,t in enumerate(s_connect):
                agent_in_s = territory_states[s]['owner'] == self.AGENT_NAME
                s_troops = territory_states[s]['troops']
                valid_at = territory_states[t]['owner'] != self.AGENT_NAME
                valid_ft = territory_states[t]['owner'] == self.AGENT_NAME
                if agent_in_s and valid_at and s_troops > 1:#enemy troop or none is in t and player has mor than 1 troop in s
                    state[attack_connections_start + self.MAX_CONNECTIONS*i + j] = 1
                if agent_in_s and valid_ft and s_troops > 1:#enemy troop or none is in t and player has mor than 1 troop in s
                    state[freemove_connections_start + self.MAX_CONNECTIONS*i + j] = 1
        return state

