import dataoperation as do
from numpy import *
import numpy as np
import scipy.linalg
import scipy.optimize as opt
from enum import IntEnum
from abc import ABC

class Model(ABC):
    def __init__(self, variables_num, inequality_constr_num, equality_constr_num, prediction_horizon):
        self.variables_num = variables_num
        self.inequality_constr_num = inequality_constr_num
        self.equality_constr_num = equality_constr_num
        self.prediction_horizon = prediction_horizon

    def prepare_matrixes(self):
        self.fill_matrixes_with_zeros()
        self.make_objective()
        self.make_constraints()

    def make_objective(self):
        pass

    def make_constraints(self):
        pass

    def fill_matrixes_with_zeros(self):
        rows_in_equalities_num = self.equality_constr_num * self.prediction_horizon
        rows_in_inequalities_num = self.inequality_constr_num * self.prediction_horizon
        columns_num = self.variables_num * self.prediction_horizon
        
        self.objective = np.zeros(columns_num)
        self.bounds = np.empty(columns_num, dtype = object)

        if self.equality_constr_num > 0:
            self.Aeq = np.zeros((rows_in_equalities_num, columns_num))
            self.beq = np.zeros(rows_in_equalities_num)

        if self.inequality_constr_num > 0:
            self.A_ub = np.zeros((rows_in_inequalities_num, columns_num))
            self.b_ub = np.zeros(rows_in_inequalities_num)

    
class MicroinstallationModel(Model):
    def __init__(self, config_path):
        self.paths = do.get_paths(config_path)
        self.prepare_model()
        
        super(MicroinstallationModel, self).__init__(variables_num = 10, 
                                                     inequality_constr_num = 0, 
                                                     equality_constr_num = 4, 
                                                     prediction_horizon = len(self.demand))

        self.prepare_matrixes()
    
    def prepare_model(self):
        self.demand = do.get_data_from_file(self.paths['demand'])
        self.price_from_grid = do.get_data_from_file(self.paths['prices'])
        self.profile = do.get_data_from_file(self.paths['profile'])
        self.restr = do.get_data_from_file(self.paths['restr'])
        self.soc = do.get_data_from_file(self.paths['soc'])

    def make_objective(self):
        j = 0

        for period in range(0, self.prediction_horizon):
            self.objective[ix_([j+Variable.g_u,
                                j+Variable.g_es])] = self.price_from_grid[period]

            j += self.variables_num

    def make_constraints(self):
        i, j = 0, 0

        for period in range(0, self.prediction_horizon):
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
                                          j+Variable.g_es])] = -self.restr[Restr.efficiency_coef]/self.restr[Restr.capacity]

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
            self.bounds[j+Variable.res_u] = (0, self.profile[period])
            self.bounds[j+Variable.res_es] = (0, self.profile[period])
            self.bounds[j+Variable.res_m] = (0, self.profile[period])
            
            self.bounds[j+Variable.es_u] = (0, self.restr[Restr.max_charge])
            self.bounds[j+Variable.es_m] = (0, self.restr[Restr.max_charge])
            
            self.bounds[j+Variable.m_u] = (0, None)
            self.bounds[j+Variable.m_es] = (0, None)

            self.bounds[j+Variable.g_u] = (0, self.restr[Restr.connection_constraint])
            self.bounds[j+Variable.g_es] = (0, self.restr[Restr.max_charge])

            self.bounds[j+Variable.soc] = (self.restr[Restr.min_soc], self.restr[Restr.max_soc])
            
            j += self.variables_num
            i += self.equality_constr_num


class Optimizer(ABC):
    def __init__(self):
        self.optinfo = []
        self.clear_results()

    def calculate(self):
        pass

    def prepare_task(self):
        self.clear_results()
        self.model.prepare_matrixes()

    def clear_results(self):
        self.results = np.empty([self.model.prediction_horizon, self.model.variables_num])
    
    def save_results(self, file_path):
        j = 0
        for i in range(0, self.model.hp):
            self.results[i] = self.optinfo.x[j:(j+self.model.variables_num)]
            j += self.model.variables_num

        np.savetxt(file_path, self.results, fmt='%.3f', delimiter=' ', newline='\r\n')
        print('Wynik optymalizacji zapisano do pliku.')


class MicroinstallationOptimizer(Optimizer):

    def __init__(self, config_path):
        self.model = MicroinstallationModel(config_path)
        super(MicroinstallationOptimizer, self).__init__()

    def calculate(self):
        self.prepare_task()

        self.optinfo = opt.linprog(self.model.objective, 
                                   A_eq = self.model.Aeq, 
                                   b_eq = self.model.beq, 
                                   bounds = self.model.bounds)
        
        print(self.optinfo.message)
        
        self.save_results(self.model.paths['results'])


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
        connection_constraint = 7
