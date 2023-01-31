from gym_risk.envs.game.ai import AI
from gym_risk.envs.game.deployment_maps import MAP_PLACEMENTS
import random
import logging

LOG = logging.getLogger("pyrisk")
LOG.setLevel(logging.INFO)

import collections


class P6(AI):

    def __init__(self, player, game, world, **kwargs):
        super().__init__(player, game, world, **kwargs)
        assert 'map_name' in kwargs.keys()
        assert 'corresponding_color' in kwargs.keys()

        self.map_name = kwargs['map_name']
        assert self.map_name in MAP_PLACEMENTS.keys() or self.map_name == 'RANDOM'

        self.kwargs = kwargs
        self.corresponding_color = kwargs['corresponding_color']
        if self.map_name != 'RANDOM':
            self.locations = list(MAP_PLACEMENTS[self.map_name][self.corresponding_color].keys())
            self.reinforcment_amounts = MAP_PLACEMENTS[self.map_name][self.corresponding_color]
            self.reinforcment_amounts = {location: amount - 1 for (location, amount) in
                                         self.reinforcment_amounts.items() if amount - 1 > 0}
        self.player = player

    def __call__(self, player, game, world, **kwargs):
        self.__init__(player, game, world, **kwargs)

    def __repr__(self):
        return "AI;%s" % self.player

    def initial_placement(self, empty, remaining):
        '''
        Place troops using one of the 15 predetermined maps (A - O)
        Each map corresponds to one of the maps used during data collection
        Alternatively, the maps can also be randomly by choosing one the 15 maps at random if the 'map_name' parameter is random.
        This function places one troop on one of the empty territories and returns that territory.
        :param empty: Set of empty territories
        :param remaining: Number of troops that you have left to draft into territories
        :return: drafted territory
        '''
        if self.map_name != 'RANDOM':
            if self.locations:
                t = self.locations[0]
                self.locations = self.locations[1:]
                return t
            elif remaining > 0:  # assumes that each map in MAP_PLACEMENTS specifies 14 troop placements
                t = list(self.reinforcment_amounts.keys())[0]
                t_remaining = self.reinforcment_amounts[t]
                assert t_remaining > 0, f"tried to reinforce {t} too many times"
                self.reinforcment_amounts[t] -= 1
                if self.reinforcment_amounts[t] == 0:
                    self.reinforcment_amounts.pop(t)
                return t
            else:
                assert False, 'Method failed to reinforce correctly'
        else:  # if map name is RANDOM
            # same as the random player, but adding it here to simplify code for initializing a random map
            if empty and remaining > 7:  # since agents start with 14 troops, this is equivalent to choosing 7 unnocupied territories
                return random.choice(empty)
            else:
                t = random.choice(list(self.player.territories))
                return t

    def attack(self):
        territories_owner = {}
        min = 1000
        src = None
        trg = None
        trg_player = None

        for t in self.world.territories.values() :
            if t.owner is not None and t.owner != self.player:
                if t.owner.name in territories_owner.keys() :
                    territories_owner[t.owner.name] += t.forces
                else :
                    territories_owner[t.owner.name] = t.forces

        countries_occupied, continents_occupied_number, continents_occupied  =   self.countries_and_continents_occupied()

        if continents_occupied_number < 2 :
            for t in self.player.territories:
                for a in t.connect:
                    if a.owner != self.player and continents_occupied[a.area.name]>0 :
                        if t.forces > a.forces:
                            yield (t, a, None, None)


        for owner, forces in territories_owner.items():
            if forces<min :
                min = forces
                trg_player = owner

        attack = []
        while True:
            length = len(list(self.player.territories))
            for t in self.player.territories:
                for a in t.connect:
                    if a.owner is None:
                        yield (t, a, None, None)
            if len(list(self.player.territories)) != length:
                continue
            else :
                break

        while True:
            length = len(list(self.player.territories))
            for t in self.player.territories:
                for a in t.connect:
                    if a.owner is not None and a.owner.name == trg_player:
                        yield (t, a, None, None)
            if len(list(self.player.territories)) != length:
                continue
            else:
                break

    def reinforce(self, available):
        border = [t for t in self.player.territories if t.border]
        if len(border) == 0:
            border = list(self.player.territories)
        result = collections.defaultdict(int)
        for i in range(available):
            t = random.choice(border)
            result[t] += 1
        return result

    # sets the map and the troop deployments that the AI will attempt to emulate
    def start(self):
        pass


