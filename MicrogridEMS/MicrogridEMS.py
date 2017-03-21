import numpy as np
from numpy import *
import microgridOpitimizer as ems
import getDatas

hp, numberOfLoads = 24, 1
load = 1

demand = getDatas.parseFloat('demand.txt',numberOfLoads)
prices = getDatas.parseFloat('prices.txt',3)
profiles = getDatas.parseFloat('profiles.txt',numberOfLoads)
SOC = getDatas.parseFloat('SOC0.txt',numberOfLoads)
restrictions = getDatas.parseFloat('restrictions.txt',numberOfLoads)

res = ems.optimizer(hp,60,prices,demand[load-1],profiles[load-1],SOC[load-1],restrictions[load-1])

x=[]
j = 0
for i in range(0,hp):
    x.append(res.x[j:(j+10)])
    j = j+10

for row in x:
    print(row)

np.savetxt('res.txt',x,fmt='%.3f',delimiter=' ',newline='\r\n')






