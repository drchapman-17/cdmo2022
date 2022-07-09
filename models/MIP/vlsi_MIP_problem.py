from ctypes import util
import enum
from operator import indexOf
from pulp import *
import numpy as np
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
sys.path.insert(0, currentdir) 
import utils

class VLSI_Problem():

    def __init__(self,instance,rotationsAllowed=False,initialValues=None):
        self.instance=instance
        self.rotationsAllowed=rotationsAllowed
        #PARAMETERS
        M=1000
        WC=instance["w"]
        n=instance["n"]
        dim=instance['dim']
        p=[i[0] for i in dim]
        q=[i[1] for i in dim]
        largest_idx=np.argmax([p[i]*q[i] for i in range(n)])
        tot_area=sum([w_i*h_i for w_i,h_i in zip(p,q)])
        stupidSol=utils.computeMostStupidSolution(instance,rotationsAllowed=rotationsAllowed)
        if not stupidSol:
            raise Exception("Feasibility check failed: No solution can exist to the problem. The object can not be built.")
        Hmin = tot_area/WC
        Hmax=stupidSol[0][1]
        # DECISION VARIABLES
        W=[] # Width of block
        H=[] # Height of block
        Xl=[] # left boundary of block
        Yb=[] # bottom boundary of block
        R=[] # 0 if block i is to the left of block j
        U=[] # 0 if block i is below block j
        F=[] # rotations
        
        HC=LpVariable(f"H_c",Hmin,Hmax,LpInteger)
        for i in range(n):
            Xl.append(LpVariable(f"Xl_{i}",0,None,LpInteger))
            Yb.append(LpVariable(f"Yb_{i}",0,None,LpInteger))
            if rotationsAllowed:
                W.append(LpVariable(f"W_{i}",0,None,LpInteger))
                H.append(LpVariable(f"H_{i}",0,None,LpInteger))
                F.append(LpVariable(f"F_{i}",0,1,LpInteger))
            else: 
                W.append(p[i])
                H.append(q[i])
                F.append(0)
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
        
        self.variables={
            'HC':HC,
            'X':Xl,
            'Y':Yb,
            'W':W,
            'H':H,
            'R':R,
            'U':U,
            'F':F
        }

        # SET WARM START VALUES
        if initialValues:
            self.__setInitialValues__(initialValues)
        
        # CONSTRAINT REDUCTIONS
        
        for i in range(n):
            if not rotationsAllowed:
                if i!=largest_idx and  p[i]>(WC-p[largest_idx])/2: # Block would occupy the entire area available for the largest block, avoid it 
                    R[i][largest_idx]=1
                for j in range(n):
                    if i!=j and p[i]+p[j]>WC: # Blocks are too wide together, cannot be stacked horizontally
                        R[i][j]=1
            if rotationsAllowed:
                if p[i]==q[i]: # Block is a square, avoid flipping
                    F[i]=0
                    W[i]=p[i]
                    H[i]=q[i]
            if i<j:
                if p[i]==p[j] and q[i]==p[j]: # Blocks have equal size, arbitrarily fix one to be in the low/left position   
                    R[i][j]=1 
                    U[i][j]=1 

        # PROBLEM FORMULATION    
        problem=LpProblem("VLSI_Problem", LpMinimize)

        problem += HC, "Chip_Height"
        problem += 2*Xl[largest_idx]<=WC-p[largest_idx], "Largest_rectangle_Xpos"
        problem += 2*Yb[largest_idx]<=HC-q[largest_idx], "Largest_rectangle_Ypos"
        for i in range(n):
            problem += W[i]==(1-F[i])*p[i] + F[i]*q[i], f"B_{i}_width"
            problem += H[i]==F[i]*p[i] + (1-F[i])*q[i], f"B_{i}_height"
            problem += Yb[i]+H[i]<=HC,  f"Max_{i}_Ypos"
            problem += Xl[i]+W[i]<=WC,  f"Max_{i}_Xpos"
            for j in range(n):
                problem += Xl[i]+W[i]-Xl[j]<=WC,  f"B_{i}_{j}_width_less_than_chip"
                problem += Yb[i]+H[i]-Yb[j]<=HC,  f"B_{i}_{j}_height_less_than_chip"
                if i!=j:
                    problem += Xl[i]+W[i]<=Xl[j]+M*R[i][j], f"B_{i}_{j}_non_overlap_horizontal"
                    problem += Yb[i]+H[i]<=Yb[j]+M*U[i][j], f"B_{i}_{j}_non_overlap_vertical"
                    # problem += W[i]+(1-R[i][j])*W[j]<=WC
                if i<j:
                    problem += R[i][j]+R[j][i]+U[i][j]+U[j][i]<=3, f"B_{i}_{j}_at_most_one_rel"                    

        
        self.problem=problem

    def __setInitialValues__(self,sol):
        if not utils.isFeasible(sol):
            raise Exception("The provided solution is unfeasible!")
        p=[d[0] for d in self.instance['dim']]
        q=[d[1] for d in self.instance['dim']]
        HC=self.variables['HC']
        X=self.variables['X']
        Y=self.variables['Y']
        H=self.variables['H']
        W=self.variables['W']
        R=self.variables['R']
        U=self.variables['U']
        F=self.variables['F']
        n=len(X)
        x_sol=[e[2]-1 for e in sol[1:]]
        y_sol=[e[3]-1 for e in sol[1:]]
        HC.setInitialValue(sol[0][1])
        for i in range(n):
            X[i].setInitialValue(x_sol[i])
            Y[i].setInitialValue(y_sol[i])
            if self.rotationsAllowed:
                if p[i]==sol[i+1][0] and q[i]==sol[i+1][1]:
                    F[i].setInitialValue(0)
                    W[i].setInitialValue(p[i])
                    H[i].setInitialValue(q[i]) 
                else:
                    F[i].setInitialValue(1) 
                    W[i].setInitialValue(q[i])
                    H[i].setInitialValue(p[i]) 
            for j in range(n):
                if i!=j:
                    if x_sol[i]+p[i]<=x_sol[j]:
                        R[i][j].setInitialValue(0)
                        R[j][i].setInitialValue(1)
                    if y_sol[i]+q[i]<=y_sol[j]:
                        U[i][j].setInitialValue(0)
                        U[j][i].setInitialValue(1)

    def __setPriorities__(self):
        solverModel=self.problem.solverModel
        if not self.rotationsAllowed:
            dim=[(d[0],d[1]) for d in self.instance['dim']]
        else: 
            dim=[(min(d[0],d[1]),max(d[0],d[1])) for d in self.instance['dim']]

        varsDict={var.VarName:var for var in solverModel.getVars()}
        # a=sorted(set(dim), key=lambda b:(b[1],b[0])) # Sort by height then width if not rotations, else by longer then shorted side
        # a=sorted(set(dim), key=lambda b:(b[1])) # Sort by height/longer side
        a=sorted(set(dim), key=lambda b:(b[0])) # Sort by width/shorter side
        # a=sorted(set(dim), key=lambda b:(b[1]*b[0])) # Sort by area
        
        # priority=[d[0] for d in dim]
        # varsDict[f"H_c"].setAttr("branchpriority",max(priority)+1)
        # for i in range(self.instance['n']):
        #     varsDict[f"Xl_{i}"].setAttr("branchpriority",priority[i])
        #     varsDict[f"Yb_{i}"].setAttr("branchpriority",priority[i])
        #     if self.rotationsAllowed:
        #         if f"W_{i}" in varsDict.keys():
        #             varsDict[f"W_{i}"].setAttr("branchpriority",priority[i])
        #             varsDict[f"H_{i}"].setAttr("branchpriority",priority[i])
        #             varsDict[f"F_{i}"].setAttr("branchpriority",priority[i])
        #     for j in range(self.instance['n']):
        #         if i!=j:
        #             if f"R_{i}_{j}" in varsDict.keys():
        #                 varsDict[f"R_{i}_{j}"].setAttr("branchpriority",min(priority[i],priority[j])+1)
        #             if f"U_{i}_{j}" in varsDict.keys():
        #                 varsDict[f"U_{i}_{j}"].setAttr("branchpriority",min(priority[i],priority[j])+1)

        varsDict[f"H_c"].setAttr("branchpriority",2*len(a)+1)
        for i in range(self.instance['n']):
            pi=2*indexOf(a,dim[i])    
            print(pi,dim[i],a[int(pi/2)])                    
            varsDict[f"Xl_{i}"].setAttr("branchpriority",pi)
            varsDict[f"Yb_{i}"].setAttr("branchpriority",pi)
            if self.rotationsAllowed:
                if f"W_{i}" in varsDict.keys():
                    varsDict[f"W_{i}"].setAttr("branchpriority",pi)
                    varsDict[f"H_{i}"].setAttr("branchpriority",pi)
                    varsDict[f"F_{i}"].setAttr("branchpriority",pi)
            for j in range(self.instance['n']):
                if i!=j:
                    pj=2*indexOf(a,dim[j])
                    if f"R_{i}_{j}" in varsDict.keys():
                        varsDict[f"R_{i}_{j}"].setAttr("branchpriority",min(pi,pj)+1)
                    if f"U_{i}_{j}" in varsDict.keys():
                        varsDict[f"U_{i}_{j}"].setAttr("branchpriority",min(pi,pj)+1)

    def solve(self,timeLimit=None,verbose=False,ws=False):
        solver = getSolver('GUROBI', timeLimit=timeLimit,msg=verbose,gapRel=0,ws=ws)
        solver.buildSolverModel(self.problem)
        self.__setPriorities__()
        solver.callSolver(self.problem)
        solver.findSolutionValues(self.problem)
        
    def getElapsedTime(self):
        return self.problem.solverModel.RunTime
 
    def getStatusMessage(self):
        return LpStatus[self.problem.status]+ ("(or maybe time-out idk lol)" if self.problem.status==1 else "")
    
    def getStatusCode(self):
        return self.problem.solverModel.status

    def getSolution(self):
        solverModel=self.problem.solverModel
        if solverModel.SolCount > 0:
            vn=[var.VarName for var in solverModel.getVars()]
            vv=[var.X for var in solverModel.getVars()]
            solution=[[self.instance["w"],int(vv[vn.index("H_c")])]]
            for i in range(self.instance["n"]):
                if self.rotationsAllowed and f"W_{i}" in vn:
                        w=int(vv[vn.index(f"W_{i}")])
                        h=int(vv[vn.index(f"H_{i}")])
                else: 
                    w=self.instance['dim'][i][0]
                    h=self.instance['dim'][i][1]
                solution.append([w ,h \
                    ,int(vv[vn.index(f"Xl_{i}")])+1 ,int(vv[vn.index(f"Yb_{i}")])+1])
            return solution    
        else:
            return None

# DEBUG
if __name__=="__main__":
    if len(sys.argv)>1:
        instance=utils.loadInstance(f"instances/ins-{sys.argv[1]}.txt")
    else:
        instance=utils.loadInstance("instances/ins-35.txt")
    stupid=utils.computeMostStupidSolution(instance,True)
    model=VLSI_Problem(instance,False)
    model.solve(timeLimit=300,verbose=True,ws=True)
    sol=model.getSolution()
    print("Time:",model.getElapsedTime() ,"\nSOL:",sol)
    if sol:
        utils.display_solution(sol)
