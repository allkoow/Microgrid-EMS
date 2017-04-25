import dataoperation as do

class HouseholdAgent(object):
    def __init__(self, prediction_horizon = 24):
        self.paths = do.getpaths()
        self.hp = prediction_horizon


