import dataoperation as do
from numpy import *
import numpy as np
import scipy.linalg
import scipy.optimize as opt

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
        hp = self.hp
        prices = self.model['prices']
        demand = self.model['demand']
        profile = self.model['profile']
        SOC0 = self.model['soc']
        restr = self.model['restr']

        #przeskalowanie minut na godziny
        step = self.step / 60

        # liczba zmiennych w zadaniu dla jednego kroku i ogr. 
        x, y = self.variables_number, self.restr_number

        # inicjalizacja macierzy
        f = np.zeros(x*hp)
        Aeq = np.zeros((y*hp, x*hp))
        beq = np.zeros(y*hp)
        bn = []
    
        j, i = 0, 0

        for it in range(0, hp):
            # 1. koszt energii z sieci dystrybucyjnej
            f[(j+7):(j+9)] = prices[0][it]*step
            # 2. koszt energii kupionej z mikrosieci
            f[(j+5):(j+7)] = prices[2][it]*step

            # ograniczenia rownosciowe
            # 1. Bilans energetyczny odbioru
            Aeq[i][ix_([j+0,j+3,j+5,j+7])] = 1
            beq[i] = demand[it]
            # 2. Bilans energetyczny OZE
            Aeq[i+1][(j+0):(j+3)] = 1
            beq[i+1] = profile[it]
            # 3. Stan zasobnika
            Aeq[i+2][j+9] = 1
            Aeq[i+2][ix_([j+3,j+4])] = 1/restr[6]
            Aeq[i+2][ix_([j+1,j+6,j+8])] = -restr[5]/restr[6]

            if it>0:
                Aeq[i+2][j-1] = -restr[4]
            else:
                beq[i+2] = SOC0[0]

            # 4. Sprzedaż nadwyżek
            Aeq[i+3][ix_([j+2,j+4])] = 1
            if profile[it]>demand[it]:
                beq[i+3] = profile[it]-demand[it]
            else:
                beq[i+3] = 0

            # Ograniczenia brzegowe
            bn.extend([(0,profile[it]), (0,profile[it]), (0,profile[it])])
            bn.extend([(0,restr[1]), (0,restr[1])])
            bn.extend([(0,demand[it]), (0,restr[1]), (0,demand[it]), (0,restr[1])])
            bn.extend([(restr[3], restr[2])])

            j += x
            i += y

            #np.savetxt('optimization_task/Aeq.txt', Aeq,fmt='%.3f', delimiter='\t', newline='\r\n')
            #np.savetxt('optimization_task/beq.txt', beq,fmt='%.3f', delimiter=' ',  newline='\r\n')
    
        self.optinfo = opt.linprog(f, A_eq=Aeq, b_eq=beq, bounds=bn)
        self.saveresults()
    
    def saveresults(self):
        j = 0
        for i in range(0, self.hp):
            self.results[i] = self.optinfo.x[j:(j+10)]
            j += 10

        np.savetxt(self.paths['results'], self.results, fmt='%.3f', delimiter=' ', newline='\r\n')
        print('Wynik optymalizacji zapisano do pliku.')
