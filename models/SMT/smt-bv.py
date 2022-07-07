from math import log2
from socket import timeout
from z3 import *

from time import time
import numpy as np
import os,sys 
import inspect
import getopt
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
sys.path.insert(0, currentdir) 
import utils

# ROBA RUBATA
def z3_cumulative(start, duration, resources, total):

    decomposition = []
    for u in resources:
        decomposition.append(
            sum([If(And(start[i] <= u, u < start[i] + duration[i]), resources[i], 0)
                 for i in range(len(start))]) <= total
        )
    return decomposition

def format_solution(m, o, dim, n, W):

    schema = []
    if m != None:
        nicer = sorted ([(d, m[d]) for d in m], key = lambda x: str(x[0]))
        dict = {str(l[0]):l[1] for l in nicer if str(l[0]).startswith("x__") or str(l[0]).startswith("y__")}

        blockpos = []
        for i in range(n):
            blockpos.append([int(str(dict['x__{}'.format(i)]))+1,int(str(dict['y__{}'.format(i)]))+1])

        schema = [[W,o]]

        for i in range(n):
            schema.append([*dim[i], *blockpos[i]])

    return schema

# def distinct_coordinates(Xs, Ys, W, n):
    
#     diff = [ W*Xs[i]+Ys[i]  for i in range(n)]

#     return Distinct(diff)

def boundary_constraints(Xs, Ys, Ws, Hs, W, d, n):

    x_width = [ Xs[i] + Ws[i] <= W for i in range(n)]
    y_height = [ Ys[i] + Hs[i] <= d for i in range(n)]
    x_morethan_0 = [ Xs[i] >= 0 for i in range(n)]
    y_morethan_0 = [ Ys[i] >= 0 for i in range(n)]

    return [*x_width, *y_height, *x_morethan_0, *y_morethan_0]

# def no_overlap(Xs, Ys, Xij, Yij, Ws, Hs, W, H, n):
#     no_1 = [ Xs[i] + Ws[i] <= Xs[j] + W*(Xij[i*n+j] + Yij[i*n+j]) for i in range(n) for j in range(n) if i<j ]
#     no_2 = [ Xs[i] - Ws[j] >= Xs[j] - W*(1 - Xij[i*n+j] + Yij[i*n+j]) for i in range(n) for j in range(n) if i<j ]
#     no_3 = [ Ys[i] + Hs[i] <= Ys[j] + H*(1 + Xij[i*n+j] - Yij[i*n+j]) for i in range(n) for j in range(n) if i<j ]
#     no_4 = [ Ys[i] - Hs[j] >= Ys[j] - H*(2 - Xij[i*n+j] - Yij[i*n+j]) for i in range(n) for j in range(n) if i<j ]
#     return [*no_1,*no_2,*no_3,*no_4]

def no_overlap(Xs, Ys, Ws, Hs, W, H, n):
    no = [ Or(
                And(
                    Xs[i] + Ws[i] <= Xs[j], 
                    Xs[i] - Ws[j] >= Xs[j] - W, 
                    Ys[i] + Hs[i] <= Ys[j] + H, 
                    Ys[i] - Hs[j] >= Ys[j] - 2*H),
                And(
                    Xs[i] + Ws[i] <= Xs[j] + W, 
                    Xs[i] - Ws[j] >= Xs[j] - 2*W, 
                    Ys[i] + Hs[i] <= Ys[j], 
                    Ys[i] - Hs[j] >= Ys[j] - H),
                And(
                    Xs[i] + Ws[i] <= Xs[j] + W, 
                    Xs[i] - Ws[j] >= Xs[j], 
                    Ys[i] + Hs[i] <= Ys[j] + 2*H, 
                    Ys[i] - Hs[j] >= Ys[j] - H),
                And(
                    Xs[i] + Ws[i] <= Xs[j] + 2*W, 
                    Xs[i] - Ws[j] >= Xs[j] - W, 
                    Ys[i] + Hs[i] <= Ys[j] + H, 
                    Ys[i] - Hs[j] >= Ys[j])
                ) for i in range(n) for j in range(n) if i!=j ]

    return no

def reduce_domain_largest_rectangle(Xs, Ys, Ws, Hs, W, H, n):
    no = [ Or(
                And(
                    Xs[i] - Ws[j] >= Xs[j] - W, 
                    Ys[i] + Hs[i] <= Ys[j] + H, 
                    Ys[i] - Hs[j] >= Ys[j] - 2*H),
                And(
                    Xs[i] - Ws[j] >= Xs[j] - 2*W, 
                    Ys[i] + Hs[i] <= Ys[j], 
                    Ys[i] - Hs[j] >= Ys[j] - H),
                And(
                    Xs[i] - Ws[j] >= Xs[j], 
                    Ys[i] + Hs[i] <= Ys[j] + 2*H, 
                    Ys[i] - Hs[j] >= Ys[j] - H),
                And(
                    Xs[i] + Ws[i] <= Xs[j] + 2*W, 
                    Xs[i] - Ws[j] >= Xs[j] - W, 
                    Ys[i] + Hs[i] <= Ys[j] + H, 
                    Ys[i] - Hs[j] >= Ys[j])
                ) for i in range(n) for j in range(n) if i!=j ]

def boundary_constraints_rotation(Xs, Ys, Ws, Hs, W, d, n):
    pass


def buildModel(instance, o):

    verbose=False
    timeout=None
    
    n = instance['n']
    w = instance['w']
    dim = instance['dim']

    #Largest block symmetry break
    largest_block = np.argmax([d[0]*d[1] for d in dim ])

    # Height: sum of all blocks heights
    H = sum([int(dim[i][1]) for i in range(n)])

    # Width: silicon plate width
    W = w

    # Block Position Vectors
    X = IntVector('x', n)
    Y = IntVector('y', n)


    # Block widths and heights
    widths = [d[0] for d in dim]
    heights = [d[1] for d in dim]

    # Height variable
    d = o
    
    #Solver Declaration
    s = Tactic('lra').solver()

    #Boundary
    # Max X Domain
    s.add([And(0 <= X[i], X[i] <= W-widths[i]) 
            if i!=largest_block else And(0 <= X[i], X[i] <= int(W-widths[i])/2) 
            for i in range(n)])
    # Max Y Domain
    s.add([And(0 <= Y[i], Y[i] <= d-heights[i]) 
            if i!=largest_block else And(0 <= Y[i], Y[i] <= int(d-heights[i])/2) 
            for i in range(n)])


    no = no_overlap(X, Y, widths, heights, W, H, n)

    s.add(no)

    return s
    
def bisection(instance):

    init = time()

    LB = int(math.ceil(sum([p[0]*p[1] for p in instance['dim']])/instance['w']))

    #UB = int(2*max(max([[p[0],p[1]] for p in instance['dim']], key=lambda p:p[0]*p[1])[1],LB))+1
    naiive = utils.computeMostStupidSolution(instance)
    #print(heuristic)
    #UB = int(3*(LB/2))
    UB = naiive[0][1]+1
    #print(naiive)

    m=None

    print('lb', LB)

    print('ub', UB)

    o = int((LB+UB)/2)

    while LB<UB and (time()-init)<301:
        
        s = buildModel(instance, o)
        set_option(timeout=int(300-(time()-init))*1000)
        if(s.check() == sat):
            #m = s.model()
            UB = o
            m = s.model()
            

            print("sat, UB:", UB)
        else:
            LB = o +1
            print("unsat, LB:", LB)
        
        o = int((LB+UB)/2)
        #print("O:",o)


    #print(time()-init)
    #m = None
    #if s.check()==sat:
    # if time()-init<301:
    #     m = format_solution(m, o, instance['dim'], instance['n'], instance['w'])
    # else:
    #     m = naiive

    return o, m, time()-init

if __name__=="__main__":
    # set_option("parallel.enable","true")
    # set_option("parallel.threads.max","4")
    filename=currentdir+"/report.csv"
    with open(filename, 'w') as outfile:
        outfile.write("Instance;Time;Solution\n")
    for i in range(1,41):
        print("SOLVING: ", i)
        instance = utils.loadInstance(currentdir+f"/../instances/ins-{i}.txt")

        print(instance)
        o, m, t = bisection(instance)

        m = format_solution(m, o, instance['dim'], instance['n'], instance['w'])
        print(m)

        if(t<300):
            with open(filename, 'a') as outfile:
                outfile.write("{};{};{}\n".format(i,t,m))
        else:
            with open(filename, 'a') as outfile:
                outfile.write("{};{};{}\n".format(i,t,m))
        print("Finished in:", t)    

