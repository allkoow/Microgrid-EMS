import dataoperation as do
from Optimizer import Optimizer

class HouseholdAgent(object):
    def __init__(self, config_path = "files/config.txt"):
        self.config_path = config_path
        self.optimizer = Optimizer(self.config_path)
        
        self.needs = Needs()
        self.offers = Offers()

    def optimize(self):
        self.optimizer.calculate()
        
        self.needs.m_u.power = self.optimizer.results[:, self.optimizer.Variable.m_u]
        self.needs.m_es.power = self.optimizer.results[:, self.optimizer.Variable.m_es]

        self.offers.res_m.power = self.optimizer.results[:, self.optimizer.Variable.res_m]
        self.offers.es_m.power = self.optimizer.results[:, self.optimizer.Variable.es_m]

        #TODO: mechanizm ustalania cen dla ofert


class TradeInfo(object):
    def __init__(self):
        self.power = []
        self.price = []

class Needs(object):
    def __init__(self):
        self.m_u = TradeInfo()
        self.m_es = TradeInfo()

class Offers(object):
    def __init__(self):
        self.res_m = TradeInfo()
        self.es_m = TradeInfo()
        



