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
