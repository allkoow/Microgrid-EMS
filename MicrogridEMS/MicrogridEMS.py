import numpy as np
from numpy import *
import scipy.linalg
import scipy.optimize as opt
import microgridOpitimizer as ems
import getDatas

hp, numberOfLoads = 2, 1

demand = getDatas.parseFloat('demand.txt',numberOfLoads)
prices = getDatas.parseFloat('prices.txt',3)
profiles = getDatas.parseFloat('profiles.txt',numberOfLoads)
SOC = getDatas.parseFloat('SOC0.txt',numberOfLoads)
restrictions = getDatas.parseFloat('restrictions.txt',numberOfLoads)

f = ems.optimizer(hp,60,prices,demand[0],profiles[0],SOC[0],restrictions[0])









