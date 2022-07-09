from z3 import *
from time import time
import numpy as np
import os,sys 
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
sys.path.insert(0, currentdir) 
import utils

def format_solution(m, o, dim, n, W,rotationsAllowed):
    if m != None:
        sol = []
        variables={str(d):m.evaluate(m[d]) for d in m}
        sol=[[W,o]]
        for i in range(n):
            x=variables[f"x__{i}"].as_long()
            y=variables[f"y__{i}"].as_long()
            if rotationsAllowed and variables[f"f__{i}"]:
                w=dim[i][1]
                h=dim[i][0]
            else:
                w=dim[i][0]
                h=dim[i][1]
            sol.append([w,h,x+1,y+1])                
        return sol

    else: return None

def boundary(i, Xs, Ys, Ws, Hs, W, d, fi):
    dim1i,dim2i=(Ws,Hs) if not fi else (Hs,Ws)
    return And(Xs[i]+dim1i[i]<=W, Ys[i]+dim2i[i]<=d, Xs[i]>=0, Ys[i]>=0)

def no_overlap(i, j, Xs, Ys, Ws, Hs, W, H, fi, fj):
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

def buildModel(instance, o):
    n = instance['n']
    W = instance['w']
    dim = instance['dim']

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

    #Largest block symmetry break
    largest_idx = np.argmax([d[0]*d[1] for d in dim ])
    xmax_largest=(W-widths[largest_idx])/2
    ymax_largest=(d-heights[largest_idx])/2

    # Constraints
    s.add([boundary(i,X,Y,widths,heights,W,d,False) for i in range(n) if i!=largest_idx])
    s.add(And(
        X[largest_idx]>=0,
        Y[largest_idx]>=0,
        X[largest_idx]<=xmax_largest,
        Y[largest_idx]<=ymax_largest
        ))
    s.add([no_overlap(i, j, X, Y, widths, heights, W, d, False,False) for i in range(n) for j in range(n) if i!=j ])
    
    return s

def buildModelRotations(instance, o):
    
    n = instance['n']
    w = instance['w']
    dim = instance['dim']

    #Largest block symmetry break
    largest_idx = np.argmax([d[0]*d[1] for d in dim ])

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
    
    #Largest block symmetry break
    largest_idx = np.argmax([d[0]*d[1] for d in dim ])
    xmax_largest=(W-widths[largest_idx])/2
    ymax_largest=(d-heights[largest_idx])/2
    s.add(Or(
        And(Not(f[largest_idx]),X[largest_idx]<=xmax_largest,Y[largest_idx]<=ymax_largest),
        And(f[largest_idx],X[largest_idx]<=xmax_largest,Y[largest_idx]<=ymax_largest)))

    for i in range(n):
        for j in range(n):
            if i!=j:
                s.add(Or(
                    And(Not(f[i]),Not(f[j]),no_overlap(i,j, X, Y, widths, heights, W, d, False,False)),
                    And(f[i],Not(f[j]),no_overlap(i,j,X, Y, widths, heights, W, d,True,False)),
                    And(Not(f[i]),f[j],no_overlap(i,j,X, Y, widths, heights, W, d,False,True)),
                    And(f[i],f[j],no_overlap(i,j,X, Y, widths, heights, W, d,True,True))
                ))
        s.add(Or(
                And(Not(f[i]), 
                    boundary(i, X, Y, widths, heights, W, d, False)),
                And(f[i], 
                    boundary(i, X, Y, widths, heights, W, d, True))))
    return s


def bisection(instance,rotationsAllowed=False,timeout=None,verbose=False):

    naiive = utils.computeMostStupidSolution(instance)
    if not naiive:
        return None,None,None

    LB = int(sum([p[0]*p[1] for p in instance['dim']])/instance['w'])
    UB = naiive[0][1]+1

    m=None
    o = int((LB+UB)/2)
    best_o=o=UB

    build=buildModelRotations if rotationsAllowed else buildModel 

    init = time()
    
    if verbose:
        print("BISECTION STARTING VALUES:")
        print('lb', LB)
        print('ub', UB)
        print("o", o)
        print("-----------------------")
    
    while LB<UB:
        s = build(instance, o)
        if timeout and (time()-init>timeout+1):
            break
        if timeout: set_option(timeout=int(timeout+init-time())*1000)
        if(s.check() == sat):
            UB = o
            best_o=o
            m = s.model()        
            if verbose:
                print("sat, UB:", UB)
        elif(s.check()==unknown):
            if verbose:
                print("time-out")
        else:
            LB = o +1
            if verbose:
                print("unsat, LB:", LB)
        o = int((LB+UB)/2)
        if verbose:
            print("o:", o)
            print("-----------------------")

    return best_o, m, time()-init


def solveInstance(instance, options):
    # Solve the instance
    verbose=options['verbose']
    output=options['output']
    show=options['show']
    timeout=options['timeout']
    rotationsAllowed=options["rotationsAllowed"]

    o, m, t = bisection(instance,rotationsAllowed,timeout,verbose)
    if timeout and t>timeout:  print("Time limit reached")
    if m:
        sol=format_solution(m, o, instance['dim'], instance['n'], instance['w'],rotationsAllowed)
        print("Instance solved")
        print("Minimum Height Found: ", o)
        print("Instance Model:", sol)
        print("Solved in: {}s".format(t))
        print("-----------------------")
        # Write out the solutions
        if output:
            utils.writeSolution(output,sol)
        # Plot the solution
        if show:
            utils.display_solution(sol)
    else: print("No solution found!")

def main():
    # Report
    rotationsAllowed=False
    filename=currentdir+"/report.csv"

    with open(filename, 'w') as outfile:
        outfile.write("Instance;Time;Solution\n")
    for i in range(1,41):
        print("SOLVING: ", i)
        instance = utils.loadInstance(currentdir+f"/../instances/ins-{i}.txt")

        print(instance)
        o, m, t = bisection(instance,rotationsAllowed,300)

        m = format_solution(m, o, instance['dim'], instance['n'], instance['w'],rotationsAllowed)
        print(m)

        if(t<300):
            with open(filename, 'a') as outfile:
                outfile.write("{};{};{}\n".format(i,t,m))
        else:
            with open(filename, 'a') as outfile:
                outfile.write("{};{};{}\n".format(i,None,m))
        print("Finished in:", t)

if __name__=="__main__":
    main()
