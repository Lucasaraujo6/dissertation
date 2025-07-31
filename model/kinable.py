#documentarion https://www.ibm.com/docs/en/icos/22.1.1?topic=cplex-list-parameters
from docplex.mp.model import Model
# from docplex.mp.constants import WriteLevel
import numpy as np
import data, time


class md():
    def __init__(self,dt):
        self.dt = dt

    def create_model(self):
        dt : data.Instance = self.dt 

        I, J, L = dt.I, dt.J, dt.Lj
        J = [J[i] + 1 for i in J]
        # print(len(C))

        D = [(j, l) for j in J for l in L[j - 1]]
        V = [0]
        # input(D)
        D_codes = []
        vValueToTrip = [None]
        idx = 1
        for trip in D:
            V.append(idx)
            D_codes.append(idx)
            # print(trip,idx)
            idx+=1
            vValueToTrip.append(trip)
        V.append(idx)
        vValueToTrip.append(None)

        K = range(dt.K)

        c = []
        A = []
        M = 9999
        
        A.append((0,V[-1]) ) 
        c.append(0)
        # print(A[-1], c[-1])
        for i in V:
            if i == V[-1]: continue
            for j in V:
                if j == 0 or (i == 0 and j == V[-1]): continue
                if i == 0:
                    A.append((i, j))
                    c.append(min(dt.c[plant][vValueToTrip[j][0] - 1] + dt.dist_plant_central[plant] for plant in I))
                    # print(A[-1], c[-1])
                elif j == V[-1]:
                    A.append((i, j))
                    c.append(min(dt.c[plant][vValueToTrip[i][0] - 1] + dt.dist_plant_central[plant] for plant in I))
                    # print(A[-1], c[-1])
                elif ((vValueToTrip[i][0] == vValueToTrip[j][0] and vValueToTrip[i][1] < vValueToTrip[j][1]) 
                or (vValueToTrip[i][0] != vValueToTrip[j][0] 
                    and dt.a[vValueToTrip[i][0] - 1] + dt.min_k_value 
                        <= dt.b[vValueToTrip[j][0] - 1] - dt.min_k_value )):
                    
                    A.append((i, j))
                    c.append(min(dt.c[plant][vValueToTrip[i][0] - 1] + dt.c[plant][vValueToTrip[j][0] - 1] for plant in I))
                    # print(A[-1], c[-1])
                    # print(vValueToTrip[j],vValueToTrip[i])
        # print("\nA")
        # print(A)
        # # print(c)
        # # print(len(A))
        # # print(len(c))
        # input()
        def outgoing(A, trip):
            return [(origin, destination) for origin, destination in A if origin == trip]
        
        def incoming(A, trip, vValueToTrip = None):
            if vValueToTrip: 
                # print("trip",trip)
                # print(vValueToTrip)
                return [
                        (origin, destination)
                        for origin, destination in A
                        if 0 <= destination < len(vValueToTrip)
                        and isinstance(vValueToTrip[destination], (list, tuple))
                        and vValueToTrip[destination][0] == trip
                    ]

            return [(origin, destination) for origin, destination in A if destination == trip]
        
        m = Model(name='CDP2')
        
        # 33,34 - Variáveis de decisão

        # x = m.binary_var_dict(A, name='x')  # Se um caminhão atende uma viagem específica
        x = m.binary_var_dict(((i, j, k) for (i, j) in A for k in K), name='x')
        y = m.binary_var_dict(J, name='y')  # Se um cliente é atendido
        C_end = m.integer_var_dict(V, name='C')  # Tempo de conclusão da entrega (corrigido para V)
        dt.qk = [dt.qk[0] for k in dt.qk]
        
        # 21 - Função objetivo: Maximizar a quantidade de concreto entregue
        m.maximize(m.sum(dt.d[j - 1] * y[j] for j in J))
        
        # 22 - Todo veículo sai pelo menos uma vez
        m.add_constraints(m.sum(x[(i, j, k)] for (i,j) in outgoing(A,0) ) == 1 for k in K)
        m.add_constraints(m.sum(x[(i, j, k)] for (i,j) in incoming(A,V[-1]) ) == 1 for k in K)

        # 23 - Toda viagem de chegada tem que sair
        m.add_constraints(m.sum(x[i,j,k] for (i,j) in incoming(A,code) ) 
                        == m.sum(x[i,j,k] for (i,j) in outgoing(A,code) ) for code in D_codes for k in K)
        
        # 24 - Todo nó tem apenas uma saída
        m.add_constraints(m.sum(x[(i, j, k)] for (i,j) in outgoing(A,code) for k in K ) <= 1  for code in D_codes)

        # 25 - ativação de viagens sucessivas
        m.add_constraints(m.sum(x[(i, j, k)] for (i,j) in outgoing(A, code) for k in K )  
                        >= m.sum(x[(i, j, k)] for (i,j) in outgoing(A, code+1) for k in K ) 
                        for code in D_codes[:-1] if (vValueToTrip[code][0] == vValueToTrip[code+1][0]))

        # 26 - Restrição de atendimento de clientes
        m.add_constraints(m.sum(dt.qk[k] * x[i,j,k] for k in K for (i,j) in incoming(A,jj,vValueToTrip) ) >= dt.d[jj-1] * y[jj] for jj in J)
        
        # 27,28 - Restrição de tempo de conclusão
        m.add_constraints(C_end[i] - M * (1 - x[i, j, k]) <= C_end[j] - dt.qk[k] - c[A.index((i, j))] for k in K for (i,j) in A if i!=0 )
        m.add_constraints(C_end[i] - M * (1 - x[i, j, k]) <= C_end[j] - c[A.index((i, j))] for k in K for (i, j) in A if i == 0 )
        
        # 29 - início do descarregamento após abertura da TW 
        m.add_constraints(C_end[code] - m.sum(dt.qk[k] * x[(i, j, k)] for k in K for (i,j) in outgoing(A,code) ) 
                          >= dt.a[vValueToTrip[code][0]-1] for code in D_codes)
        
        # 30,31 - timelag entre viagens do mesmo cliente
        m.add_constraints(C_end[code+1] - m.sum(dt.qk[k] * x[i,j,k] for k in K for (i,j) in outgoing(A,code)) - C_end[code] <= dt.time_lag 
                        for code in D_codes[:-1] if (vValueToTrip[code][0] == vValueToTrip[code+1][0]))
        m.add_constraints(C_end[code + 1] >= C_end[code] +  m.sum(dt.qk[k] * x[(i, j, k)] for k in K for (i,j) in outgoing(A,code) )
                        for code in D_codes[:-1] if (vValueToTrip[code][0] == vValueToTrip[code+1][0]))
        # # input(A)
        # # 32 - Restrição de tempo de início e janelas de tempo
        # # # # m.add_constraints(dt.a[j - 1] <= C_end[(j, l)] for (j, l) in D )
        m.add_constraints(C_end[code] <= dt.b[vValueToTrip[code][0] - 1]  for code in D_codes )
        
        # Armazenamento das variáveis e modelo
        dt.x, dt.y, dt.C_end = x, y, C_end
        self.m = m
        # m.export_as_lp('tsp.lp') 
        # input('exported')


    def extract_solution(self, dt: data.Instance, sol):
            dt.vehicles_per_plant = [0] * dt.ni

            unorganized_solution = [[] for vehicle in dt.qk]
            for var in sol.iter_variables():
                # print(var.name, var.solution_value)
                value = round(var.solution_value)
                var_name = var.name
                if value < 1e-5: continue
                if var_name.startswith('x_'):
                    parts = var_name.split('_')
                    origin, destination, vehicle = (parts[1]), (parts[2]), int(parts[3])
                    unorganized_solution[vehicle].append((origin, destination))
                else:

                    unorganized_solution.append((var_name,value))
            # for var in sol.iter_variables():
            #     value = round(var.solution_value)
            #     var_name = var.name
            #     print('kinable', var.name, var.solution_value)

            dt.md_kinable_solution = unorganized_solution
            dt.md_kinable_time = sol._solve_details.time
            dt.md_kinable_cost = sol.objective_value
        
    def run(self, dt: data.Instance):
        self.create_model()
        print('criado o modelo')
        m = self.m
        # m.parameters.mip.limits.solutions = 1
        # m.parameters.mip.limits.treememory = 5000
        if dt.LOG: print('implementou o limite de memória')
        
        sol = m.solve(log_output=dt.LOG, time_limit=dt.TIME_LIMIT)
        print('resolvido')
        jobStatus = m.solve_status.name
        jobDetails = m.solve_details
        # input(jobDetails)
        # input(jobStatus)
        match jobStatus:
            case 'UNKNOWN':
                if dt.LOG: print('limite de execução (tempo ou memória) atingido')
                dt.md_kinable_gap = 100
                dt.md_kinable_cost = -1
            case 'OPTIMAL_SOLUTION':
                if dt.LOG: print('solução otima')
                dt.md_kinable_gap = 0
                dt.md_kinable_cost = -1
                self.extract_solution(dt, sol)
            case 'FEASIBLE_SOLUTION':
                if dt.LOG: print('solução subótima ')
                self.extract_solution(dt, sol)
                dt.md_kinable_gap = round(jobDetails.gap*100, 2)
            case 'INFEASIBLE_SOLUTION':
                if dt.LOG: print('sem solução viável ')
                dt.md_kinable_gap = 100
        dt.md_kinable_status = jobDetails.status
        if dt.LOG: 
            print('PAROU POR ', dt.md_kinable_status)
            print('fo final: ', dt.md_kinable_cost)
            print('tempo de execução: ', dt.md_kinable_time )
