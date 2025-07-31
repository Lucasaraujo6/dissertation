#documentarion https://www.ibm.com/docs/en/icos/22.1.1?topic=cplex-list-parameters
from docplex.mp.model import Model
# from docplex.mp.constants import WriteLevel
from docplex.mp.relax_linear import LinearRelaxer

import numpy as np
import data, time

class md():
    def __init__(self,dt):
        self.dt = dt

    def create_model(self):
        dt : data.Instance = self.dt 
        t = dt.t

        I,J,L,T = dt.I,dt.J,dt.Lj,range(dt.T)
        unloadingTime = dt.qk
        unloadingTime = dt.qk[0]
        vehiclQnt = dt.K
        # IJLR = [(i,j,l,r) for i in I for j in J for l in L[j] for r in range(dt.a[j],dt.b[j])]
        IJLR = [(i,j,l,r) for i in I for j in J for l in L[j] for r in range(dt.a[j],dt.b[j]-unloadingTime+1)]

        # print(IJLR)
        # exit()
        m = Model(name='TimeIndexed')
        # equal 1 if a truck serves trip l of customer j operating at plant i and finishing at time r; 0, otherwise
        h = m.binary_var_dict(J,name='h')
        x = m.binary_var_dict(IJLR,name='x')
        y = m.binary_var_dict(IJLR,name='y')

        # number of trucks assigned to plant i
        z = m.integer_var_dict(I,lb=0.0,ub=dt.K,name='depot_vehicles')
        
        # maximize volume transported
        m.maximize(m.sum(h[j]* dt.d[j]  for (j) in J))

        # one customers' trips must be served maximum once
        m.add_constraints(m.sum(x[i,j,l,r] for (i,j,l,r) in IJLR if j == jj and l == ll) == h[jj] for jj in J for ll in L[jj]) 
        m.add_constraints(m.sum(y[i,j,l,r] for (i,j,l,r) in IJLR if j == jj and l == ll) == h[jj]  for jj in J for ll in L[jj]) 
        
        #restrição de time lag mínimo - a chegada antetior mais o tempo de descarregamento deve ser maior que a chegada posterior
        # m.add_constraints( m.sum(r * x[i,j,l+1,r] for (i,j,l,r) in IJLR if j == jj and l == ll) 
        #                   - m.sum((r +unloadingTime) * x[i,j,l,r] for (i,j,l,r) in IJLR if j == jj and l == ll) 
        #                   >= 0 for jj in J for ll in L[jj][:-1]) 
        
        # # restrição de time lag máximo  - a chegada anterior mais o tempo de descarregamento deve ser ter no max 5 de intervalo com a posterior
        # m.add_constraints( m.sum(r * x[i,j,l+1,r] for (i,j,l,r) in IJLR if j == jj and l == ll) 
        #                   - (unloadingTime +m.sum((r  )* x[i,j,l,r] for (i,j,l,r) in IJLR if j == jj and l == ll) )
        #                   <= 5 for jj in J for ll in L[jj][:-1]) 
        m.add_constraints(m.sum(y[i,j,l,r] for i in I ) 
                    <= m.sum(y[i,j,l+1,rr] for i in I for rr in range(r+unloadingTime,min(r+5+unloadingTime+1 ,dt.b[j]-unloadingTime+1))) 
                    for j in J for l in L[j][:-1] for r in range(dt.a[j],dt.b[j]-unloadingTime+1) ) 
        m.add_constraints(m.sum(x[i,j,l,r] for i in I ) 
                    <= m.sum(x[i,j,l+1,rr] for i in I for rr in range(r+unloadingTime,min(r+5+unloadingTime+1 ,dt.b[j]-unloadingTime+1))) 
                    for j in J for l in L[j][:-1] for r in range(dt.a[j],dt.b[j]-unloadingTime+1) ) 
        #execução de todas de um mesmo cliente
        # m.add_constraints(m.sum(x[i,j,l+1,r] for (i,j,l,r) in IJLR if j == jj and l == ll) 
        #                   == m.sum(x[i,j,l,r] for (i,j,l,r) in IJLR if j == jj and l == ll) 
        #                   for jj in J for ll in L[jj][:-1]) 

        # restrição de término dentro do TH
        # m.add_constraints(m.sum((r + t[i][j]+unloadingTime + dt.dist_plant_central[i])* y[i,j,l,r] for (i,j,l,r) in IJLR if j == jj and l == ll)
        #                    <= dt.T for jj in J for ll in L[jj][:-1]) 
        # m.add_constraints(m.sum((r - t[i][j]- dt.dist_plant_central[i]) * y[i,j,l,r] for (i,j,l,r) in IJLR if j == jj and l == ll)
        #                    >= 0 for jj in J for ll in L[jj]) 
        # 
        # descarregamento dentro da janela
        # m.add_constraints(dt.b[jj]  - unloadingTime- m.sum( r*x[i,j,l,r] for (i,j,l,r) in IJLR if j == jj and l == ll) >= 0 for jj in J for ll in L[jj]) 
        # m.add_constraints(m.sum((r -dt.a[jj]) * x[i,j,l,r] for (i,j,l,r) in IJLR if j == jj and l == ll) >= 0 for jj in J for ll in L[jj]) 
        # m.export_as_lp('tsp.lp') 

        # input()

        #NÃO PODE TER MAIS DO QUE OS VEHICS DISPONÍVEIS NAS PLANTAS
        m.add_constraints(m.sum(x[i,j,l,r] for (i,j,l,r) in IJLR if r>=rr >= r-t[i][j]  )+
                          m.sum(y[i,j,l,r] for (i,j,l,r) in IJLR if r< rr< r + t[i][j] + unloadingTime ) <= vehiclQnt for rr in T) 
        
        # for jj in J:
        #     for ll in L[jj]:
        #         for mm in J:
        #             for nn in L[mm]:
        #                 if dt.a[jj] > dt.b[mm]:
        # # A VIAGEM DE IDA DEVE SER IGUAL A VIAGEM DE VOLTA
        #                     m.add_constraint(
        #                         m.sum(r*x[i,j,l,r] for (i,j,l,r) in IJLR if j == jj and l == ll) 
        #                         + 999 * (1-m.sum(x[i,j,l,r] for (i,j,l,r) in IJLR if j == jj and l == ll) )
        #                                     >= m.sum(d*x[a,b,c,d] for (a,b,c,d) in IJLR if b == mm and c == nn) 
        #                 ) 

        # departure_windows = 2*min(t[i][j] for i in I for j in J)        

        # m.add_constraints(m.sum(x[i,j,l,r] for (i,j,l,r) in IJLR if r in range(rr,rr+unloadingTime+departure_windows-1)) 
        #                   <= vehiclQnt 
        #                   for rr in T) 


        m.add_constraints(m.sum(x[i,j,l,r] for (i,j,l,r) in IJLR if j == jj and l == ll and r == rr) 
                          == m.sum(y[i,j,l,r] for (i,j,l,r) in IJLR if j == jj and l == ll and r == rr) 
                          for jj in J for ll in L[jj] for rr in range(dt.a[jj],dt.b[jj]-unloadingTime+1)) 

        # Para cada instante, toma-se a quantidade de viagens terminadas antes do instante e 
        # # permite que só se inicie no instante se houver veículo parado na planta.
        # esse menor ou igual é o que está me fazendo permitir a saída no instante de término da viagem.
        m.add_constraints( m.sum(y[i,j,l,r] for (i,j,l,r) in IJLR if i == ii and  r+t[i][j] + unloadingTime <=rr) + z[ii]
                          - m.sum(x[i,j,l,r] for (i,j,l,r) in IJLR if i == ii and r-t[i][j]<= rr ) 
                          >= 0
                          for ii in I for rr in T )
        
        m.add_constraint(m.sum(z[i] for i in I) == vehiclQnt)
        
        self.x,self.z = x,z
        self.m = m

    def extract_solution(self, dt: data.Instance, sol):
        if dt.LOG: 
            print('OBJECTIVE VALUE: ', sol.objective_value )
        dt.vehicles_per_plant = [0] * dt.ni
        partial_solution = []
        # for var in sol.iter_variables():
        #     value = round(var.solution_value)
        #     var_name = var.name
        #     print('bb', var.name, var.solution_value)
        for var in sol.iter_variables():
            value = round(var.solution_value)
            var_name = var.name
            if value < 1e-5: continue
            if var_name.startswith('x_'):
                parts = var_name.split('_')
                origin, j, l, delivery_time = int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])
                destination = f'{j}_{l}_{delivery_time}'
                for var in sol.iter_variables():
                    if destination in var.name and var.name != var_name:
                        destination = int(var.name.split('_')[1])
                        break
                strt, endt = delivery_time - dt.t[origin][j], delivery_time + dt.qk[0]  +  dt.t[destination][j]
                partial_solution.append((origin, destination, j, l, strt, endt,delivery_time))# , dt.t[i][j]))
            elif var_name.startswith('z_'):
                parts = var_name.split('_')
                plant = int(parts[1])
                trucks = int(value)  # Certifique-se de converter para inteiro aqui
                dt.vehicles_per_plant[plant] = trucks
        partial_solution.sort(key=lambda x: (x[5]))
        partial_solution.sort(key=lambda x: (x[4]))
        # print('partial_solution', len(partial_solution))
        
        # distribuo as viagens entre os veículos
        vehicles_trips = [[] for vehicle in dt.qk]
        for vehicle_id, cap in enumerate(dt.qk):
            if not partial_solution:
                break
            if not vehicles_trips[vehicle_id]:
                vehicles_trips[vehicle_id].append(partial_solution.pop(0))

            idx = 0
            while idx < len(partial_solution):  # Percorre sem modificar o índice automaticamente
                trip = partial_solution[idx]
                vehicle_last_trip = vehicles_trips[vehicle_id][-1]

                if trip[4] >= vehicle_last_trip[-1] and trip[0] == vehicle_last_trip[1]:
                    vehicles_trips[vehicle_id].append(partial_solution.pop(idx))
                else:
                    idx += 1  # Apenas avança se não remover elemento
        # print(sol.iter_variables())
        print('(plantaOrig, plantaDest, Cliente, viagem, início, fim)')
        print('vehicles_trips',vehicles_trips)
        # temp = sum(len(trips) for trips in vehicles_trips)
        # print(temp)
        # input()


        dt.md_authorial_1_lr_solution = vehicles_trips
        print('dt.md_authorial_1_lr_solution',dt.md_authorial_1_lr_solution)
        dt.md_authorial_1_lr_nb_nodes = sol.solve_details.nb_nodes_processed
        print('dt.md_authorial_1_lr_nb_nodes',dt.md_authorial_1_lr_nb_nodes)
        dt.md_authorial_1_lr_best_integer = sol.solve_details.best_bound
        print('dt.md_authorial_1_lr_best_integer',dt.md_authorial_1_lr_best_integer)
        dt.md_authorial_1_lr_time = sol._solve_details.time
        print('dt.md_authorial_1_lr_time',dt.md_authorial_1_lr_time)
        dt.md_authorial_1_lr_cost = sol.objective_value
        print('dt.md_authorial_1_lr_cost',dt.md_authorial_1_lr_cost)

    def run(self, dt: data.Instance):
        print('\nAuthorial LR')
        self.create_model()
        print('Criou')
        m = self.m = LinearRelaxer.make_relaxed_model(self.m)



        # Desabilitar heurísticas
        # m.context.cplex_parameters.mip.strategy.heuristicfreq = -1

        # ctx = m.context.cplex_parameters.mip
        # # Desativar todos os cortes de uma vez (opcional, mas pode ser usado com o acima)
        # ctx.strategy.search = 2  # 1 = tradicional, 0 = auto, 2 = dynamic search
        
        # ctx = ctx.cuts
        # # Desabilitar todos os tipos de cortes
        # ctx.cliques = -1
        # ctx.covers = -1
        # ctx.flowcovers = -1
        # ctx.gomory = -1
        # ctx.implied = -1
        # ctx.mircut = -1
        # ctx.pathcut = -1
        # ctx.liftproj = -1
        # ctx.rlt = -1
        # ctx.zerohalfcut = -1
        # ctx.mcfcut = -1
        # ctx.disjunctive = -1


        # # ctx.tolerances.mipgap  # → este é de tolerância do gap
        # # m.parameters.mip.limits.solutions = 1
        # # m.parameters.mip.limits.treememory = 5000
        # # if dt.LOG: print('implementou o limite de memória')
        m.parameters.mip.limits.treememory = 10000
        m.parameters.threads= 10

        sol = m.solve(log_output=dt.LOG, time_limit=dt.TIME_LIMIT)
        print('Resolveu')
        jobStatus = m.solve_status.name
        jobDetails = m.solve_details

        match jobStatus:
            case 'UNKNOWN':
                if dt.LOG: print('limite de execução (tempo ou memória) atingido')
                dt.md_authorial_1_lr_gap = 100
            case 'OPTIMAL_SOLUTION':
                if dt.LOG: print('solução otima')
                dt.md_authorial_1_lr_gap = 0
                self.extract_solution(dt, sol)
            case 'FEASIBLE_SOLUTION':
                if dt.LOG: print('solução subótima ')
                self.extract_solution(dt, sol)
                dt.md_authorial_1_lr_gap = round(jobDetails.gap*100, 2)
                # preciso de manter o lower bound em uma variável.
                # recalcular o gap aqui caso esteja na segunda execução
                # extrair a solução só se for melhor que a prévia.
            case 'INFEASIBLE_SOLUTION':
                if dt.LOG: print('sem solução viável ')
                dt.md_authorial_1_lr_gap = 100
        dt.md_authorial_1_lr_status = jobDetails.status
        if dt.LOG: print('PAROU POR ', dt.md_authorial_1_lr_status)
        
        if dt.LOG: 
            print('fo final: ', dt.md_authorial_1_lr_cost)
            print('tempo de execução: ', dt.md_authorial_1_lr_time )




