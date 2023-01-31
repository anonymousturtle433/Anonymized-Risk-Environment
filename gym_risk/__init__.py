from gym.envs.registration import register

name="gym_risk"

register(
    id='Risk-v0',
    entry_point='gym_risk.envs:RiskEnv',
)