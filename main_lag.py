import data, os, pandas as pd, re, random
from model import authorial_1,authorial_1_lr,kinable_homo,kinable_homo_lr
import sys, datetime, copy, time
# https://www.ibm.com/docs/en/icos/12.9.0?topic=model-output-tabs

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
    count = 0
    for idx,file in enumerate(files):
        # if (not "20_4." in file
        #  and not "30_3." in file
        #  and not "40_2." in file
        #  and not "50_1." in file):
            # continue
        # print(idx,' - ',file)
        count+=1
        # continue
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
    print(count)
    exit()

            
if __name__ == '__main__':
    # main()
    author = 'kinable'
    # data.listInsts(author, exit_after = True)
    
    # generate_from_greek()
    # generate_from_kinable(folder='setB')
    # generate_from_kinable()
    # data.listInsts('kinable')
    # exit()

    instances = list(range(data.listInsts(author, log=False)))
    
    count = 0
    current_pid = os.getpid()
    os.system(f"ps -ef | grep python3 | grep -v grep | awk '{{if ($2 != {current_pid}) print $2}}' | xargs -r kill -9")


    while instances:
        print(f'instances left: {len(instances)}')
        insNumber = instances.pop(random.randint(0,len(instances))-1) +1
        i, j, k, seed = data.get_inst_parameters(insNumber, author)
        # input(f'inst {insNumber} {datetime.datetime.now()}')


        dt = data.get_data(insNumber, author)
        # if dt.md_kinable_homo_cost is not None: continue
        print(f'\n\ninst {insNumber} {datetime.datetime.now()}')
        print(i, j, k)
        count+=1
        # if count<7: continue
        dt.setExecution(time_limit=3600)


        if dt.md_authorial_1_cost is None: 
            md = authorial_1_lr.md(dt)
            md.run(dt)
            dt.save_in_json('kinable')
            md = authorial_1.md(dt)
            md.run(dt)
            dt.save_in_json('kinable')
        if dt.md_kinable_homo_cost is None: 
            md = kinable_homo_lr.md(dt)
            md.run(dt)
            dt.save_in_json('kinable')
            md = kinable_homo.md(dt)
            md.run(dt)
            dt.save_in_json('kinable')

        
        print("dt.md_kinable_homo_cost",dt.md_kinable_homo_cost, 'time: ',round(dt.md_kinable_homo_time,2),'gap: ',dt.md_kinable_homo_gap)
        print("dt.md_authorial_cost",dt.md_authorial_1_cost,'time: ',round(dt.md_authorial_1_time,2),'gap: ',dt.md_authorial_1_gap)
        print(i, j, k)



       
