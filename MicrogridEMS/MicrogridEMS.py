import numpy as np
from numpy import *
import moptimizer as ems
import dataoperation as do

information = dict()

information['prediction_horizon'] = 24
information['demand'] = do.parsefloat('files/demand.txt')
information['profile'] = do.parsefloat('files/profiles.txt')
information['restrictions'] = do.parsefloat('files/restrictions.txt')
information['prices'] = do.parsefloat('files/prices.txt', 3)
information['SOC0'] = do.parsefloat('files/SOC0.txt')

results = ems.optimizer(information)

np.savetxt('optimization_task/results.txt', results, fmt='%.3f', delimiter=' ', newline='\r\n')

needs_and_offers = dict()
needs_and_offers['res_to_microgrid'] = results[:, 2]
needs_and_offers['es_to_microgrid'] = results[:, 4]
needs_and_offers['microgrid_to_load'] = results[:, 5]
needs_and_offers['microgrid_to_es'] = results[:, 6]

do.printcolumn(needs_and_offers['res_to_microgrid'])








