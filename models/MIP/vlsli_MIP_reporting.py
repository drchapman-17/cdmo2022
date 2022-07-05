from time import time
import numpy as np
import os,sys 
import inspect
import getopt
from pulp import *
import numpy as np

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
sys.path.insert(0, currentdir) 
import utils

report=currentdir+"/report_gurobi_2lb.txt"
outfile=open(report, 'w')
outfile.write("REPORT:\n\n")

for instn in range(1,19):
    print("SOLVING: ", instn)
    instance = utils.loadInstance(currentdir+f"/../instances/ins-{instn}.txt")
 
    #PARAMETERS
    M=1000
    WC=instance["w"]
    n=instance["n"]
    p=[i[0] for i in instance["dim"]]
    q=[i[1] for i in instance["dim"]]

    # DECISION VARIABLES
    W=[] # Width of block
    H=[] # Height of block
    Xl=[] # left boundary of block
    Xr=[] # right boundary of block
    Yt=[] # top boundary of block
    Yb=[] # bottom boundary of block
    R=[] # 0 if block i is to the left of block j
    U=[] # 0 if block i is below block j
    V=[] # rotations
    tot_area=sum([w_i*h_i for w_i,h_i in zip(p,q)])
    Hmin = tot_area/WC
#    Hmax=sum(q)
    Hmax = 2*max(max([[d[0],d[1]] for d in zip(p,q)], key=lambda d:d[0]*d[1])[1],Hmin)+1
    print(Hmax)
    biggest_i=np.argmax([p[i]*q[i] for i in range(n)])

    HC=LpVariable(f"H_c",Hmin,Hmax,LpInteger)
    for i in range(n):
        W.append(LpVariable(f"W_{i}",0,None,LpInteger))
        H.append(LpVariable(f"H_{i}",0,None,LpInteger))
        Xl.append(LpVariable(f"Xl_{i}",0,None,LpInteger))
        Xr.append(LpVariable(f"Xr_{i}",0,None,LpInteger))
        Yt.append(LpVariable(f"Yt_{i}",0,None,LpInteger))
        Yb.append(LpVariable(f"Yb_{i}",0,None,LpInteger))
        V.append(LpVariable(f"V_{i}",0,1,LpInteger))
        tempR=[]
        tempU=[]
        for j in range(n):
            if i!=j: 
                tempR.append(LpVariable(f"R_{i}_{j}",0,1,LpInteger))
                tempU.append(LpVariable(f"U_{i}_{j}",0,1,LpInteger))
            else:
                tempR.append(None)
                tempU.append(None)
        R.append(tempR)
        U.append(tempU)

    # PROBLEM FORMULATION    
    problem=LpProblem("VLSI_Problem", LpMinimize)

    problem += HC, "Chip_Height"
    #  problem += HC*WC-tot_area >=0 ,"Empty_space"
    problem += 2*Xl[biggest_i]<=WC-p[biggest_i], "Largest_rectangle_Xpos"
    problem += 2*Yb[biggest_i]<=HC-q[biggest_i], "Largest_rectangle_Ypos"
    for i in range(n):
        problem += Yb[i]+q[i]<=HC,  f"Max_{i}_Ypos"
        #problem += W[i]== V[i]*p[i] + (1-V[i])*q[i], f"B_{i}_width"
        #problem += H[i]== (1-V[i])*p[i] + V[i]*q[i], f"B_{i}_height"
        for j in range(n):
            problem += Xl[i]+p[i]-Xl[j]<=WC,  f"B_{i}_{j}_width_less_than_chip"
            problem += Yb[i]+q[i]-Yb[j]<=HC,  f"B_{i}_{j}_height_less_than_chip"

            if i!=j:
                problem += Xl[i]+p[i]<=Xl[j]+M*R[i][j], f"B_{i}_{j}_non_overlap_horizontal"
                problem += Yb[i]+q[i]<=Yb[j]+M*U[i][j], f"B_{i}_{j}_non_overlap_vertical"
                if p[i]+p[j]>WC:
                    problem+= R[i][j]==1,f"B_{i}_{j}_too_large"
            if i<j:
                problem += R[i][j]+R[j][i]+U[i][j]+U[j][i]<=3, f"B_{i}_{j}_at_most_one_rel"                    
                if p[i]==p[j] and q[i]==p[j]:  
                        problem+= R[i][j]==1,f"B_{i}_{j}_same_size_r"    
                        problem+= U[i][j]==1,f"B_{i}_{j}_same_size_u"   



    solvername='CPLEX_PY'
    solvername='GUROBI'
    
    #Build the solverModel for your preferred
    solver = getSolver(solvername, timeLimit=300,msg=0)
    solver.buildSolverModel(problem)
    solver_model = problem.solverModel

    #Solve P
    if solvername=="CPLEX_PY":  
        start=solver_model.get_time()
    solver.callSolver(problem)
    if solvername=="CPLEX_PY":  
        t=solver_model.get_time()-start
    solver.findSolutionValues(problem)
    sol=None
    # retrieve the objective value of the best integer solution
    if solvername=="GUROBI":
        if solver_model.Status == 2:
            h = value(problem.objective)
            sol=[[WC,int(HC.value())]]+[[p[i],q[i],round(Xl[i].value())+1,round(Yb[i].value())+1] for i in range(n)]
        elif solver_model.SolCount > 0:  # for the case of MIP
            h = solver_model.PoolObjVal
        else:
            problem.roundSolution()
            h = value(problem.objective)
        t=solver_model.RunTime

    if solvername=="CPLEX_PY":
        h = value(problem.objective)
        sol=[[WC,int(HC.value())]]+[[p[i],q[i],round(Xl[i].value())+1,round(Yb[i].value())+1] for i in range(n)]
    
     
    print("Time:{}\tSol:{}\n".format(t,sol))
    outfile.write("Instance:{}\tTime:{}\tSol:{}\n".format(instn,t,sol))
outfile.close()
    