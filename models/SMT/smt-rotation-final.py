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
    f = BoolVector('f',n)
    #s =  SolverFor('ALL')
    s = Tactic('lra').solver()

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

    return s
    
def bisection(instance, verbose=False):

    init = time()

    LB = int(sum([p[0]*p[1] for p in instance['dim']])/instance['w'])

    #UB = int(2*max(max([[p[0],p[1]] for p in instance['dim']], key=lambda p:p[0]*p[1])[1],LB))+1
    naiive = utils.computeMostStupidSolution(instance)
    #print(heuristic)
    #UB = int(3*(LB/2))
    UB = naiive[0][1]+1
    #print(naiive)

    m=None
    o = int((LB+UB)/2)


    if verbose:
        print("BISECTION STARTING VALUES:")
        print('lb', LB)
        print('ub', UB)
        print("o", o)
        print("-----------------------")
    
    while LB<UB and (time()-init)<301:
        
        s = buildModel(instance, o)
        set_option(timeout=int(300-(time()-init))*1000)
        if(s.check() == sat):
            #m = s.model()
            UB = o
            m = s.model()
            
            if verbose:
                print("sat, UB:", UB)
        else:
            LB = o +1
            if verbose:
                print("unsat, LB:", LB)
        
        o = int((LB+UB)/2)
        
        if verbose:
            print("o:", o)
            print("-----------------------")

    return o, m, time()-init


def solveInstance(instance, options):
    #Risolve l'istanza

    if options['verbose']:
        o, m, t = bisection(instance, options['verbose'])
        print("Solved Instance:")
        print("Minimum Height Found: ", o)
        print("Instance Model:", format_solution(m, o, instance['dim'], instance['n'], instance['w']))
        print("Solved in: {}s".format(t))
        print("-----------------------")
    else:
        o, m, t = bisection(instance)
        print("Instance Model:", format_solution(m, o, instance['dim'], instance['n'], instance['w']))
        print("-----------------------")
    #Stampa su file (zenyap)
    if options['output']:
        utils.writeSolution(options['output'],format_solution(m, o, instance['dim'], instance['n'], instance['w']))
    #Fa Show
    if options['show']:
        utils.display_solution(format_solution(m, o, instance['dim'], instance['n'], instance['w']))

        
def main():
    # report
    filename=currentdir+"/report_rotation.csv"
    with open(filename, 'w') as outfile:
        outfile.write("Instance;Time;Solution\n")
    for i in range(1,41):
        print("SOLVING: ", i)
        instance = utils.loadInstance(currentdir+f"/../instances/ins-{i}.txt")

        print(instance)
        o, m, t = bisection(instance)

        m = format_solution(m, o, instance['dim'], instance['n'], instance['w'])

        if(t<300):
            with open(filename, 'a') as outfile:
                outfile.write("{};{};{}\n".format(i,t,m))
        else:
            with open(filename, 'a') as outfile:
                outfile.write("{};{};{}\n".format(i,None,m))
        print("Finished in:", t)

if __name__=="__main__":

    main()

