import dataoperation as do
from MicroinstallationOptimization import *

class HouseholdAgent(object):
    def __init__(self, id, folder_with_files = "files/agents/"):
        self.id = id
        self.config_path = folder_with_files + id + "/config.txt"
        
        self.optimizer = MicroinstallationOptimizer(self.config_path)
        self.change_trade_bounds()
        
        self.needs = Needs()
        self.offers = Offers()

    def optimize(self):
        self.optimizer.calculate()
        
        self.needs.m_u.power = self.optimizer.results[:, Variable.m_u]
        self.needs.m_es.power = self.optimizer.results[:, Variable.m_es]

        self.offers.res_m.power = self.optimizer.results[:, Variable.res_m]
        self.offers.es_m.power = self.optimizer.results[:, Variable.es_m]

        #TODO: mechanizm ustalania cen dla ofert

    def set_prediction_horizon(self, prediction_horizon):
        if prediction_horizon <= len(self.optimizer.model.demand):
            self.optimizer.model.prediction_horizon = prediction_horizon
        else:
            print("Horyzont predykcji nie może przekraczać okresu, na który dokonano predykcji danych!")

    def change_trade_bounds(self, bounds=[]):
        do.save_to_file(self.optimizer.model.paths['trade_bounds'], bounds)


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
        



