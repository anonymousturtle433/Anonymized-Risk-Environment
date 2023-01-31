import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor

class TestRiskAgent(nn.Module):
    def __init__(self,
                 num_phases: int,
                 num_countries: int,
                 max_troops: int,
                 state_size: int):
        super().__init__()

        self.num_phases = num_phases
        self.num_countries = num_countries
        self.max_troops = max_troops
        self.state_size = state_size
        self.output_size = num_phases*num_countries*num_countries*max_troops

        self.linear = nn.Linear(self.state_size, self.output_size)


    def forward(self,
                state: Tensor) -> Tensor:
        outputs = self.linear(state)
        return F.softmax(outputs, dim=0)