import data, os, pandas as pd, re
from model import kinable, authorial,authorial_1,kinable_homo, authorial_lr,kinable_homo_lr
import sys, datetime, copy, time
# https://www.ibm.com/docs/en/icos/12.9.0?topic=model-output-tabs
from model import kinable, authorial,kinable_homo, authorial_lr,kinable_homo_lr

homogeneousInsts = [(2,5,1),(2,5,2),(2,5,3),(2,5,4),(2,10,1),(2,10,3),(2,15,1),
    (2,20,2),(2,20,3),(3,5,3),(3,5,4),(3,10,1),(3,10,4),(3,15,1),
    (3,15,4),(3,20,1),(4,15,4),(4,20,2),(5,5,1),(5,5,4),(5,15,3), 
    (5,20,3),(6,20,4),(6,40,3),(8,40,2),(8,50,1),(10,40,3),(10,50,2),
    (12,30,4),(14,30,1),(16,20,2),(16,30,4),(16,40,4),(20,20,2),
    (20,40,1),(20,50,4)]

def get_unique_combinations(directory):
    pattern = re.compile(r'cdp_o(\d+)_(\d{2})(\w+)\.mat')
    combinations = set()

    for filename in os.listdir(directory):
        match = pattern.search(filename)
        if match:
            orders_qnt = int(match.group(1))
            number = int(match.group(2))
            variationType = match.group(3)
            combinations.add((orders_qnt, number, variationType))

    return list(combinations)

def generate_from_greek():
    directory = './Data/greek/'
    unique_combinations = get_unique_combinations(directory)
    unique_combinations.sort(key=lambda x: (x[0], x[1], x[2]))
    # print(len(unique_combinations))
    for idx,( orders_qnt, number, variationType) in enumerate(unique_combinations):
        print(idx, unique_combinations[idx])
        if idx == 178: continue #bugou a 178: (45, 8, 'd')
        # if idx > 0: break #bugou a 178: (45, 8, 'd')
        qnt_plants = 8
        dt = data.Instance(qnt_plants, orders_qnt, seed=number)
        dt.get_greek(orders_qnt, number, variationType)
        dt.save_in_json('greek',number = number)


def generate_from_kinable(folder ='setA'):
    directory = f'./Data/kinable/{folder}/'
    files = os.listdir(directory)
    files.sort()
    for idx,file in enumerate(files):
        print(idx,' - ',file)
        # continue
        input
        # if idx >0 : break
        file_set, vehicles, customers, plant = file.split('_')
        # if not '3' in str(vehicles)  or not '5' in str(customers)  or not '3' in str(plant): continue
        # if  not '5' in str(customers) : continue
        plant = plant.replace('.rmc','')
        # if int(customers) > 5: continue
        currFile = directory + file
        dt = data.Instance(int(plant), int(customers) )
        dt.get_kinable(currFile)
        dt.save_in_json(dir = 'kinable')
        # input(f'{file_set}, {vehicles}, {customers}, {plant}')
        # dt = data.Data(qnt_plants, orders_qnt)
        # dt.get_kinable(orders_qnt, number, variationType)
        # dt.save_in_json(number = number)
    exit()

            
if __name__ == '__main__':
         # main()
    author = 'kinable'
    # data.listInsts(author, exit_after = True)
    
    # generate_from_greek()
    # generate_from_kinable(folder='setB')
    # generate_from_kinable()

    instances = data.listInsts(author, log=False)
    temp = True
    count = 0
    total_auth = 0
    total_kin = 0
    total_kin2 = 0
    auth_melhor = 0
    kin_melhor = 0
    for insNumber in range(1,instances+1):
                
        i, j, k, seed = data.get_inst_parameters(insNumber, author)
        # if (i, j, k) != (2, 20, 2): continue
        if (i, j, k) != (4, 15, 5): continue
        # if (i, j, k) != (1, 50, 12): continue

        print((i, j, k))
        
        dt = data.get_data(insNumber, author)
        dt.setExecution(time_limit=3600)
        md = authorial_1.md(dt)
        md.run(dt)

       
