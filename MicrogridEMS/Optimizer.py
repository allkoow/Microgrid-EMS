import dataoperation as do
from numpy import *
import numpy as np
import scipy.linalg
import scipy.optimize as opt
from enum import IntEnum

class Model(object):
    def __init__(self, model_path):
        self.paths = do.getpaths(model_path)

        self.demand = do.parsefloat(self.paths['demand'])
        self.prices = do.parsefloat(self.paths['prices'], line_numbers = 3)
        self.profile = do.parsefloat(self.paths['profile'])
        self.restr = do.parsefloat(self.paths['restr'])
        self.soc = do.parsefloat(self.paths['soc'])

        self.hp = 24
        self.variables_number = 10
        self.restr_number = 4

        self.objective = np.zeros(self.variables_number * self.hp)
        self.Aeq = np.zeros((self.restr_number * self.hp, self.variables_number * self.hp))
        self.beq = np.zeros(self.restr_number * self.hp)
        self.bn = []

    def make_objective(self):
        j, i = 0, 0

        for period in range(0, self.hp):
            # 1. koszt energii z sieci dystrybucyjnej
            objective[ix_([j+self.Variable.g_u,
                           j+self.Variable.g_es])] = self.prices[self.Price.from_grid, period]
            # 2. koszt energii kupionej z mikrosieci
            objective[ix_([j+self.Variable.m_u,
                           j+self.Variable.m_es])] = self.prices[self.Price.from_microgrid, period]

            j += self.variables_number
            i += self.restr_number

    def make_constraints(self):
        i, j = 0, 0

        for period in range(0, self.hp):
            # 1. Bilans energetyczny odbioru
            self.Aeq[i+Equation.load_balance][ix_([j+Variable.res_u,
                                                        j+Variable.es_u,
                                                        j+Variable.m_u,
                                                        j+Variable.g_u])] = 1
            
            self.beq[i+Equation.load_balance] = self.demand[period]

            # 2. Bilans energetyczny OZE
            self.Aeq[i+Equation.res_balance][ix_([j+Variable.res_u,
                                                  j+Variable.res_es,
                                                  j+Variable.res_m])] = 1
            
            self.beq[i+Equation.res_balance] = self.profile[period]

            # 3. Stan zasobnika
            self.Aeq[i+Equation.soc][j+Variable.soc] = 1
            
            self.Aeq[i+Equation.soc][ix_([j+Variable.es_u, 
                                          j+Variable.es_m])] = 1/self.restr[Restr.capacity]
            
            self.Aeq[i+Equation.soc][ix_([j+Variable.res_es,
                                          j+Variable.m_es,
                                          j+Variable.g_es])] = -self.restr[Restr.efficiency_coef]/restr[Restr.capacity]

            if period>0:
                self.Aeq[i+Equation.soc][j+Variable.previous_soc] = -self.restr[Restr.discharge_coef]
            else:
                self.beq[i+Equation.soc] = self.soc[0]

            # 4. Sprzedaż nadwyżek
            self.Aeq[i+Equation.surplus_sale][ix_([j+Variable.res_m,
                                                   j+Variable.es_m])] = 1
            
            if self.profile[period]>self.demand[period]:
                self.beq[i+Equation.surplus_sale] = self.profile[period]-self.demand[period]
            else:
                self.beq[i+Equation.surplus_sale] = 0

            # Ograniczenia brzegowe
            self.bn.extend([(0, self.profile[period]), 
                            (0, self.profile[period]), 
                            (0, self.profile[period])])
            
            self.bn.extend([(0, self.restr[Restr.max_charge]), 
                            (0, self.restr[Restr.max_charge])])
            
            self.bn.extend([(0, self.demand[period]), 
                            (0, self.restr[Restr.max_charge]), 
                            (0, self.demand[period]), 
                            (0, self.restr[Restr.max_charge])])
            
            self.bn.append((self.restr[Restr.min_soc], self.restr[Restr.max_soc]))

            j += self.variables_number
            i += self.restr_number
    

   
class Optimizer(object):

    def __init__(self, config = 'files/config.txt'):
        self.model = Model(config)


        self.optinfo = []
        self.results = np.empty([self.hp, self.variables_number])




    def calculate(self):
        
        objective = self.make_objective_function()
        Aeq, beq, bn = self.make_constraints()

        self.optinfo = opt.linprog(objective, A_eq=Aeq, b_eq=beq, bounds=bn)
        
        print(self.optinfo.message)
        
        self.saveresults()

    
    def make_constraints(self):
        demand = self.model['demand']
        profile = self.model['profile']
        SOC0 = self.model['soc']
        restr = self.model['restr']

        Aeq = np.zeros((self.restr_number * self.hp, self.variables_number * self.hp))
        beq = np.zeros(self.restr_number * self.hp)
        bn = []

        i, j = 0, 0

        for period in range(0, self.hp):
            # 1. Bilans energetyczny odbioru
            Aeq[i+self.Equation.load_balance][ix_([j+self.Variable.res_u,
                                                   j+self.Variable.es_u,
                                                   j+self.Variable.m_u,
                                                   j+self.Variable.g_u])] = 1
            
            beq[i+self.Equation.load_balance] = demand[period]

            # 2. Bilans energetyczny OZE
            Aeq[i+self.Equation.res_balance][ix_([j+self.Variable.res_u,
                                                  j+self.Variable.res_es,
                                                  j+self.Variable.res_m])] = 1
            
            beq[i+self.Equation.res_balance] = profile[period]

            # 3. Stan zasobnika
            Aeq[i+self.Equation.soc][j+self.Variable.soc] = 1
            
            Aeq[i+self.Equation.soc][ix_([j+self.Variable.es_u, 
                                          j+self.Variable.es_m])] = 1/restr[self.Restr.capacity]
            
            Aeq[i+self.Equation.soc][ix_([j+self.Variable.res_es,
                                          j+self.Variable.m_es,
                                          j+self.Variable.g_es])] = -restr[self.Restr.efficiency_coef]/restr[self.Restr.capacity]

            if period>0:
                Aeq[i+self.Equation.soc][j+self.Variable.previous_soc] = -restr[self.Restr.discharge_coef]
            else:
                beq[i+self.Equation.soc] = SOC0[0]

            # 4. Sprzedaż nadwyżek
            Aeq[i+self.Equation.surplus_sale][ix_([j+self.Variable.res_m,
                                                   j+self.Variable.es_m])] = 1
            
            if profile[period]>demand[period]:
                beq[i+self.Equation.surplus_sale] = profile[period]-demand[period]
            else:
                beq[i+self.Equation.surplus_sale] = 0

            # Ograniczenia brzegowe
            bn.extend([(0, profile[period]), 
                       (0, profile[period]), 
                       (0, profile[period])])
            
            bn.extend([(0, restr[self.Restr.max_charge]), 
                       (0, restr[self.Restr.max_charge])])
            
            bn.extend([(0, demand[period]), 
                       (0, restr[self.Restr.max_charge]), 
                       (0, demand[period]), 
                       (0, restr[self.Restr.max_charge])])
            
            bn.append((restr[self.Restr.min_soc], restr[self.Restr.max_soc]))

            j += self.variables_number
            i += self.restr_number

        return (Aeq, beq, bn)


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
        previous_soc = -1

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
