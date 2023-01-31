import logging
LOG = logging.getLogger("pyrisk")

def basic(obs, prev_obs, done, reward_config=None):
    phase, phase_done, full_state = obs
    territory_states = full_state[0]
    agent_name = 'ALPHA'
    agents_alive = []
    agent_won = False
    for i, territory in enumerate(territory_states):
        if territory_states[territory]['owner'] not in agents_alive and territory_states[territory]['owner'] != 'None':
            agents_alive.append(territory_states[territory]['owner'])
    if done and len(agents_alive) == 1 and agent_name in agents_alive:
        agent_won = True
    if phase == 'opp move': #do not give rewards for opponent actions!
        return 0
    if agent_won:
        LOG.info("Agent won. Awarding 100")
        return 100
    elif done: #game is done but agent did not win
        LOG.info("Agent did not win. Awarding -100")
        return -100
    else : #all other cases 0
        LOG.info("No rewards")
        return 0

def survival(obs,prev_obs, done, reward_config=None):
    '''
    This reward function provides a reward based on how many turns you survive.
    You are given a +1 reward at the end of each turn, and a -1 reward if you lose
    :param obs: current observation state
    :param prev_obs: prior observations state
    :param done: Whether or not the game is complete
    :return: reward
    '''
    phase, phase_done, full_state = obs
    LOG.info("In survival reward function")
    if phase == 'opp move': #do not give rewards for opponent actions!
        return 0

    if done:
        LOG.info("Agent lost. Awarding -1")
        return -1
    else:
        LOG.info("Agent survived. Awarding +1")
        return 1

def turn_count(obs,prev_obs, done, reward_config=None):
    phase, phase_done, full_state = obs
    if phase == 'opp move': #do not give rewards for opponent actions!
        return 0

    if done:
        return 0
    else:
        return 1

def rules_based(obs, prev_obs, done, reward_config):

    '''
    This reward function provides rewards based on four categories: successful_action, phase_finished, successful_phase_action, game_result
    The agent is provided a +1 reward for every successful action, everytime they successfully complete a phase,
    and when they successfully transition from one phase to the next. The agent also gets a reward for defeating a
    player in the game
    Finally, the agent is provided a +10 reward for winning the game.
    :param obs: current observation state
    :param prev_obs: prior observations state
    :param done: whether or not the game is complete
    :param reward_config: a self defined reward config to hand engineer reward weights
    :return: reward
    '''

    LOG.info("In rules_based reward function")

    phase, phase_done, full_state = obs
    territory_states = full_state[0]
    area_states = full_state[1]
    assorted_info = full_state[2]
    #the last move ended the agents turn, so the current phase is opp move - no reward for agent!
    
    #if agent turn
    if prev_obs != None:
        p_phase, p_phase_done, p_full_state = prev_obs
        p_territory_states = p_full_state[0]
    else:
        p_phase = None
        p_phase_done = None
        p_full_state = None
        p_territory_states = None

    if phase == 'opp move': 
        return 0

    reward_weights = {}
    reward_values = {}

    # get high level environment variables
    agents_alive, p_agents_alive, agent_won = getEnvironmentState(territory_states, prev_obs, done, p_territory_states)

    #high level reward states
    reward_weights['successful_action'] = int(reward_config['successful_action'])
    reward_weights['phase_finished'] = int(reward_config['phase_finished'])
    reward_weights['successful_phase_transition'] = int(reward_config['successful_phase_transition'])
    reward_weights['game_result'] = int(reward_config['game_result'])
    reward_weights['player_defeated'] = int(reward_config['player_defeated'])

    # rule based rewards
    reward_values['successful_action'] = 1 if isSucessfulActionTaken(done, agent_won) else -1
    reward_values['phase_finished'] = 1 if isPhaseFinished(phase_done, done) else 0
    reward_values['player_defeated'] = 1 if isPlayerDefeated(done, agent_won, p_agents_alive, agents_alive) else 0
    reward_values['successful_phase_transition'] = 1 if isPhraseTransitionSuccessful(p_phase, phase, done) else 0

    game_result = didAgentWin(done, agent_won)
    if game_result is None:
        reward_weights['game_result'] = 0
    else:
        reward_weights['game_result'] = 1 if game_result else -1

    #calculate reward from values and weights
    reward = 0
    for reward_name in reward_values.keys():
        reward += reward_values[reward_name]*reward_weights[reward_name]
    LOG.info(reward)
    return reward

def rules_based_legal_actions(obs, prev_obs, done, reward_config):
    '''
    This reward function is similar to rules based reward function. The only difference is that we dont provide
    additional rewards for switching to next phase as agent is allowed to take legal actions only.
    :param obs: current observation state
    :param prev_obs: prior observations state
    :param done: Whether or not the game is complete
    :param reward_config: a self defined reward config to hand engineer reward weights
    :return: reward
    '''

    phase, phase_done, full_state = obs
    territory_states = full_state[0]
    area_states = full_state[1]
    assorted_info = full_state[2]
    # the last move ended the agents turn, so the current phase is opp move - no reward for agent!

    # if agent turn
    if prev_obs != None:
        p_phase, p_phase_done, p_full_state = prev_obs
        p_territory_states = p_full_state[0]
    else:
        p_phase = None
        p_phase_done = None
        p_full_state = None
        p_territory_states = None

    if phase == 'opp move':
        return 0

    reward_weights = {}
    reward_values = {}

    # high level reward states
    reward_weights['successful_action'] = reward_config['successful_action']
    reward_weights['phase_finished'] = reward_config['phase_finished']
    reward_weights['game_result'] = reward_config['game_result']
    reward_weights['player_defeated'] = reward_config['player_defeated']

    # get high level environment variables
    agents_alive, p_agents_alive, agent_won = getEnvironmentState(territory_states, prev_obs, done, p_territory_states)

    # rule based rewards
    reward_values['successful_action'] = 1 if isSucessfulActionTaken(done,agent_won ) else -1
    reward_values['phase_finished'] = 1 if isPhaseFinished(phase_done,done ) else 0
    reward_values['player_defeated'] = 1 if isPlayerDefeated(done,agent_won,p_agents_alive,agents_alive) else 0

    game_result = didAgentWin(done, agent_won)
    if game_result is None:
        reward_weights['game_result'] = 0
    else:
        reward_weights['game_result'] = 1 if game_result else -1

    # calculate reward from values and weights
    reward = 0
    for reward_name in reward_values.keys():
        reward += reward_values[reward_name] * reward_weights[reward_name]
    LOG.info(reward)
    return reward

def getEnvironmentState(territory_states,prev_obs, done, p_territory_states) :
    """
    Helper function to extract high level information regarding the environment like number of agents is alive,
    number of agents alive in last observation and if the agent won the game.
    :param territory_states: Current state of all territories on map
    :param prev_obs: Observations from previous state
    :return: agents_alive, p_agents_alive, agent_won
    """
    agents_alive = []
    p_agents_alive = []
    agent_won = False
    agent_name = 'ALPHA'

    for i, territory in enumerate(territory_states):
        if territory_states[territory]['owner'] not in agents_alive and territory_states[territory]['owner'] != 'None':
            agents_alive.append(territory_states[territory]['owner'])

    if prev_obs is not None:
        for i, territory in enumerate(p_territory_states):
            if p_territory_states[territory]['owner'] not in p_agents_alive and \
                    p_territory_states[territory]['owner'] != 'None':
                p_agents_alive.append(p_territory_states[territory]['owner'])

    if done and len(agents_alive) == 1 and agent_name in agents_alive:
        agent_won = True

    return  agents_alive, p_agents_alive, agent_won

def isPlayerDefeated(done,agent_won,p_agents_alive,agents_alive):
    """
    Helper function to check if a SINGLE player got defeated by the agent
    :param done: Variable to check if game is done
    :param agent_won: Variable to check if agent won
    :param p_agents_alive: Variable to keep agents alive in last observation
    :param agents_alive: Variable to keep agents alive in current observation
    :return: Bool value
    """
    if not done or not agent_won: # Awarding points for defeating a single player. Separate points are provided
                                  # for winning the whole game
        if len(p_agents_alive) > len(agents_alive):
            return True
    return False

def isSucessfulActionTaken(done,agent_won ):
    """
    Helper function to check if a successful action was taken
    :param done: Variable to check if game is done
    :param agent_won: Variable to check if agent won
    :return: Bool value
    """
    if not done or agent_won:  # if game not over or agent ended game
        return True
    return False

def isPhaseFinished(phase_done, done):
    """
    Helper function to check if a phase is finished
    :param phase_done: Variable to check if a phase is done
    :param done: Variable to check if game is done
    :return: Bool Value
    """
    if phase_done and not done:
        return True
    return False

def isPhraseTransitionSuccessful(p_phase, phase, done):
    """
    Helper function to check if a phase transition was successful (eg: Reinforce to Attack)
    :param p_phase:  Variable to keep previous phase
    :param phase:  Variable to keep current phase
    :param done: Variable to check if game is done
    :return: Bool Value
    """
    if p_phase != phase and not done:
        LOG.info("Successful action in a phase. Awarding +1")
        return True

def didAgentWin(done, agent_won):
    """
    Helper function to check if the agent won the game
    :param done: Variable to check if game is done
    :param agent_won: Variable to check if agent won
    :return:
    """
    if done:
        if agent_won:
            LOG.info("Agent won. Awarding +10")
            return True  # agent won!
        else:
            LOG.info("Agent lost. Awarding -10")
            return False
    return None

"""
This reward function is not tested and we are not using it currently to train our model
"""
def phase_only(obs, prev_obs, done):
    phase, phase_done, full_state = obs
    territory_states = full_state[0]
    area_states = full_state[1]
    assorted_info = full_state[2]
    #the last move ended the agents turn, so the current phase is opp move - no reward for agent!
    
    #if agent turn
    if prev_obs != None:
        p_phase, p_phase_done, p_full_state = prev_obs
    else:
        p_phase = None
        p_phase_done = None
        p_full_state = None

    if phase == 'opp move': 
        return 0

    agent_name = 'ALPHA'

    reward_weights = {}
    reward_values = {}

    #rule based rewards
    reward_values['phase_finished'] = 0.
    reward_values['successful_phase_action'] = 0. #provide additional bonus for taking at least 1 correct action in each phase
    reward_weights['phase_finished'] = 1
    reward_weights['successful_phase_action'] = 1

    #calculate high level rewards
    if phase_done and not done:
        reward_values['phase_finished'] = 1

    if p_phase != phase and not done:
        reward_values['successful_phase_action'] = 1

    #calculate reward from values and weights
    reward = 0
    for reward_name in reward_values.keys():
        reward += reward_values[reward_name]*reward_weights[reward_name]
    return reward

"""
This reward function is not tested and we are not using it currently to train our model
"""
def medium_loss(obs,prev_obs, done):
    phase, phase_done, full_state = obs
    if phase == 'opp move': #do not give rewards for opponent actions!
        return 0

    if done:
        return -30
    else:
        return 1

"""
This reward function is not tested and we are not using it currently to train our model
"""
def overkill(obs, prev_obs, done):
    ####NOT CURRENTLY DEBUGGED!!
    phase, phase_done, full_state = obs
    territory_states = full_state[0]
    area_states = full_state[1]
    assorted_info = full_state[2]


    if phase == 'opp move': #do not give rewards for opponent actions!
        return 0

    if prev_obs != None:
        p_phase, p_phase_done, p_full_state = prev_obs
    else:
        p_phase = None
        p_phase_done = None
        p_full_state = None

    agent_name = 'ALPHA'

    reward_weights = {}
    reward_values = {}

    #direct state based rewards
    reward_values['areas_controlled'] = 0.
    reward_values['territories_controlled'] = 0.
    reward_values['troops_deployed'] = 0.
    reward_values['opponent_areas_controlled'] = 0.
    reward_values['opponent_territories_controlled'] = 0.
    reward_values['opponent_troops'] = 0.

    #change based rewards
    reward_values['enemies_defeated'] = 0.
    reward_values['troop_change'] = 0.
    reward_values['enemy_areas_disrupted'] = 0.
    reward_values['territory_change'] = 0.
    reward_values['area_change'] = 0.

    #high level rewards
    reward_values['successful_action'] = 0  
    reward_values['phase_finished'] = 0.
    reward_values['successful_phase_action'] = 0. #provide additional bonus for taking at least 1 correct action in each phase
    # reward_values['round_finished'] = 0. #not calculable with current set up
    reward_values['opponents_alive'] = 0.
    reward_values['opponent_defeated'] = 0.
    reward_values['game_result'] = 0.


    #direct state based reward weights
    reward_weights['areas_controlled'] = 1
    reward_weights['territories_controlled'] = 0.1
    reward_weights['troops_deployed'] = 0.1
    reward_weights['opponent_areas_controlled'] = -1*reward_weights['areas_controlled']/2
    reward_weights['opponent_territories_controlled'] = -1*reward_weights['territories_controlled']/2
    reward_weights['opponent_troops'] = -1*reward_weights['troops_deployed']/2 #half as important as own troops since twice as many opponents

    #change based reward states
    reward_weights['enemies_defeated'] = 0.05
    reward_weights['troop_change'] = 0.1
    reward_weights['enemy_areas_disrupted'] = 1
    reward_weights['territory_change'] = 0.1
    reward_weights['area_change'] = 1
    if phase == 'drafting': #use differnt weights for drafting
        #agent has no control over oppoenent placements, so don't consider for reward
        reward_weights['opponent_areas_controlled'] = 0
        reward_weights['opponent_territories_controlled'] = 0
        reward_weights['opponent_troops'] = 0
        #don't give rewards for things previously placed in the drafting phase, only new things
        reward_weights['areas_controlled'] = 0
        reward_weights['territories_controlled'] = 0
        reward_weights['troops_deployed'] = 0

        # reward_weights['territory_change'] = 1
        # reward_weights['troop_change'] = 0.1

    #high level reward states
    reward_weights['successful_action'] = 1
    reward_weights['phase_finished'] = 1
    reward_weights['successful_phase_action'] = 1
    # reward_weights['round_finished'] = 1 #not calculable with current set up
    reward_weights['opponents_alive'] = 0 #no longer using, since very difficult for agent to control
    reward_weights['opponent_defeated'] = 1 #easier for agent to control
    reward_weights['game_result'] = 5

    #state reward calculations
    num_player_troops = 0
    opponent_troops = 0
    num_player_territories = 0
    areas_controlled = 0
    opponent_areas_controlled = 0
    opponent_territories = 0
    for i, territory in enumerate(territory_states):
        if territory_states[territory]['owner'] == agent_name:
            num_player_troops += territory_states[territory]['troops']
            num_player_territories += 1
        elif territory_states[territory]['owner'] != 'None':
            opponent_troops += territory_states[territory]['troops']
            opponent_territories += 1

    for i, area in enumerate(area_states):
        if area_states[area]['owner'] == agent_name:
            areas_controlled += 1
        elif area_states[area]['owner'] != 'None':
            opponent_areas_controlled += 1

    reward_values['areas_controlled'] = areas_controlled
    reward_values['territories_controlled'] = num_player_territories
    reward_values['troops_deployed'] = num_player_troops
    reward_values['opponent_areas_controlled'] = opponent_areas_controlled
    reward_values['opponent_territories_controlled'] = opponent_territories
    reward_values['opponent_troops'] = opponent_troops

    #prev obs is not from previous turn 
    #calculate change rewards
    if not (p_phase == 'freemove' and phase == 'reinforce') and (prev_obs != None):
        territory_states = p_full_state[0]
        area_states = p_full_state[1]
        assorted_info = p_full_state[2]

        p_num_player_troops = 0
        p_opponent_troops = 0
        p_num_player_territories = 0
        p_areas_controlled = 0
        p_opponent_areas_controlled = 0
        p_opponent_territories = 0
        for i, territory in enumerate(territory_states):
            if territory_states[territory]['owner'] == agent_name:
                p_num_player_troops += territory_states[territory]['troops']
                p_num_player_territories += 1
            elif territory_states[territory]['owner'] != 'None':
                p_opponent_troops += territory_states[territory]['troops']
                p_opponent_territories += 1

        for i, area in enumerate(area_states):
            if area_states[area]['owner'] == agent_name:
                p_areas_controlled += 1
            elif area_states[area]['owner'] != 'None':
                p_opponent_areas_controlled += 1

        reward_values['enemies_defeated'] = p_opponent_troops - opponent_troops #enemy troops can't increase, since this is all on agent turn
        reward_values['troop_change'] = num_player_troops - p_num_player_troops #if number of deployed troops increases, bonus
        reward_values['enemy_areas_disrupted'] = p_opponent_areas_controlled - opponent_areas_controlled #enemy territories can't increase, since this is all on agent turn
        reward_values['territory_change'] = num_player_territories - p_num_player_territories
        reward_values['area_change'] = areas_controlled - p_areas_controlled

    #calculate high level rewards
    agents_alive = {None}
    agent_won = False
    for i, territory in enumerate(territory_states):
        if territory_states[territory]['owner'] not in agents_alive:
            agents_alive.add(territory_states[territory]['owner'])
    if done and len(agents_alive) == 1 and agent_name in agents_alive:
        agent_won = True


    if not done or agent_won: #if game not over or agent ended game
        reward_values['successful_action'] = 1
    else:
        reward_values['successful_action'] = -1

    if phase_done and not done:
        reward_values['phase_finished'] = 1

    if p_phase != phase and not done:
        reward_values['successful_phase_action'] = 1

    # if phase == 'freemove' and phase_done and not done: #not calculable with current set up
    #     reward_values['round_finished'] = 1

    if done and agent_won:
        reward_values['game_result'] = 1 #agent won!

    reward_values['opponents_alive'] = len(agents_alive) - 1

    if prev_obs != None:
        territory_states = p_full_state[0]
        p_agents_alive = {None}
        for i, territory in enumerate(territory_states):
            if territory_states[territory]['owner'] not in p_agents_alive:
                p_agents_alive.add(territory_states[territory]['owner'])
        reward_values['opponents_alive'] = len(p_agents_alive) -  len(agents_alive)

    # else: #this was subtracting -10 from all turns, overwhelming the other rewards
    #     reward_values['game_result'] = -1 #agent lost, but they made it to the end!


    #calculate reward from values and weights
    reward = 0
    for reward_name in reward_values.keys():
        reward += reward_values[reward_name]*reward_weights[reward_name]

    return reward

"""
This reward function is not tested and we are not using it currently to train our model
"""
def drafting_loss(obs,prev_obs, done, reward_config=None):
    phase, phase_done, full_state = obs
    if phase == 'opp move': #do not give rewards for opponent actions!
        return 0

    if done:
        return -14
    else:
        return 1