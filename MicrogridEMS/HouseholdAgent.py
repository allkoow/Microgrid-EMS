import dataoperation as do
from MicroinstallationOptimization import *

class HouseholdAgent(object):
    def __init__(self, id, folder_with_files = "files/agents/"):
        self.id = id
        self.config_path = folder_with_files + id + "/config.txt"
        self.optimizer = MicroinstallationOptimizer(self.config_path)
        
        self.needs = Needs()
        self.offers = Offers()

    def optimize(self):
        self.optimizer.calculate()
        
        self.needs.m_u.power = self.optimizer.results[:, Variable.m_u]
        self.needs.m_es.power = self.optimizer.results[:, Variable.m_es]

        self.offers.res_m.power = self.optimizer.results[:, Variable.res_m]
        self.offers.es_m.power = self.optimizer.results[:, Variable.es_m]

        #TODO: mechanizm ustalania cen dla ofert

    def set_prediction_horizon(self, hp):
        if hp <= len(self.optimizer.model.demand):
            self.optimizer.model.hp = hp
        else:
            print("Horyzont predykcji nie może przekraczać okresu, na który dokonano predykcji danych!")

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
        



