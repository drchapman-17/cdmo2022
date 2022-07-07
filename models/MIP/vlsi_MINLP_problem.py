from pulp import *

class VLSI_Problem():
    
    def __init__(self,instance,rotationsAllowed=False):
        self.instance=instance 
        #PARAMETERS
        M=1000
        WC=instance["w"]
        n=instance["n"]
        p=[i[0] for i in instance["dim"]]
        q=[i[1] for i in instance["dim"]]
        Hmax=sum(q)

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

        HC=LpVariable(f"H_c",0,Hmax,LpInteger)
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
        self.problem=LpProblem("VLSI_Problem", LpMinimize)

        self.problem += HC, "Chip_Height"
        for i in range(n):
            self.problem += Xr[i]-Xl[i]==W[i], f"B_{i}_boundaries_LR"
            self.problem += Yt[i]-Yb[i]==H[i], f"B_{i}_boundaries_TB"
            if(rotationsAllowed):
                self.problem += W[i]== V[i]*p[i] + (1-V[i])*q[i], f"B_{i}_width"
                self.problem += H[i]== (1-V[i])*p[i] + V[i]*q[i], f"B_{i}_height"
            else:
                self.problem += W[i]==p[i], f"B_{i}_width"
                self.problem += H[i]==q[i], f"B_{i}_heigth"
            for j in range(n):
                self.problem += Yt[i]-Yb[j]<=HC,  f"B_{i}_{j}_height_less_than_chip"
                self.problem += Xr[i]-Xl[j]<=WC,  f"B_{i}_{j}_width_less_than_chip"
                if i!=j:
                    self.problem += R[i][j]+R[j][i]+U[i][j]+U[j][i]<=3, f"B_{i}_{j}_at_most_one_rel"
                    self.problem += Xr[i]<=Xl[j]+M*R[i][j], f"B_{i}_{j}_non_overlap_horizontal"
                    self.problem += Yt[i]<=Yb[j]+M*U[i][j], f"B_{i}_{j}_non_overlap_vertical"

    def solve(self,timeLimit=None,verbose=False):
        self.problem.solve(pulp.PULP_CBC_CMD(timeLimit=timeLimit, msg=1 if verbose else 0, gapRel=0))

    def getStatusMessage(self):
        return LpStatus[self.problem.status]+ ("(or maybe time-out idk lol)" if self.problem.status==1 else "")
    
    def getStatusCode(self):
        return self.problem.status

    def getSolution(self):
        if self.problem.status<0:
            return None
        vn=[var.name for var in self.problem.variables()]
        vv=[var.varValue for var in self.problem.variables()]
        solution=[[self.instance["w"],int(vv[vn.index("H_c")])]]
        for i in range(self.instance["n"]):
            solution.append([int(vv[vn.index(f"W_{i}")]) ,int(vv[vn.index(f"H_{i}")]) \
                ,int(vv[vn.index(f"Xl_{i}")])+1 ,int(vv[vn.index(f"Yb_{i}")])+1])
        return solution
        