import dataoperation as do
import Optimizer as ems
import TradeInfo as trade

class HouseholdAgent(object):
    def __init__(self, config_path = "files/config"):
        self.config_path = config_path
        self.optimizer = ems.Optimizer(self.config_path)
        
        self.needs = trade.Needs()
        self.offers = trade.Offers()

    def optimize(self):
        self.optimizer.calculate()

        



