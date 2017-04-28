import numpy as np
from numpy import *
import dataoperation as do
from HouseholdAgent import HouseholdAgent
from Optimization import Variable

agent = HouseholdAgent(id = "001")

agent.set_prediction_horizon(24)
agent.optimize(bounds_power_from_microgrid = (0, 0))

do.printcolumn(agent.optimizer.results[:, Variable.m_u])


