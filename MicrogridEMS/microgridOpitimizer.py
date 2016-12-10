import numpy as np
from numpy import *
import scipy.linalg
import scipy.optimize as opt

def optimizer(hp,step,prices,demand,profile,SOC0,restrictions):
    #przeskalowanie minut na godziny
    step = step / 60

    # liczba zmiennych w zadaniu dla jednego kroku i ogr. 
    x,y = 10,4

    # inicjalizacja macierzy
    f = np.zeros(x*hp)
    Aeq = np.zeros((yeq*hp,x*hp))
    beq = np.zeros(yeq*hp)
    bn = []
    
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
        Aeq[i+2][ix_([j+1,j+6,j+8])] = -restrictions[5]/restrictions[6]

        if it>0:
            Aeq[i+2][j-1] = -restrictions[4]
        else:
            beq[i+2] = SOC0[0]

        # 4. Sprzedaż nadwyżek
        Aeq[i+3][ix_([j+2,j+4])] = 1
        if profile[it]>demand[it]:
            beq[i+3] = profile[it]-demand[it]
        else:
            beq[i+3] = 0

        # Ograniczenia brzegowe
        bn.append((0,profile[it]))
        bn.append((0,profile[it]))
        bn.append((0,profile[it]))
        bn.append((0,restrictions[1]))
        bn.append((0,restrictions[1]))
        bn.append((0,demand[it]))
        bn.append((0,restrictions[0]))
        bn.append((0,demand[it]))
        bn.append((0,restrictions[0]))
        bn.append((restrictions[3],restrictions[2]))

        j = j + x;
        i = i + y

        np.savetxt('Aeq.txt',Aeq,fmt='%.3f',delimiter='\t',newline='\r\n')
        np.savetxt('beq.txt',beq,fmt='%.3f',delimiter=' ',newline='\r\n')
    
    res = opt.linprog(f,A_eq=Aeq,b_eq=beq,bounds=bn)
    return res
    
