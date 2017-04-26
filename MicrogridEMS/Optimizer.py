import dataoperation as do
from numpy import *
import numpy as np
import scipy.linalg
import scipy.optimize as opt
from enum import IntEnum

class Optimizer(object):

    def __init__(self, config = 'files/config.txt'):
        self.paths = do.getpaths(config)
        
        self.model = dict()
        self.model['demand'] = do.parsefloat(self.paths['demand'])
        self.model['prices'] = do.parsefloat(self.paths['prices'], 3)
        self.model['profile'] = do.parsefloat(self.paths['profile'])
        self.model['restr'] = do.parsefloat(self.paths['restr'])
        self.model['soc'] = do.parsefloat(self.paths['soc'])

        self.hp = 24
        self.step = 60
        self.variables_number = 10
        self.restr_number = 4

        self.optinfo = []
        self.results = np.empty([self.hp, self.variables_number])

    def calculate(self):
        prices = self.model['prices']
        demand = self.model['demand']
        profile = self.model['profile']
        SOC0 = self.model['soc']
        restr = self.model['restr']

        # inicjalizacja macierzy
        objective = np.zeros(self.variables_number * self.hp)
        Aeq = np.zeros((self.restr_number * self.hp, self.variables_number * self.hp))
        beq = np.zeros(self.restr_number * self.hp)
        bn = []
    
        j, i = 0, 0

        for period in range(0, self.hp):
            # 1. koszt energii z sieci dystrybucyjnej
            objective[ix_([j+Variable.g_u,
                          j+Variable.g_es])] = prices[Price.from_grid][period]
            # 2. koszt energii kupionej z mikrosieci
            objective[ix_([j+Variable.m_u,
                           j+Variable.m_es])] = prices[Price.from_microgrid][period]

            # ograniczenia rownosciowe
            # 1. Bilans energetyczny odbioru
            Aeq[i+Equation.load_balance][ix_([j+Variable.res_u,
                                              j+Variable.es_u,
                                              j+Variable.m_u,
                                              j+Variable.g_u])] = 1
            
            beq[i+Equation.load_balance] = demand[period]
            
            # 2. Bilans energetyczny OZE
            Aeq[i+Equation.res_balance][ix_([j+Variable.res_u,
                                            j+Variable.res_es,
                                            j+Variable.res_m])] = 1
            
            beq[i+Equation.res_balance] = profile[period]
            
            # 3. Stan zasobnika
            Aeq[i+Equation.soc][j+Variable.soc] = 1
            
            Aeq[i+Equation.soc][ix_([j+Variable.es_u, 
                                     j+Variable.es_m])] = 1/restr[Restr.capacity]
            
            Aeq[i+Equation.soc][ix_([j+Variable.res_es,
                                     j+Variable.m_es,
                                     j+Variable.g_es])] = -restr[Restr.efficiency_coef]/restr[Restr.capacity]

            if period>0:
                Aeq[i+Equation.soc][j-1] = -restr[Restr.discharge_coef]
            else:
                beq[i+Equation.soc] = SOC0[0]

            # 4. Sprzedaż nadwyżek
            Aeq[i+Equation.surplus_sale][ix_([j+Variable.res_m,
                                              j+Variable.es_m])] = 1
            
            if profile[period]>demand[period]:
                beq[i+Equation.surplus_sale] = profile[period]-demand[period]
            else:
                beq[i+Equation.surplus_sale] = 0

            # Ograniczenia brzegowe
            bn.extend([(0, profile[period]), 
                       (0, profile[period]), 
                       (0, profile[period])])
            
            bn.extend([(0, restr[Restr.max_charge]), 
                       (0, restr[Restr.max_charge])])
            
            bn.extend([(0, demand[period]), 
                       (0, restr[Restr.max_charge]), 
                       (0, demand[period]), 
                       (0, restr[Restr.max_charge])])
            
            bn.append((restr[Restr.min_soc], restr[Restr.max_soc]))

            j += self.variables_number
            i += self.restr_number

            #np.savetxt('optimization_task/Aeq.txt', Aeq,fmt='%.3f', delimiter='\t', newline='\r\n')
            #np.savetxt('optimization_task/beq.txt', beq,fmt='%.3f', delimiter=' ',  newline='\r\n')
    
        self.optinfo = opt.linprog(objective, A_eq=Aeq, b_eq=beq, bounds=bn)
        print(self.optinfo.message)
        self.saveresults()
    
    def saveresults(self):
        j = 0
        for i in range(0, self.hp):
            self.results[i] = self.optinfo.x[j:(j+10)]
            j += 10

        np.savetxt(self.paths['results'], self.results, fmt='%.3f', delimiter=' ', newline='\r\n')
        print('Wynik optymalizacji zapisano do pliku.')

class Variable(IntEnum):
    res_u = 0
    res_es = 1
    res_m = 2
    es_u = 3
    es_m = 4
    m_u = 5
    m_es = 6
    g_u = 7
    g_es = 8
    soc = 9


class Price(IntEnum):
    from_grid = 0
    to_microgrid = 1
    from_microgrid = 2


class Equation(IntEnum):
    load_balance = 0
    res_balance = 1
    soc = 2
    surplus_sale = 3


class Restr(IntEnum):
    max_charge = 0
    max_discharge = 1
    max_soc = 2
    min_soc = 3
    discharge_coef = 4
    efficiency_coef = 5
    capacity = 6
