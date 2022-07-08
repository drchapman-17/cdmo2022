from time import time
import numpy as np
import os,sys 
import inspect
from pulp import *
import numpy as np
from vlsi_MIP_problem import VLSI_Problem


currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
sys.path.insert(0, currentdir) 
import utils

report=currentdir+"/report_gurobi_rot_2.csv"
# solvername='CPLEX_PY'
solvername='GUROBI'
    
outfile=open(report, 'w')
outfile.write("Instance;Time;Solution\n")
ws=False # Warm Start

for instn in range(1,41):    
    print("SOLVING: ", instn)
    instance = utils.loadInstance(currentdir+f"/../instances/ins-{instn}.txt")
    model=VLSI_Problem(instance,True)
    model.solve(timeLimit=300,verbose=False)
    sol=model.getSolution()
    t=model.getElapsedTime()
    # PRINT OUT THE RESULT 
    print("Time:{}\tSol:{}\n".format(t,sol))
    outfile.write("{};{};{}\n".format(instn,t,sol))
outfile.close()
    