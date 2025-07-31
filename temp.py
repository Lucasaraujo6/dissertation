import data, os, pandas as pd, re, random

if __name__ == '__main__':
     author = 'kinable'
     doneA = doneB = 0
     hard = worst = avg = 0
     total = data.listInsts(author, log=False)
     for  insNumber in range(1, 1+total):
          
          i, j, k, seed = data.get_inst_parameters(insNumber, author)
          dt = data.get_data(insNumber, author)
          # print(i, j, k)
          if dt.md_authorial_1_cost:
               if j <= 20 and k<=5:
                    doneA+=1
               else:
                    try:
                         avg += dt.md_authorial_1_lr_time
                         doneB+=1
                    except:
                         print('jump 1',i,j,k)
                         pass
               try:
                    if dt.md_authorial_1_cost+1< dt.md_kinable_homo_cost:
                         print(i,j,k,dt.md_authorial_1_cost,'vs', dt.md_kinable_homo_cost)
                         worst +=1

               except:
                    print('jump 2')
                    pass
          elif j >=20 and k>5 and i >2:
               hard+=1
          
     print(doneA,' + ',doneB,' de ', total,' faltam: ', total-doneA-doneB, ' ou ',64-doneA,' + ',128-doneB)
     print('avg : ', avg/(doneB))
     print('hard: ', hard)
     print('worst: ', worst)