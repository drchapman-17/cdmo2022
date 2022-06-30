from z3 import *


def loadInstance(number):

    with open(f"/home/stefano/cdmo2022/models/instances/ins-{number}.txt") as f:
        lines=f.readlines()
        w=int(lines[0])
        n=int(lines[1])
        elements=[]
        for i in range(n):
            x,y=lines[2+i].split()
            x=int(x)
            y=int(y)
            elements.append([x,y])

    return {"n":n,"w":w,"dim":elements}


def boundary_constraints(Xs, Ys, Ws, Hs, W, d, n):

    x_width = [ Xs[i] + Ws[i] <= W for i in range(n)]
    y_height = [ Ys[i] + Hs[i] <= d for i in range(n)]
    x_morethan_0 = [ Xs[i] >= 0 for i in range(n)]
    y_morethan_0 = [ Ys[i] >= 0 for i in range(n)]

    return [*x_width, *y_height, *x_morethan_0, *y_morethan_0]

def no_overlap(Xs, Ys, Xij, Yij, Ws, Hs, W, H, n):
    no_1 = [ Xs[i] + Ws[i] <= Xs[j] + W*(Xij[i*n+j] + Yij[i*n+j]) for i in range(n) for j in range(n) if i!=j ]
    no_2 = [ Xs[i] - Ws[j] >= Xs[j] - W*(1 - Xij[i*n+j] + Yij[i*n+j]) for i in range(n) for j in range(n) if i!=j ]
    no_3 = [ Ys[i] + Hs[i] <= Ys[j] + H*(1 + Xij[i*n+j] - Yij[i*n+j]) for i in range(n) for j in range(n) if i!=j ]
    no_4 = [ Ys[i] - Hs[j] >= Ys[j] - H*(2 - Xij[i*n+j] - Yij[i*n+j]) for i in range(n) for j in range(n) if i!=j ]
    return [*no_1,*no_2,*no_3,*no_4]

def boundary_constraints_rotation(Xs, Ys, Ws, Hs, W, d, n):
    pass


def solveInstance(instance, options):

    verbose=False
    timeout=None
    # if options["verbose"]:
    #     verbose=True
    # if options["timeout"]:
    #     timeout=options["timeout"] # passare a script di amadini
    # if options["show"]:
    #     show=True
    
    # output=options["output"]          
    # rotationsAllowed=options["rotationsAllowed"]

    #load instance (Dictionary: n, m , dim)
    #instance = loadInstance(instance_number)

    n = instance['n']
    w = instance['w']
    dim = instance['dim']

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
    d = Int('d')

    #Solver Declaration
    #s = Solver()
    opt = Optimize()
    #Height is >= 0
    #s.add(d>0)
    opt.add(d>0)
    rotationsAllowed=False
    ## IF NO ROTATION
    # Boundary constraints for each block
    if rotationsAllowed:
        pass
    else:
        bc = boundary_constraints(X, Y, widths, heights, d, W, n)
        #s.add(bc)
        opt.add(bc)
        Xij = [Int('x{}_{}'.format(i,j)) for i in range(n) for j in range(n)]
        Yij = [Int('y{}_{}'.format(i,j)) for i in range(n) for j in range(n)]

        # # Xij = IntVector('x', n, n)
        # # Yij = IntVector('y', n, n)
        # print(Xij)
        # #Boolean Restriction
        x_bool0 = [x>=0 for x in Xij]
        y_bool0 = [y>=0 for y in Yij]
        x_bool1 = [x<=1 for x in Xij]
        y_bool1 = [y<=1 for y in Yij]
        opt.add([*x_bool0,*y_bool0,*x_bool1,*y_bool1])
        # No overlapping constraints
        no = no_overlap(X, Y, Xij, Yij, widths, heights, W, H, n)
        #s.add(no)
        opt.add(no)

    # IF ROTATION

    # VERBOSE
    if verbose:
        #print(s.check())
        #print(s.model())
        pass

    h = opt.minimize(d)
    print(opt.check())
    print(opt.lower(h))
    print(opt.model())
    with open("temp/model.smt2", 'w') as outfile:
        
        for line in opt.sexpr():
            outfile.write(line)
        outfile.write("(check-sat)")

    ## SCRIPT DI AMADINI CON OPZIONI

    
            


if __name__=="__main__":
    solveInstance(loadInstance(10), {})

