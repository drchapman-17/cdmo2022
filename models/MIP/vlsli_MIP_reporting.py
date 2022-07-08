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

def warmStart(stupidSol,p,q,H,X,Y,R,U):
    n=len(X)
    x_sol=[e[2]-1 for e in stupidSol[1:]]
    y_sol=[e[3]-1 for e in stupidSol[1:]]
    H.setInitialValue(stupidSol[0][1])
    for i in range(n):
        X[i].setInitialValue(x_sol[i])
        Y[i].setInitialValue(y_sol[i])
        for j in range(n):
            if i!=j:
                if x_sol[i]+p[i]<=x_sol[j]:
                    R[i][j].setInitialValue(0)
                    R[j][i].setInitialValue(1)
                if y_sol[i]+q[i]<=y_sol[j]:
                    U[i][j].setInitialValue(0)
                    U[j][i].setInitialValue(1)

report=currentdir+"/report_gurobi_rot.csv"
# solvername='CPLEX_PY'
solvername='GUROBI'
    
outfile=open(report, 'w')
outfile.write("Instance;Time;Solution\n")
ws=False # Warm Start

for instn in range(1,41):    
    print("SOLVING: ", instn)
    instance = utils.loadInstance(currentdir+f"/../instances/ins-{instn}.txt")
    problem=VLSI_Problem(instance)
    model=VLSI_Problem(instance,True)
    model.solve(timeLimit=300,verbose=False)
    sol=model.getSolution()
    t=model.getElapsedTime()
    # PRINT OUT THE RESULT 
    print("Time:{}\tSol:{}\n".format(t,sol))
    outfile.write("{};{};{}\n".format(instn,t,sol))

    """
    #PARAMETERS
    M=1000
    WC=instance["w"]
    n=instance["n"]
    dim=instance['dim']
    p=[i[0] for i in dim]
    q=[i[1] for i in dim]
    largest_idx=np.argmax([p[i]*q[i] for i in range(n)])
    tot_area=sum([w_i*h_i for w_i,h_i in zip(p,q)])
    stupidSol=utils.computeMostStupidSolution(instance)
    Hmin = tot_area/WC
    Hmax=stupidSol[0][1]
    
    # DECISION VARIABLES
    Xl=[] # left boundary of block
    Yb=[] # bottom boundary of block
    R=[] # 0 if block i is to the left of block j
    U=[] # 0 if block i is below block j
    V=[] # rotations

    HC=LpVariable(f"H_c",Hmin,Hmax,LpInteger)
    for i in range(n):
        Xl.append(LpVariable(f"Xl_{i}",0,None,LpInteger))
        Yb.append(LpVariable(f"Yb_{i}",0,None,LpInteger))
        # V.append(LpVariable(f"V_{i}",0,1,LpInteger))
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

    
    # CONSTRAINT REDUCTIONS
    for i in range(n):
        for j in range(n):
            if i!=j:
                if p[i]+p[j]>WC: # Blocks are too wide together, cannot be stacked horizontally
                    R[i][j]=1
            if i<j:
                if p[i]==p[j] and q[i]==p[j]: # Blocks have equal size, arbitrarily fix one to be in the low/left position   
                    R[i][j]=1 
                    U[i][j]=1 
  
    if ws: warmStart(stupidSol,HC,Xl,Yb,R,U) # NON SO SE SERVE PORCODDI
    
    # PROBLEM FORMULATION    
    problem=LpProblem("VLSI_Problem", LpMinimize)

    problem += HC, "Chip_Height"
    problem += 2*Xl[largest_idx]<=WC-p[largest_idx], "Largest_rectangle_Xpos"
    problem += 2*Yb[largest_idx]<=HC-q[largest_idx], "Largest_rectangle_Ypos"
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
            # if p[i]+p[j]>WC:    
            #         problem+= R[i][j]==1,f"B_{i}_{j}_too_large"
            if i<j:
                problem += R[i][j]+R[j][i]+U[i][j]+U[j][i]<=3, f"B_{i}_{j}_at_most_one_rel"                    
                # if p[i]==p[j] and q[i]==p[j]:  
                #         problem+= R[i][j]==1,f"B_{i}_{j}_same_size_r"    
                #         problem+= U[i][j]==1,f"B_{i}_{j}_same_size_u"   

    # BUILD SOLVER
    solver = getSolver(solvername, timeLimit=300,msg=0,warmStart=ws)
    solver.buildSolverModel(problem)
    solver_model = problem.solverModel

    # SOLVE
    if solvername=="CPLEX_PY":  
        start=solver_model.get_time()
    solver.callSolver(problem)
    if solvername=="CPLEX_PY":  
        t=solver_model.get_time()-start
    solver.findSolutionValues(problem)
    sol=None
    
    # RETRIEVE THE SOLUTION
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
    # PRINT OUT THE RESULT 
    print("Time:{}\tSol:{}\n".format(t,sol))
    outfile.write("{};{};{}\n".format(instn,t,sol))
    """    

outfile.close()
    