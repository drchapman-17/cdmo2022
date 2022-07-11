from re import S
import pandas as pd
from ctypes import util
import getopt,sys
import datetime
from minizinc import Model,Solver,Instance
import minizinc.error as err
import json
import os
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
import utils


#csv_no_rot=currentdir+'/report_CP.csv'
#csv_rot=currentdir+'/report_rotation_CP.csv'

instance_dir = currentdir+'/'+'../instances'
instance_files = os.listdir(instance_dir)

# reordering 
instance_files_0 = [i for i in instance_files if len(i)==9]
instance_files_1 = [i for i in instance_files if len(i)==10]
instance_files = instance_files_0+instance_files_1

for i in range(len(instance_files)):
    instance_files[i] = instance_dir + '/' + instance_files[i]

vlsi = Model(currentdir + '/' + "vlsi_diffn.mzn")
vlsi_flip = Model(currentdir + '/' + 'vlsi_diffn_flip.mzn')
chuffed=Solver.lookup("chuffed")
timeout = datetime.timedelta(seconds=300)

times = []
solutions = []
times_flip = []
solutions_flip = []

with open(csv_no_rot,"w+") as f:
    f.write("Instance;Time;Solution\n")
with open(csv_rot,"w+") as f:
    f.write("Instance;Time;Solution\n")

for i in range(40):
    inst = utils.loadInstance(instance_files[i])
    instance=Instance(chuffed,vlsi)
    instance_flip = Instance(chuffed, vlsi_flip)
    instance["n"]=inst["n"]
    instance["w"]=inst["w"]
    instance["dim"]=inst["dim"]
    instance_flip["n"]=inst["n"]
    instance_flip["w"]=inst["w"]
    instance_flip["dim"]=inst["dim"]
    print('------------------' + str(i+1) + '------------------')

    try:
        result=instance.solve(timeout=timeout,free_search=True)
        t= result.statistics['time']
        print('time : ', t)
        print('solution :\n', result)
        sol=json.loads(str(result))
        with open(csv_no_rot,"a") as f:
            f.write("{};{};{}\n".format(i+1,t,sol))
    except err.MiniZincError as e:
        print(e)  

    try:
        result_flip=instance.solve(timeout=timeout,free_search=True)
        print('\n--- FLIP ---')
        t=result_flip.statistics['time']
        print('time : ',t)
        print('solution :\n', result_flip)
        sol=json.loads(str(result))
        with open(csv_rot,"a") as f:
            f.write("{};{};{}\n".format(i+1,t,sol))

    except err.MiniZincError as e:
        print(e)
