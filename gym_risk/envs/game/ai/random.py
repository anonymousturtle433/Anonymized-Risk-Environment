from gym_risk.envs.game.ai import AI
import random
import logging

LOG = logging.getLogger("pyrisk")

import collections

class RandomAI(AI):
    """
    RandomAI: Plays a completely random game, randomly choosing and reinforcing
    territories, and attacking wherever it can without any considerations of wisdom.
    """
    def initial_placement(self, empty, remaining):
        if empty:
            p = random.uniform(0,1)
            if p < 0.3:
                return None
            else:
                return random.choice(empty)
        else:
            t = random.choice(list(self.player.territories))
            return t

    def attack(self):
        for t in self.player.territories:
            for a in t.connect:
                if a.owner != self.player:
                    if t.forces > a.forces:
                        yield (t, a, None, None)

    def reinforce(self, available):
        border = [t for t in self.player.territories if t.border]
        if len(border) == 0:
            border = list(self.player.territories)
        result = collections.defaultdict(int)
        for i in range(available):
            t = random.choice(border)
            result[t] += 1
        return result
