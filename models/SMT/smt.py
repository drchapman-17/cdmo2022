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

def no_overlap(Xs, Ys, Ws, Hs, n):
    n_o = [Or(  Xs[i] + Ws[i] <= Xs[j], 
                Xs[i] - Ws[j] >= Xs[j], 
                Ys[i] + Hs[i] <= Ys[j],
                Ys[i] - Hs[j] <= Ys[j] ) for i in range(n) for j in range(n)]
    return n_o


def main():
    #load instance (Dictionary: n, m , dim)
    instance = loadInstance(1)

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
    s = Solver()

    #Height is >= 0
    s.add(d>0)

    # Boundary constraints for each block
    bc = boundary_constraints(X, Y, widths, heights, d, W, n)
    s.add(bc)

    # No overlapping constraints
    no = no_overlap(X, Y, widths, heights, n)
    s.add(no)

    #print(s.check())
    #print(s.model())
    with open("prova.smt2", 'w') as outfile:
        
        for line in s.sexpr():
            outfile.write(line)
        outfile.write("(check-sat)")
            


if __name__=="__main__":
    main()