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
        self.organize_results_into_square_matrix()
        do.save_to_file(file_path, self.results)
        print('Wynik optymalizacji zapisano do pliku.')

    def organize_results_into_square_matrix(self):
        j = 0
        for i in range(0, self.model.prediction_horizon):
            self.results[i] = self.optinfo.x[j:(j+self.model.variables_num)]
            j += self.model.variables_num

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




