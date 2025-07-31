import json
import os, re, math
import numpy as np, random
import pandas as pd
import matplotlib.colors as mcolors
from typing import Literal
GRIDSIZE = 50

class Instance():
    def __init__(self,ni,nj,seed=None):
        self.generate_data(int(ni),int(nj), (seed)) 

    def generate_data(self,ni,nj,K = None, seed = None):
        self.seed = seed or random.randint(10000, 99999)
        np.random.seed(self.seed)
        # assert ni < nj, "number of customer nodes (nj) must be greater than (ni)" 
        # number of plantas, number of customers
        self.ni,self.nj = ni,nj # number of plants and customers
        self.I,self.J = range(ni),range(nj)
        # truck capacity 8 m3
        self.qk = 8 
        self.min_k_value = 8 
        #demands m3
        self.d = np.random.randint(2,48,size=nj)
        # number of trips per customers
        self.L = np.ceil(self.d/self.qk).astype(int)
        remain = self.d - np.floor(self.d/self.qk) * self.qk
        maxL = int(self.L.max())
        
        self.djl = np.zeros((nj,maxL))
        for j in self.J:
            for l in range(self.L[j]-1):
                self.djl[j][l] = self.qk
            self.djl[j][self.L[j]-1] = remain[j]

        # maximum number of trips per truck
        self.R = 5 
        # number of trucks
        self.K = K or int(np.ceil(self.L.sum()/self.R) + 10)

        # set of customers' trips 
        self.Lj = {j : range(int(self.L[j])) for j in self.J}

        # total time 
        self.time_windows = 20
        self.T = 600
        self.vehic_cost = 250
        
        #last_trip = np.random.randint(
        # plants' and customers' coordinates
        self.coordi = np.random.randint(0,GRIDSIZE,size=(ni,2))
        self.coordj = np.random.randint(0,GRIDSIZE,size=(nj,2))
        
        c = self.coordi[:,np.newaxis,:] - self.coordj[np.newaxis,:,:]

        # Euclidean distance matrix
        self.c = np.linalg.norm(c,axis=-1)

        # round to the greatest minute (40 km/h average speed)
        self.t = np.ceil(60 * self.c/40)
        self.cost_matrix = [[2 * self.t[plant][customer] for customer in range(nj)] for plant in range(ni)]

        # input(self.t )
        # first trip [max travel time, latest trip time possible] 
        earliest_trip = np.max(self.t,axis=0)
        # input(earliest_trip)
        # input(self.T - maxL* self.time_windows)
        self.first_trip_arrival = np.random.randint(earliest_trip,self.T - maxL* self.time_windows, size=nj)

        self.A = np.zeros((ni,nj,maxL)).astype(int) 
        self.B = np.zeros((ni,nj,maxL)).astype(int) 
        for i in self.I:
            for j in self.J:
                for l in range(self.L[j]):
                    self.A[i][j][l] = min(self.first_trip_arrival[j] + self.time_windows * l - self.t[i,j], self.T)
                    self.B[i][j][l] = min(self.first_trip_arrival[j] + self.time_windows * (l+1) + self.t[i,j], self.T)
        
        # time_windows opening and closing times
        a = np.zeros((nj, maxL), dtype=int)
        b = np.zeros((nj, maxL), dtype=int)

        for j in self.J:
            for l in range(self.L[j]):
                if l == 0:
                    a[j][l] = int(self.first_trip_arrival[j])
                else:
                    a[j][l] = int(a[j][l-1] + self.time_windows)
                b[j][l] = a[j][l] + self.time_windows

        self.a = a.tolist()
        self.b = b.tolist()

        # plants' capacity
        total_d = self.d.sum()
        plant_capacity = np.ceil(total_d/(10*ni))*10
        self.q = np.full(ni,plant_capacity)

        #self.truck_colors = np.random.uniform(0,.7,size=(self.K,3))
        self.truck_colors = list(mcolors.CSS4_COLORS.values())[10:]
        
        self.md_authorial_solution = None
        self.md_authorial_cost = None
        self.md_authorial_gap = None
        self.md_authorial_time = None
        self.md_authorial_status = None
        self.md_authorial_best_integer = None
        self.md_authorial_nb_nodes = None
        self.md_authorial_1_solution = None
        self.md_authorial_1_cost = None
        self.md_authorial_1_gap = None
        self.md_authorial_1_time = None
        self.md_authorial_1_status = None
        self.md_authorial_1_best_integer = None
        self.md_authorial_1_nb_nodes = None

        self.md_authorial_1_lr_solution = None
        self.md_authorial_1_lr_cost = None
        self.md_authorial_1_lr_gap = None
        self.md_authorial_1_lr_time = None
        self.md_authorial_1_lr_status = None

        self.md_authorial_lr_solution = None
        self.md_authorial_lr_cost = None
        self.md_authorial_lr_gap = None
        self.md_authorial_lr_time = None
        self.md_authorial_lr_status = None
        
        self.md_kinable_gap = None
        self.md_kinable_solution = None
        self.md_kinable_cost = None
        self.md_kinable_time = None
        self.md_kinable_status = None

        self.md_kinable_homo_gap = None
        self.md_kinable_homo_solution = None
        self.md_kinable_homo_cost = None
        self.md_kinable_homo_time = None
        self.md_kinable_homo_status = None
        self.md_kinable_homo_best_integer = None
        self.md_kinable_homo_nb_nodes = None

        self.md_kinable_homo_lr_solution = None
        self.md_kinable_homo_lr_cost = None
        self.md_kinable_homo_lr_gap = None
        self.md_kinable_homo_lr_time = None
        self.md_kinable_homo_lr_status = None

        self.solutions_costs = []
        self.solutions = []
        self.dw_z = []

        # MULTI START
        self.not_meeting_cost = 2 * self.vehic_cost 
        self.step_ordered = []
        self.input_order = []
        self.temp_solution = []
        self.temp_cost = 99999999
        self.temp_q = None
        self.multi_strt_solution = []
        self.multi_strt_time = None
        self.multi_strt_cost = 9999999
        self.trips = []
        self.customers = []
        self.vehicles = []
        self.plants = []
        self.customer_trip_plant = [] # where the trip is attributed
        self.vehicles_per_plant = [ 0 for _ in self.I]
        self.HM_general = [set() for _ in range(self.T)]
        self.HM_plant = [[set() for _ in range(self.T)] for _i in range(i)] # heatmap de cada deposito
        self.tabu_list = []
        self.sorted_cost_by_colum_indices = np.argsort(np.array(self.cost_matrix), axis=0).tolist()
        self.dist_plant_central = None
        self.dist_customer_central = None

    
    def setExecution(self, log = True, time_limit = 3600):
        self.LOG = log
        self.TIME_LIMIT = time_limit
        
    def get_kinable(self, file_path, localLog = False):
        self.T = 500
        with open(file_path, 'r') as file:
            lines = file.readlines()
            storedCustomerTW = 0
            stationPercurredLines = 0
            k_values = []
            self.min_k_value = 9999
            self.max_k_value = 0
            self.d = []
            self.a = []
            self.b = []
            self.locations = {
                'vehicles': {0:(50,50),1:(50,50)},
                'stations': {},
                'customers': {}
            }
            self.qk = []
            self.vehicles_by_capacity = {}
            for line in lines:
                if line.startswith("MaxTimeLag:"):
                    self.time_lag = int(line.split()[1])
                    if localLog: print(f"MaxTimeLag: {self.time_lag}")
                elif line.startswith("Vehicles:"):
                    self.K = int(line.split()[1])
                    if localLog: print(f"Vehicles: {self.K}")
                elif line.startswith("k"):
                    values = list(map(int, line.split()[1:]))
                    self.min_k_value = min(self.min_k_value, *values)
                    if values[0] in self.vehicles_by_capacity: self.vehicles_by_capacity[values[0]] += 1
                    else: self.vehicles_by_capacity[values[0]] = 1
                    self.qk.append(values[0])
                    self.max_k_value = max(self.max_k_value, *values)
                    if localLog: print(f"k values: {values}, min k value: {self.min_k_value}, max k value: {self.max_k_value}")
                elif line.startswith("Customers:"):
                    self.i = int(line.split()[1])
                    if localLog: print(f"Customers: {self.i}")
                elif line.startswith("c"):
                    try:
                        values = list(map(int, line.split()[1:]))
                        if len(values) == 3:
                            self.d.append(values[0])
                            self.a.append(values[1])
                            self.b.append(values[2])
                            if localLog: print(f"c values: {values}, d: {self.d[-1]}, a: {self.a[-1]}, b: {self.b[-1]}")
                        elif len(values) == 2:
                            idx = int(line.split()[0].replace('c',''))
                            x, y = list(map(int, line.split()[1:]))
                            self.locations['customers'][idx] = (x, y)
                            if localLog: print(f"Customer {idx}: location ({x}, {y})")
                    except:
                        if localLog: print('bugou')
                elif line.startswith("Stations:"):
                    self.i = int(line.split()[1])
                    if localLog: print(f"Stations: {self.i}")
                elif line.startswith("s"):
                    try:
                        # input(line)
                        idx = int(line.split()[0].replace('s',''))
                        x, y = list(map(int, line.split()[1:]))
                        self.locations['stations'][idx] = (x, y)
                        if localLog: print(f"Station {idx}: location ({x}, {y})")
                    except: continue
                elif line.startswith("Locations:"):
                    pass  # Skip the "Locations" line
                elif line.startswith("v"):
                    continue
                    idx, x, y = list(map(int, line.split()[1:]))
                    self.locations['vehicles'][idx] = (x, y)
                    if localLog: print(f"Vehicle {idx}: location ({x}, {y})")
                elif line.startswith("c"):
                    pass
                if '-' in line: break
            # input(self.locations)
            # self.qk = self.min_k_value
            self.qk.sort()
            self.c = self.t = [[math.ceil(math.sqrt((self.locations['stations'][plant][0] - self.locations['customers'][customer][0]) ** 2 
                                        + (self.locations['stations'][plant][1] - self.locations['customers'][customer][1]) ** 2))
                                          for customer in range(self.nj)] for plant in range(self.ni)]
            
            self.dist_plant_central = [math.ceil(math.sqrt((self.locations['customers'][plant][0] - self.locations['vehicles'][0][0]) ** 2 +
                                      (self.locations['customers'][plant][1] - self.locations['vehicles'][0][1]) ** 2)) for plant in range(self.ni)]
            self.dist_customer_central = [math.ceil(math.sqrt((self.locations['customers'][customer][0] - self.locations['vehicles'][0][0]) ** 2 +
                                      (self.locations['customers'][customer][1] - self.locations['vehicles'][0][1]) ** 2)) for customer in range(self.nj)]
            
            self.cost_matrix = [[2 * self.t[plant][customer] for customer in range(self.nj)] for plant in range(self.ni)]
            self.sorted_cost_by_colum_indices = np.argsort(np.array(self.cost_matrix), axis=0).tolist()

            self.L = np.ceil(np.array(self.d) / self.min_k_value).astype(int).tolist()
            # Criar o dicionário self.Lj
            self.Lj = {j: range(self.L[j]) for j in range(len(self.L))}
            self.djl = np.zeros((self.nj,int(max(self.L))))
            if self.min_k_value != self.max_k_value: 
                if localLog: print('atribuiu valor mínimo para os veículos, quando variava entre',self.min_k_value,' e ',self.max_k_value)
            d_array = np.array(self.d)
            remain = d_array - np.floor(d_array / self.min_k_value) * self.min_k_value            
            for j in self.J:
                for l in range(self.L[j]):
                    self.djl[j][l] = self.min_k_value
                
                if remain[j]> 0: self.djl[j][self.L[j]-1] = remain[j]
            # input(self.seed)




    def get_greek(self, orders_qnt, number, variationType = 'd'):
        prod2constr_matrix_name = f'cdp_o{orders_qnt}_{number:02d}{variationType}.mat_prod2constr_matrix.csv'
        orders_name = f'cdp_o{orders_qnt}_{number:02d}{variationType}.mat_orders.csv'

        prod2constr_matrix = pd.read_csv(f'./Data/greek/{prod2constr_matrix_name}', header=None)
        orders = pd.read_csv(f'./Data/greek/{orders_name}')
        
        self.ni,self.nj = ni,nj  = 8, orders_qnt # number of plants and customers
        np.random.seed(number)
        self.seed = number
        self.I,self.J = range(ni),range(nj)
        # truck capacity 8 m3
        self.qk = 7.5 
        self.min_k_value = self.qk
        #demands m3
        self.d = orders['OrderedQuantity']
        # input(self.d)
        self.L = np.ceil(self.d/self.qk).astype(int)
        remain = self.d - np.floor(self.d/self.qk) * self.qk
        maxL = int(self.L.max())
        
        self.djl = np.zeros((nj,maxL))
        for j in self.J:
            for l in range(self.L[j]):
                self.djl[j][l] = self.qk
            
            if remain[j]> 0: self.djl[j][self.L[j]-1] = remain[j]

        # maximum number of trips per truck
        self.R = 100

        # number of trucks
        self.K = int(2323.5 / self.qk)
        self.vehicles_by_capacity = {self.qk: self.K}

        # set of customers' trips 
        # input(self.d)
        # input(self.L)
        self.Lj = {j : range(int(self.L[j])) for j in self.J}
        # self.Lj = {str(k): list(v) for k, v in self.Lj.items()}
        
        #last_trip = np.random.randint(
        # plants' and customers' coordinates
        # self.coordi = np.random.randint(0,GRIDSIZE,size=(ni,2))
        # self.coordj = np.random.randint(0,GRIDSIZE,size=(nj,2))
        
        # c = self.coordi[:,np.newaxis,:] - self.coordj[np.newaxis,:,:]
        self.t = [[None for _ in range(nj)] for _ in range(ni)]   
     
        # Euclidean distance matrix
        for customer, row in prod2constr_matrix.iterrows():
            for plant, distance in enumerate(row):
                self.t[plant][customer] = round(distance,2)
        self.cost_matrix = [[2 * self.t[plant][customer] for customer in range(nj)] for plant in range(ni)]
        # input(self.t)
        # round to the greatest minute (40 km/h average speed)
        # self.t = np.ceil(60 * self.c/40)

        maxTravelTime = np.max(np.array(self.t))
        # first trip [max travel time, latest trip time possible]
        orders['ExpectedDeliveryTime'] = pd.to_timedelta(orders['ExpectedDeliveryTime'])
        orders['ExpectedDeliveryTime'] = orders['ExpectedDeliveryTime'].dt.total_seconds()/60
        # total time 
        self.time_windows = 20

        self.T = int(maxTravelTime + max(orders['ExpectedDeliveryTime'] + (self.time_windows) * maxL) )
        # input(self.T)
        # input(maxTravelTime)
        # earliest_trip = np.max(self.t,axis=0)
        # self.a = np.random.randint(earliest_trip,self.T - self.L * self.time_windows, size=nj).tolist()

        earliest_trip = orders['ExpectedDeliveryTime'] - min(orders['ExpectedDeliveryTime']) + maxTravelTime
        latestTrip = max(earliest_trip) or 600

        self.first_trip_arrival = [0]*nj # instante da chegada da primeira entrega no cliente
        for customer in self.J:
            if not orders['ExpectedDeliveryTime'][customer]:
                self.first_trip_arrival[customer] = np.random.randint(0,latestTrip)
            else:
                self.first_trip_arrival[customer] = earliest_trip[customer]
        
        self.A = np.zeros((ni,nj,maxL)).astype(int) 
        self.B = np.zeros((ni,nj,maxL)).astype(int) 
        for i in self.I:
            for j in self.J:
                for l in range(self.L[j]):
                    self.A[i][j][l] = min(self.first_trip_arrival[j] + self.time_windows * l - self.t[i][j], self.T)
                    self.B[i][j][l] = min(self.first_trip_arrival[j] + self.time_windows * (l+1) + self.t[i][j], self.T)
        self.A = self.A.tolist()
        self.B = self.B.tolist()
        
        # time_windows opening and closing times
        a = np.zeros((nj, maxL), dtype=int)
        b = np.zeros((nj, maxL), dtype=int)

        for j in self.J:
            for l in range(self.L[j]):
                if l == 0:
                    a[j][l] = int(self.first_trip_arrival[j])
                else:
                    a[j][l] = int(a[j][l-1] + self.time_windows)
                b[j][l] = a[j][l] + self.time_windows

        self.a = a.tolist()
        self.b = b.tolist()


        # plants' capacity
        total_d = self.d.sum()
        plant_capacity = np.ceil(total_d/(10*ni))*10
        self.q = np.full(ni,plant_capacity)
        
        # MULTI START
        self.HM_general = [set() for _ in range(self.T)]
        self.HM_plant = [[set() for _ in range(self.T)] for _i in self.I] # heatmap de cada deposito
        self.sorted_cost_by_colum_indices = np.argsort(np.array(self.cost_matrix), axis=0).tolist()

        return self
    
    def print(self):
        print(f'number of plants   : {self.ni:>4d}')
        print(f'number of customers: {self.nj:>4d}')
        print(f'truck capacity     : {self.qk:>4d}')
        print(f'number of trucks   : {self.K:>4d}')

    def save_in_json(self, dir: Literal['greek', 'kinable'] , number = 0):
        # Convertendo todos os ndarrays para listas
        # if dir =='kinable': number = number or self.seed
        self.d = [float(x) for x in self.d]  # Converter int64 para int
        self.djl = make_json_serializable(self.djl)
        self.coordi = make_json_serializable(self.coordi)
        self.coordj = make_json_serializable(self.coordj)
        # self.t = self.t.tolist()
        self.cost_matrix = [[2 * self.t[plant][customer] for customer in range(self.nj)] for plant in range(self.ni)]
        # self.a = self.a.tolist()
        # self.A = self.A.tolist()
        # self.B = self.B.tolist()
        self.q = make_json_serializable(self.q)
        trips_data = []
        for customer in self.customers:
            for trip in customer.trips:
                trips_data.append(make_json_serializable(trip)) 
        
        to_save = {
            "ni": make_json_serializable(self.ni),
            "nj": make_json_serializable(self.nj),
            "qk": make_json_serializable(self.qk),
            "min_k_value": make_json_serializable(self.min_k_value),
            "vehicles_by_capacity ": make_json_serializable(self.vehicles_by_capacity ),
            "d": make_json_serializable(self.d),
            "L": make_json_serializable(self.L),
            "djl": make_json_serializable(self.djl),
            # "R": make_json_serializable(self.R),
            "K": make_json_serializable(self.K),
            "Lj": make_json_serializable({str(k): list(v) for k, v in self.Lj.items()}),
            "time_windows": make_json_serializable(self.time_windows),
            "time_lag": make_json_serializable(self.time_lag),
            "T": make_json_serializable(self.T),
            "coordi": make_json_serializable(self.coordi),
            "coordj": make_json_serializable(self.coordj),
            "c": make_json_serializable(self.c),
            "t": make_json_serializable(self.t),
            "cost_matrix": make_json_serializable(self.cost_matrix),
            "first_trip_arrival": make_json_serializable(self.first_trip_arrival),
            "A": make_json_serializable(self.A),
            "B": make_json_serializable(self.B),
            "a": make_json_serializable(self.a),
            "b": make_json_serializable(self.b),
            "q": make_json_serializable(self.q),
            "seed": make_json_serializable(self.seed),
            
            "md_kinable_solution": make_json_serializable(self.md_kinable_solution),
            "md_kinable_cost": make_json_serializable(self.md_kinable_cost),
            "md_kinable_gap": make_json_serializable(self.md_kinable_gap),
            "md_kinable_time": make_json_serializable(self.md_kinable_time),
            "md_kinable_status": make_json_serializable(self.md_kinable_status),
            
            "md_kinable_homo_solution": make_json_serializable(self.md_kinable_homo_solution),
            "md_kinable_homo_cost": make_json_serializable(self.md_kinable_homo_cost),
            "md_kinable_homo_gap": make_json_serializable(self.md_kinable_homo_gap),
            "md_kinable_homo_time": make_json_serializable(self.md_kinable_homo_time),
            "md_kinable_homo_status": make_json_serializable(self.md_kinable_homo_status),
            "md_kinable_homo_best_integer": make_json_serializable(self.md_kinable_homo_best_integer),
            "md_kinable_homo_nb_nodes": make_json_serializable(self.md_kinable_homo_nb_nodes),
            "md_kinable_homo_lr_solution": make_json_serializable(self.md_kinable_homo_lr_solution),
            "md_kinable_homo_lr_cost": make_json_serializable(self.md_kinable_homo_lr_cost),
            "md_kinable_homo_lr_gap": make_json_serializable(self.md_kinable_homo_lr_gap),
            "md_kinable_homo_lr_time": make_json_serializable(self.md_kinable_homo_lr_time),
            "md_kinable_homo_lr_status": make_json_serializable(self.md_kinable_homo_lr_status),
            
            "md_authorial_1_lr_solution": make_json_serializable(self.md_authorial_1_lr_solution),
            "md_authorial_1_lr_cost": make_json_serializable(self.md_authorial_1_lr_cost),
            "md_authorial_1_lr_time": make_json_serializable(self.md_authorial_1_lr_time),
            "md_authorial_1_lr_gap": make_json_serializable(self.md_authorial_1_lr_gap),
            "md_authorial_1_lr_status": make_json_serializable(self.md_authorial_1_lr_status),

            "md_authorial_1_solution": make_json_serializable(self.md_authorial_1_solution),
            "md_authorial_1_cost": make_json_serializable(self.md_authorial_1_cost),
            "md_authorial_1_time": make_json_serializable(self.md_authorial_1_time),
            "md_authorial_1_gap": make_json_serializable(self.md_authorial_1_gap),
            "md_authorial_1_status": make_json_serializable(self.md_authorial_1_status),
            "md_authorial_1_best_integer": make_json_serializable(self.md_authorial_1_best_integer),
            "md_authorial_1_nb_nodes": make_json_serializable(self.md_authorial_1_nb_nodes),
            
            "md_authorial_solution": make_json_serializable(self.md_authorial_solution),
            "md_authorial_cost": make_json_serializable(self.md_authorial_cost),
            "md_authorial_time": make_json_serializable(self.md_authorial_time),
            "md_authorial_gap": make_json_serializable(self.md_authorial_gap),
            "md_authorial_status": make_json_serializable(self.md_authorial_status),
            "md_authorial_best_integer": make_json_serializable(self.md_authorial_best_integer),
            "md_authorial_nb_nodes": make_json_serializable(self.md_authorial_nb_nodes),

            "md_authorial_lr_solution": make_json_serializable(self.md_authorial_lr_solution),
            "md_authorial_lr_cost": make_json_serializable(self.md_authorial_lr_cost),
            "md_authorial_lr_gap": make_json_serializable(self.md_authorial_lr_gap),
            "md_authorial_lr_time": make_json_serializable(self.md_authorial_lr_time),
            "md_authorial_lr_status": make_json_serializable(self.md_authorial_lr_status),

            # MLTSTRT
            "not_meeting_cost": make_json_serializable(self.not_meeting_cost),
            "step_ordered": make_json_serializable(self.step_ordered),
            "input_order": make_json_serializable(self.input_order),
            "temp_solution": make_json_serializable(self.temp_solution),
            "temp_cost": make_json_serializable(self.temp_cost),
            "temp_q": make_json_serializable(self.temp_q),
            "multi_strt_solution": make_json_serializable(self.multi_strt_solution),
            "multi_strt_cost": make_json_serializable(self.multi_strt_cost),
            "multi_strt_time": make_json_serializable(self.multi_strt_time),
            "customer_trip_dep": make_json_serializable(self.customer_trip_plant),
            "vehicles_per_plant": make_json_serializable(self.vehicles_per_plant),
            # "HM_general": make_json_serializable(self.HM_general),
            # "HM_plant": make_json_serializable(self.HM_plant),
            # "tabu_list": make_json_serializable(self.tabu_list),
            "sorted_cost_by_colum_indices": make_json_serializable(self.sorted_cost_by_colum_indices),
            "dist_plant_central": make_json_serializable(self.dist_plant_central),
            "dist_customer_central": make_json_serializable(self.dist_customer_central),

            'multi_strt_trips': trips_data
            
        }

        filename = f'./Insts/{dir}/inst_{self.ni}_{self.nj}_{self.K}_{number}.json'
        os.makedirs(os.path.dirname(filename), exist_ok=True)  # Cria o diretório se não existir
        # print(os.listdir())
        with open(filename, 'w') as json_file:
            json_file.write(json.dumps(to_save, indent=4))  # indent para facilitar a leitura, opcional
            print(filename)
    
    def from_json(self, json_data):

        self.ni = json_data['ni']
        self.nj = json_data['nj']
        self.qk = json_data['qk']
        self.min_k_value = json_data['min_k_value']
        self.vehicles_by_capacity  = json_data['vehicles_by_capacity ']
        self.d = np.array(json_data['d'])
        self.L = np.array(json_data['L'])
        self.djl = np.array(json_data['djl'])
        # self.R = json_data['R']
        self.K = json_data['K']
        self.Lj = {int(k): range(len(v)) for k, v in json_data['Lj'].items()}
        self.time_windows = json_data['time_windows']
        self.T = json_data['T']
        self.coordi = np.array(json_data['coordi'])
        self.coordj = np.array(json_data['coordj'])
        self.c = np.array(json_data['c'])
        self.t = np.array(json_data['t'])
        self.cost_matrix = np.array(json_data['cost_matrix'])
        self.first_trip_arrival = np.array(json_data['a'])
        self.A = np.array(json_data['A'])
        self.B = np.array(json_data['B'])
        self.a = np.array(json_data['a'])
        self.b = np.array(json_data['b'])
        self.q = np.array(json_data['q'])
        self.time_lag = json_data['time_lag']
        
        self.md_kinable_gap = json_data['md_kinable_gap']
        self.md_kinable_solution = json_data['md_kinable_solution']
        self.md_kinable_cost = json_data['md_kinable_cost']
        self.md_kinable_time = json_data['md_kinable_time']
        self.md_kinable_status = json_data['md_kinable_status']
        

        self.md_kinable_homo_gap = json_data['md_kinable_homo_gap']
        self.md_kinable_homo_solution = json_data['md_kinable_homo_solution']
        self.md_kinable_homo_cost = json_data['md_kinable_homo_cost']
        self.md_kinable_homo_time = json_data['md_kinable_homo_time']
        self.md_kinable_homo_status = json_data['md_kinable_homo_status']
        self.md_kinable_homo_best_integer = json_data['md_kinable_homo_best_integer']
        self.md_kinable_homo_nb_nodes = json_data['md_kinable_homo_nb_nodes']
        self.md_kinable_homo_lr_solution = json_data['md_kinable_homo_lr_solution']
        self.md_kinable_homo_lr_cost = json_data['md_kinable_homo_lr_cost']
        self.md_kinable_homo_lr_gap = json_data['md_kinable_homo_lr_gap']
        self.md_kinable_homo_lr_time = json_data['md_kinable_homo_lr_time']
        self.md_kinable_homo_lr_status = json_data['md_kinable_homo_lr_status']

        self.md_authorial_gap = json_data['md_authorial_gap']
        self.md_authorial_solution = json_data['md_authorial_solution']
        self.md_authorial_cost = json_data['md_authorial_cost']
        self.md_authorial_time = json_data['md_authorial_time']
        self.md_authorial_status = json_data['md_authorial_status']
        self.md_authorial_best_integer = json_data['md_authorial_best_integer']
        self.md_authorial_nb_nodes = json_data['md_authorial_nb_nodes']
        
        self.md_authorial_1_gap = json_data['md_authorial_1_gap']
        self.md_authorial_1_solution = json_data['md_authorial_1_solution']
        self.md_authorial_1_cost = json_data['md_authorial_1_cost']
        self.md_authorial_1_time = json_data['md_authorial_1_time']
        self.md_authorial_1_status = json_data['md_authorial_1_status']
        self.md_authorial_1_best_integer = json_data['md_authorial_1_best_integer']
        self.md_authorial_1_nb_nodes = json_data['md_authorial_1_nb_nodes']
        
        try:
            self.md_authorial_1_lr_gap = json_data['md_authorial_1_lr_gap']
            self.md_authorial_1_lr_solution = json_data['md_authorial_1_lr_solution']
            self.md_authorial_1_lr_cost = json_data['md_authorial_1_lr_cost']
            self.md_authorial_1_lr_time = json_data['md_authorial_1_lr_time']
            self.md_authorial_1_lr_status = json_data['md_authorial_1_lr_status']
        except:
            self.md_authorial_1_lr_gap = None
            self.md_authorial_1_lr_solution = None
            self.md_authorial_1_lr_cost = None
            self.md_authorial_1_lr_time = None
            self.md_authorial_1_lr_status = None

        self.md_authorial_lr_solution = json_data['md_authorial_lr_solution']
        self.md_authorial_lr_cost = json_data['md_authorial_lr_cost']
        self.md_authorial_lr_gap = json_data['md_authorial_lr_gap']
        self.md_authorial_lr_time = json_data['md_authorial_lr_time']
        self.md_authorial_lr_status = json_data['md_authorial_lr_status']

        self.step_ordered = json_data['step_ordered']
        self.input_order = json_data['input_order']
        self.temp_solution = json_data['temp_solution']
        self.temp_cost = json_data['temp_cost']
        self.temp_q = json_data['temp_q']
        self.customer_trip_plant = json_data['customer_trip_dep']
        self.dist_plant_central = json_data['dist_plant_central']
        self.dist_customer_central = json_data['dist_customer_central']
        # self.vehicles_per_plant = json_data['vehicles_per_plant']

        self.sorted_cost_by_colum_indices = json_data['sorted_cost_by_colum_indices']
        

def get_inst_parameters(number, dir: Literal['greek', 'kinable']):
    files = os.listdir(f'./Insts/{dir}/')
    files.sort()
    file = files[number-1]
    i_j_k_seed = re.findall(r'\d+', file)
    i_j_k_seed = [int(valor) for valor in i_j_k_seed]

    return tuple(i_j_k_seed)

def get_data(inst_number,  dir: Literal['greek', 'kinable']):
    i, j, k, seed = get_inst_parameters(inst_number, dir)
    # print(i, j, k, seed)
    # try:
    dat = Instance(i, j)
    file = f'./Insts/{dir}/inst_{i}_{j}_{k}_{seed}.json'
    if dir =='kinable': file = f'./Insts/{dir}/inst_{i}_{j}_{k}_{0}.json'
    with open(file, 'r') as file:
        dados = json.load(file)
    # Verificação básica dos dados carregados do JSON
    if isinstance(dados, dict):
        dat.from_json(dados)
        # setBounds(dat)
        dat.seed = seed
        if dir =='kinable': dat.seed = 0
    else:
        raise ValueError("O arquivo JSON não contém dados no formato esperado.")
    return dat
    # except FileNotFoundError:
    #     print(f"Arquivo ./Insts/{dir}inst_{i}_{j}_{k}_{seed}.json não encontrado.")
    #     return None
    # except json.JSONDecodeError:
    #     print(f"Erro ao decodificar o arquivo JSON ./Insts/py/inst_{i}_{j}_{k}_{seed}.json.")
    #     return None
    # except Exception as e:
    #     print(f"Arquivo ./Insts/{dir}inst_{i}_{j}_{k}_{seed}.json não encontrado.")
    #     print(f"Ocorreu um erro inesperado: {e}")
    #     return None
    
def listInsts( dir: Literal['greek', 'kinable'] , log = True, exit_after = False):
    files = os.listdir(f'./Insts/{dir}/')
    files.sort()
    
    for idx, file in enumerate(files):
        if log: print(f'{idx + 1} - {file}')
    if exit_after: exit()
    return len(files)

def f(dt: Instance, solution):
    cost = 0
    plants = [[] for _ in dt.I]
    customers_served = [1 for _ in dt.J]
    for (i, j, k, l,s ) in solution:
        cost+= dt.cost_matrix[i][j]
        customers_served[j] = 0
        if k not in plants[i]:
            plants[i].append(k)
    vehicles_per_plant = []
    for i in plants:
        vehicles_per_plant.append(len(i))
    unserved_trips = 0
    for idx, unserved_customer in enumerate(customers_served) :
        unserved_trips += dt.L[idx] * unserved_customer
    total_cost = cost + sum(vehicles_per_plant) * dt.vehic_cost + dt.not_meeting_cost * unserved_trips
    return total_cost, cost, sum(vehicles_per_plant), unserved_trips

def plant_consumption(dt: Instance, solution):
    consumption = [0]*dt.ni
    for (i, j, k, l,s ) in solution:
        consumption[i]+= dt.djl[j][l]
    return consumption

def vehicles_per_plant(dt: Instance, solution):
    plants = [[] for _ in dt.I]
    for (i, j, k, l, s ) in solution:
        if k not in plants[i]:
            plants[i].append(k)
    vehicles_per_plant = []
    for i in plants:
        vehicles_per_plant.append(len(i))
    return vehicles_per_plant

def setBounds(dt: Instance):
    wosrtPlants = [[0 for _ in range(dt.T)] for _i in dt.I] # heatmap de cada deposito
    bestPlants = [0 for _ in range(dt.T)]
    bestCost = 0
    for customer in dt.J:
        worstPlant = dt.sorted_cost_by_colum_indices[-1][customer]
        bestPlant = dt.sorted_cost_by_colum_indices[0][customer]

        for trip in dt.Lj[customer]:
            worstOpening = dt.A[worstPlant][customer][trip]
            worstClosing = worstOpening + 2* dt.t[worstPlant][customer]
            for i in range(worstOpening, worstClosing):
                wosrtPlants[worstPlant][i] += 1
            
            bestOpening = dt.A[bestPlant][customer][trip]
            bestClosing = bestOpening + 2* dt.t[bestPlant][customer]
            for instant in range(bestOpening, bestClosing):
                bestPlants[instant] += 1

            bestCost += dt.cost_matrix[bestPlant][customer]


    dt.total_vehics_max = 0
    for i in dt.I:
        dt.total_vehics_max += max(wosrtPlants[i])
    
    # dt.total_vehics_min = max(bestPlants)
    # dt.bestCost = bestCost + dt.total_vehics_min * dt.vehic_cost
    # print(dt.total_vehics_max, dt.total_vehics_min, dt.bestCost)



from datetime import datetime
from decimal import Decimal

def make_json_serializable(obj):
    """
    Verifica se um objeto é serializável em JSON e, se não for,
    converte as partes problemáticas para que sejam.
    """
    try:
        json.dumps(obj)
        return obj
    except TypeError:
        if isinstance(obj, dict):
            return {key: make_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [make_json_serializable(item) for item in obj]
        elif isinstance(obj, set):
            return [make_json_serializable(item) for item in obj]
        elif isinstance(obj, tuple):
            return tuple(make_json_serializable(item) for item in obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.int64):
            return int(obj)
        elif hasattr(obj, '__dict__'):
            return make_json_serializable(obj.__dict__)
        else:
            return str(obj)
