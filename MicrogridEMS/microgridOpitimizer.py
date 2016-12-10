import numpy as np
from numpy import *
import scipy.linalg

def optimizer(hp,step,prices,demand,profile,S0C0,restrictions):
    #przeskalowanie minut na godziny
    step = step / 60

    # liczba zmiennych w zadaniu dla jednego kroku
    x = 10

    # liczba ograniczen rownosciowych
    yeq = 4

    f = np.zeros(x*hp)
    Aeq = np.zeros((yeq*hp,x*hp))
    beq = np.zeros((yeq*hp,1))
    j = 0
    i = 0

    for it in range(0,hp):
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
        Aeq[i+2][ix_([j+3,j+4])] = 1/restrictions[6]
        Aeq[i+2][ix_([j+6,j+8])] = -restrictions[5]/restrictions[6]

        if it>0:
            Aeq[i+2][j-1] = -restrictions[4]

        # 4. Sprzedaż nadwyżek
        Aeq[i+3][ix_([j+2,j+4])] = 1
        if profile[it]>demand[it]:
            beq[i+3] = profile[it]-demand[it]
        else:
            beq[i+3] = 0

        j = j + x;
        i = i + yeq


        
    return Aeq
    
