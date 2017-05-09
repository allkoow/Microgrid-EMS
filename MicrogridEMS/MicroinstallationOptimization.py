from Optimization import *

class MicroinstallationOptimizer(Optimizer):

    def __init__(self, config_path):
        self.model = MicroinstallationModel(config_path)
        super(MicroinstallationOptimizer, self).__init__()

    def calculate(self):
        self.model.load_data_from_files()
        self.model.is_trade_bounds_empty()
        self.prepare_task()
        
        self.optinfo = opt.linprog(self.model.objective, 
                                   A_eq = self.model.Aeq, 
                                   b_eq = self.model.beq, 
                                   bounds = self.model.bounds)
        
        print(self.optinfo.message)
        
        self.save_results(self.model.paths['results'])

class MicroinstallationModel(Model):
    def __init__(self, config_path):
        self.paths = do.get_paths(config_path)
        
        self.load_data_from_files()

        super(MicroinstallationModel, self).__init__(variables_num = 10, 
                                                     inequality_constr_num = 0, 
                                                     equality_constr_num = 4, 
                                                     prediction_horizon = len(self.demand))

        self.fill_trade_bounds_with_none()

    def load_data_from_files(self):
        self.demand = do.get_data_from_file(self.paths['demand'])
        self.price_from_grid = do.get_data_from_file(self.paths['prices'])
        self.profile = do.get_data_from_file(self.paths['profile'])
        self.restr = do.get_data_from_file(self.paths['restr'])
        self.soc = do.get_data_from_file(self.paths['soc'])
        self.trade_bounds = do.get_data_from_file(self.paths['trade_bounds'], 2)

    def is_trade_bounds_empty(self):
        if not self.trade_bounds:
            self.fill_trade_bounds_with_none()
        
    def fill_trade_bounds_with_none(self):
        self.trade_bounds = [[], []]
        for i in range(0, self.prediction_horizon):
            self.trade_bounds[0].append(None)
            self.trade_bounds[1].append(None)

    def make_objective(self):
        j = 0

        for period in range(0, self.prediction_horizon):
            self.objective[ix_([j+Variable.g_u,
                                j+Variable.g_es])] = self.price_from_grid[period]

            j += self.variables_num

    def make_constraints(self):
        i, j = 0, 0

        for period in range(0, self.prediction_horizon):
            # 1. Bilans energetyczny odbioru
            self.Aeq[i+Equation.load_balance][ix_([j+Variable.res_u,
                                                   j+Variable.es_u,
                                                   j+Variable.m_u,
                                                   j+Variable.g_u])] = 1
            
            self.beq[i+Equation.load_balance] = self.demand[period]

            # 2. Bilans energetyczny OZE
            self.Aeq[i+Equation.res_balance][ix_([j+Variable.res_u,
                                                  j+Variable.res_es,
                                                  j+Variable.res_m])] = 1
            
            self.beq[i+Equation.res_balance] = self.profile[period]

            # 3. Stan zasobnika
            self.Aeq[i+Equation.soc][j+Variable.soc] = 1
            
            self.Aeq[i+Equation.soc][ix_([j+Variable.es_u, 
                                          j+Variable.es_m])] = 1/self.restr[Restr.capacity]
            
            self.Aeq[i+Equation.soc][ix_([j+Variable.res_es,
                                          j+Variable.m_es,
                                          j+Variable.g_es])] = -self.restr[Restr.efficiency_coef]/self.restr[Restr.capacity]

            if period>0:
                self.Aeq[i+Equation.soc][j+Variable.previous_soc] = -self.restr[Restr.discharge_coef]
            else:
                self.beq[i+Equation.soc] = self.soc[0]

            # 4. Sprzedaz nadwyzek
            self.Aeq[i+Equation.surplus_sale][ix_([j+Variable.res_m,
                                                   j+Variable.es_m])] = 1
            
            if self.profile[period]>self.demand[period]:
                self.beq[i+Equation.surplus_sale] = self.profile[period]-self.demand[period]
            else:
                self.beq[i+Equation.surplus_sale] = 0

            # Ograniczenia brzegowe
            self.bounds[j+Variable.res_u] = (0, self.profile[period])
            self.bounds[j+Variable.res_es] = (0, self.profile[period])
            self.bounds[j+Variable.res_m] = (0, self.profile[period])
            
            self.bounds[j+Variable.es_u] = (0, self.restr[Restr.max_charge])
            self.bounds[j+Variable.es_m] = (0, self.restr[Restr.max_charge])
            
            self.bounds[j+Variable.m_u] = (0, self.trade_bounds[0][period])
            self.bounds[j+Variable.m_es] = (0, self.trade_bounds[1][period])

            self.bounds[j+Variable.g_u] = (0, self.restr[Restr.connection_constraint])
            self.bounds[j+Variable.g_es] = (0, self.restr[Restr.max_charge])

            self.bounds[j+Variable.soc] = (self.restr[Restr.min_soc], self.restr[Restr.max_soc])
            
            j += self.variables_num
            i += self.equality_constr_num


class Restr(IntEnum):
        max_charge = 0
        max_discharge = 1
        max_soc = 2
        min_soc = 3
        discharge_coef = 4
        efficiency_coef = 5
        capacity = 6
        connection_constraint = 7

class Equation(IntEnum):
        load_balance = 0
        res_balance = 1
        soc = 2
        surplus_sale = 3