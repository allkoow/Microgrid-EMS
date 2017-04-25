import numpy as np
from numpy import *
import dataoperation as do
import Optimizer as ems

optimizer = ems.Optimizer()
optimizer.calculate()

print(optimizer.optinfo.message)

#needs_and_offers = dict()
#needs_and_offers['res_to_microgrid'] = results[:, 2]
#needs_and_offers['es_to_microgrid'] = results[:, 4]
#needs_and_offers['microgrid_to_load'] = results[:, 5]
#needs_and_offers['microgrid_to_es'] = results[:, 6]

#do.printcolumn(needs_and_offers['res_to_microgrid'])








