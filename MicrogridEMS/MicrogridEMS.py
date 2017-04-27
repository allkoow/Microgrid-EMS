import numpy as np
from numpy import *
import dataoperation as do
from HouseholdAgent import HouseholdAgent


agent = HouseholdAgent()
agent.optimize()

do.printcolumn(agent.offers.res_m.power)














