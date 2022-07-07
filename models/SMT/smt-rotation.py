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

def format_solution(m, o, dim, n, W):

    print(m)
    schema = []

    if m != None:
        nicer = sorted ([(d, m[d]) for d in m], key = lambda x: str(x[0]))
        dict = {str(l[0]):l[1] for l in nicer if str(l[0]).startswith("x__") or str(l[0]).startswith("y__") or str(l[0]).startswith("f__")}

        blockpos = []
        for i in range(n):
            blockpos.append([int(str(dict['x__{}'.format(i)]))+1,int(str(dict['y__{}'.format(i)]))+1])
            
        schema = [[W,o]]

        for i in range(n):
            if bool(dict['f__{}'.format(i)]):
                #swap
                dim[i][1], dim[i][0] = dim[i][0],dim[i][1]

            schema.append([*dim[i], *blockpos[i]])

    return schema

def boundary_constraints(Xs, Ys, Ws, Hs, W, d, n):

    x_width = [ Xs[i] + Ws[i] <= W for i in range(n)]
    y_height = [ Ys[i] + Hs[i] <= d for i in range(n)]
    x_morethan_0 = [ Xs[i] >= 0 for i in range(n)]
    y_morethan_0 = [ Ys[i] >= 0 for i in range(n)]

    return [*x_width, *y_height, *x_morethan_0, *y_morethan_0]


def no_overlap2(Xs, Ys, Ws, Hs, W, H, n):
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


def no_overlap(i, j, Xs, Ys, Ws, Hs, W, H, d, fi, fj):
    dim1i,dim2i=(Ws,Hs) if not fi else (Hs,Ws)
    dim1j,dim2j=(Ws,Hs) if not fj else (Hs,Ws)

    

    no =    Or(
                And(
                    Xs[i] + dim1i[i] <= Xs[j], 
                    Xs[i] - dim1j[j] >= Xs[j] - W, 
                    Ys[i] + dim2i[i] <= Ys[j] + H, 
                    Ys[i] - dim2j[j] >= Ys[j] - 2*H),
                And(
                    Xs[i] + dim1i[i] <= Xs[j] + W, 
                    Xs[i] - dim1j[j] >= Xs[j] - 2*W, 
                    Ys[i] + dim2i[i] <= Ys[j], 
                    Ys[i] - dim2j[j] >= Ys[j] - H),
                And(
                    Xs[i] + dim1i[i] <= Xs[j] + W, 
                    Xs[i] - dim1j[j] >= Xs[j], 
                    Ys[i] + dim2i[i] <= Ys[j] + 2*H, 
                    Ys[i] - dim2j[j] >= Ys[j] - H),
                And(
                    Xs[i] + dim1i[i] <= Xs[j] + 2*W, 
                    Xs[i] - dim1j[j] >= Xs[j] - W, 
                    Ys[i] + dim2i[i] <= Ys[j] + H, 
                    Ys[i] - dim2j[j] >= Ys[j])
                )

    

    return no

def boundary(i, Xs, Ys, Ws, Hs, W, d, fi):
    dim1i,dim2i=(Ws,Hs) if not fi else (Hs,Ws)
    return And(Xs[i]+dim1i[i]<=W, Ys[i]+dim2i[i]<=d, Xs[i]>=0, Ys[i]>=0)

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
    #X = [ BitVec('x__{}'.format(i), int(log2(H))) for i in range(n)]
    #Y = [ BitVec('y__{}'.format(i), int(log2(H))) for i in range(n)]

    # Block widths and heights
    widths = [d[0] for d in dim]
    heights = [d[1] for d in dim]

    # Height variable
    d = o
    
    #Solver Declaration
    f = BoolVector('f',n)
    #s =  SolverFor('ALL')
    s = Tactic('lra').solver()
    #s = SimpleSolver()
    #s.set("smt.ematching", False)
    #Height is >= 0
    #s.add(d>0)


    for i in range(n):
        for j in range(n):
            if i!=j:
                s.add(Or(
                    And(Not(f[i]),Not(f[j]),no_overlap(i,j, X, Y, widths, heights, W, H, d, False,False)),
                    And(f[i],Not(f[j]),no_overlap(i,j,X, Y, widths, heights, W, H, d,True,False)),
                    And(Not(f[i]),f[j],no_overlap(i,j,X, Y, widths, heights, W, H, d,False,True)),
                    And(f[i],f[j],no_overlap(i,j,X, Y, widths, heights, W, H, d,True,True))
                ))
        s.add(Or(
                And(Not(f[i]), 
                    boundary(i, X, Y, widths, heights, W, d, False)),
                And(f[i], 
                    boundary(i, X, Y, widths, heights, W, d, True))))

    #Boundary
    # Max X Domain
    #s.add([And(0 <= X[i], X[i] <= W-widths[i]) 
    #        if i!=largest_block else And(0 <= X[i], X[i] <= int(W-widths[i])/2) 
    #        for i in range(n)])
    # Max Y Domain
    # s.add([And(0 <= Y[i], Y[i] <= d-heights[i]) 
            # if i!=largest_block else And(0 <= Y[i], Y[i] <= int(d-heights[i])/2) 
            # for i in range(n)])
    
    rotationsAllowed=False
    ## IF NO ROTATION
    # Boundary constraints for each block
    # IF ROTATION



    return s
    
def bisection(instance):

    init = time()

    #Lower Bound
    LB = int(sum([p[0]*p[1] for p in instance['dim']])/instance['w'])

    # Naiive Solution Heuristic to compute an Wpper Bound
    naiive = utils.computeMostStupidSolution(instance)
    UB = naiive[0][1]+1

    print(naiive)

    #Model
    m=None

    print('lb', LB)

    print('ub', UB)

    #Objective Computation
    o = int((LB+UB)/2)

    #Bisection
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

    return o, m, time()-init

if __name__=="__main__":
    
    
    #Report
    filename=currentdir+"/report_rotation.csv"
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
                outfile.write("{};{};{}\n".format(i,t,[]))
        print("Finished in:", t)    

