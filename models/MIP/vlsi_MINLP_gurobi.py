import gurobipy as gp
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
import utils

instance=utils.loadInstance(currentdir+"/../instances/ins-15.txt")


print(*[f" {key} = {val}\n" for key,val in instance.items()])

#PARAMETERS
M=1000
WC=instance["w"]
n=instance["n"]
p=[i[0] for i in instance["dim"]]
q=[i[1] for i in instance["dim"]]
Hmax=sum(q)

m=gp.Model()

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
print(Hmin,Hmax)
HC=m.addVar(vtype="I",name=f"H_c")

for i in range(n):
    W.append(m.addVar(vtype="I",name=f"W_{i}"))
    H.append(m.addVar(vtype="I",name=f"H_{i}"))
    Xl.append(m.addVar(vtype="I",name=f"Xl_{i}"))
    Xr.append(m.addVar(vtype="I",name=f"Xr_{i}"))
    Yt.append(m.addVar(vtype="I",name=f"Yt_{i}"))
    Yb.append(m.addVar(vtype="I",name=f"Yb_{i}"))
    #V.append(m.addVar(vtype="I",name=f"V_{i}"))
    tempR=[]
    tempU=[]
    for j in range(n):
        if i!=j: 
            tempR.append(m.addVar(vtype="I",name=f"R_{i}_{j}"))
            tempU.append(m.addVar(vtype="I",name=f"U_{i}_{j}"))
        else:
            tempR.append(None)
            tempU.append(None)
    R.append(tempR)
    U.append(tempU)

# PROBLEM FORMULATION
m.setObjective(HC, gp.GRB.MINIMIZE)
m.addConstr( HC<=Hmax, name=f"H_max")
m.addConstr( HC>=Hmin, name=f"H_min")
for i in range(n):
    m.addConstr( Xr[i]-Xl[i]==W[i],name=f"B_{i}_boundaries_LR")
    m.addConstr( Yt[i]-Yb[i]==H[i],name=f"B_{i}_boundaries_TB")
    m.addConstr( W[i]==p[i],name=f"B_{i}_width")
    m.addConstr( H[i]==q[i],name=f"B_{i}_heigth")
    m.addConstr( Yt[i]<=HC, name=f"Max_{i}_ytpos")
    m.addConstr( Yt[i]>=q[i], name=f"Min_{i}_ybpos")
    #m.addConstr( W[i]== V[i]*p[i] + (1-V[i])*q[i],name=f"B_{i}_width")
    #m.addConstr( H[i]== (1-V[i])*p[i] + V[i]*q[i],name=f"B_{i}_height")
    for j in range(n):
        m.addConstr( Yt[i]-Yb[j]<=HC, name=f"B_{i}_{j}_height_less_than_chip")
        m.addConstr( Xr[i]-Xl[j]<=WC, name=f"B_{i}_{j}_width_less_than_chip")
        if i!=j:
            m.addConstr( R[i][j]+R[j][i]+U[i][j]+U[j][i]<=3, name=f"B_{i}_{j}_at_most_one_rel")
            m.addConstr( Xr[i]<=Xl[j]+M*R[i][j], name=f"B_{i}_{j}_non_overlap_horizontal")
            m.addConstr( Yt[i]<=Yb[j]+M*U[i][j], name=f"B_{i}_{j}_non_overlap_vertical")
    
    # m.addConstr( Yb[i]+q[i]<=HC, name=f"Max_{i}_ytpos")
    # m.addConstr( Xl[i]+p[i]<=WC, name=f"Max_{i}_ytpos")
    # for j in range(n):
    #     m.addConstr( Yb[i]+q[i]-Yb[j]<=HC, name=f"B_{i}_{j}_height_less_than_chip")
    #     m.addConstr( Xl[i]+p[i]-Xl[j]<=WC, name=f"B_{i}_{j}_width_less_than_chip")
    #     if i!=j:
    #         m.addConstr( R[i][j]+R[j][i]+U[i][j]+U[j][i]<=3, name=f"B_{i}_{j}_at_most_one_rel")
    #         m.addConstr( Xl[i]+p[i]<=Xl[j]+M*R[i][j], name=f"B_{i}_{j}_non_overlap_horizontal")
    #         m.addConstr( Yb[i]+q[i]<=Yb[j]+M*U[i][j], name=f"B_{i}_{j}_non_overlap_vertical")

# Solve it!
m.optimize()

print(f"Optimal height: {m.objVal}")
sol=[[WC,int(HC.X)]]
for i in range(n):
    sol.append([p[i],q[i],int(Xl[i].X)+1,int(Yb[i].X)+1])
print(sol)
utils.show(sol)
