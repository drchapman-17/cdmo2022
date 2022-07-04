from z3 import *
from cumulative import cumulative
from time import time

# ROBA RUBATA
def z3_cumulative(start, duration, resources, total):

    decomposition = []
    for u in resources:
        decomposition.append(
            sum([If(And(start[i] <= u, u < start[i] + duration[i]), resources[i], 0)
                 for i in range(len(start))]) <= total
        )
    return decomposition

def format_solution(opt, dim, n, W, h):
    m = opt.model()
    nicer = sorted ([(d, m[d]) for d in m], key = lambda x: str(x[0]))
    dict = {str(l[0]):l[1] for l in nicer if str(l[0]).startswith("x__") or str(l[0]).startswith("y__")}

    print(dict)

    print(n)
    blockpos = []
    for i in range(n):
        blockpos.append([int(str(dict['x__{}'.format(i)]))+1,int(str(dict['y__{}'.format(i)]))+1])

    #print(blockpos)
    schema = [[W,opt.lower(h)]]

    for i in range(n):
        schema.append([*dim[i], *blockpos[i]])

    return schema

def distinct_coordinates(Xs, Ys, W, n):
    
    diff = [ W*Xs[i]+Ys[i]  for i in range(n)]

    return Distinct(diff)

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
    no_1 = [ Xs[i] + Ws[i] <= Xs[j] + W*(Xij[i*n+j] + Yij[i*n+j]) for i in range(n) for j in range(n) if i<j ]
    no_2 = [ Xs[i] - Ws[j] >= Xs[j] - W*(1 - Xij[i*n+j] + Yij[i*n+j]) for i in range(n) for j in range(n) if i<j ]
    no_3 = [ Ys[i] + Hs[i] <= Ys[j] + H*(1 + Xij[i*n+j] - Yij[i*n+j]) for i in range(n) for j in range(n) if i<j ]
    no_4 = [ Ys[i] - Hs[j] >= Ys[j] - H*(2 - Xij[i*n+j] - Yij[i*n+j]) for i in range(n) for j in range(n) if i<j ]
    return [*no_1,*no_2,*no_3,*no_4]

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

# def no_overlap3(Xs, Ys, Ws, Hs, W, H, n):
#     no=[]
#     for i in range(n):
#         for j in range(n):
#             A = And(
#                             Xs[i] + Ws[i] <= Xs[j], 
#                             Xs[i] - Ws[j] >= Xs[j] - W, 
#                             Ys[i] + Hs[i] <= Ys[j] + H, 
#                             Ys[i] - Hs[j] >= Ys[j] - 2*H)

#             B = And(
#                             Xs[i] + Ws[i] <= Xs[j] + W, 
#                             Xs[i] - Ws[j] >= Xs[j] - 2*W, 
#                             Ys[i] + Hs[i] <= Ys[j], 
#                             Ys[i] - Hs[j] >= Ys[j] - H)

#             C = And(
#                             Xs[i] + Ws[i] <= Xs[j] + W, 
#                             Xs[i] - Ws[j] >= Xs[j], 
#                             Ys[i] + Hs[i] <= Ys[j] + 2*H, 
#                             Ys[i] - Hs[j] >= Ys[j] - H)
#             D = And(
#                             Xs[i] + Ws[i] <= Xs[j] + 2*W, 
#                             Xs[i] - Ws[j] >= Xs[j] - W, 
#                             Ys[i] + Hs[i] <= Ys[j] + H, 
#                             Ys[i] - Hs[j] >= Ys[j])
#             no.append(And(Or(A,B,C,D), Not(And(A,B)),Not(And(A,C)), Not(And(A,D)), Not(And(B,C)), Not(And(B,D), Not(And(C,D)))))            

#     return no

    
#     return [*no_1,*no_2,*no_3,*no_4]

def boundary_constraints_rotation(Xs, Ys, Ws, Hs, W, d, n):
    pass


def buildModel(instance, o):

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
    d = o

    #Solver Declaration
    #s = Solver()
    #opt = Optimize()

    s =  SolverFor("QF_LIA")
    #Height is >= 0
    #s.add(d>0)

    # Max X Domain
    s.add([And(0 <= X[i], X[i] <= W-widths[i]) for i in range(n)])
    # Max Y Domain
    s.add([And(0 <= Y[i], Y[i] <= d-heights[i]) for i in range(n)])

    #opt.add([Y[i] <= d-heights[i] for i in range(n)])

    # Cumulative

    # cumulative(s, X, widths, heights, d, 0, W)
    # cumulative(s, Y, heights, widths, W, 0, H)

    # cumulative_y = z3_cumulative(Y, heights, widths, W)
    # s.add(cumulative_y)
    # cumulative_x = z3_cumulative(X, widths, heights, H)
    # s.add(cumulative_x)
    # #Distinct coordinates
    #s.add(distinct_coordinates(X, Y, W, n))
    #s.add(d>0)



    rotationsAllowed=False
    ## IF NO ROTATION
    # Boundary constraints for each block
    if rotationsAllowed:
        pass
    else:
        #bc = boundary_constraints(X, Y, widths, heights, W, d, n)
        #s.add(bc)
        #s.add(bc)
        #Xij = [Int('x{}_{}'.format(i,j)) for i in range(n) for j in range(n)]
        #Yij = [Int('y{}_{}'.format(i,j)) for i in range(n) for j in range(n)]

        # # Xij = IntVector('x', n, n)
        # # Yij = IntVector('y', n, n)
        # print(Xij)
        # #Boolean Restriction
        # x_bool0 = [x>=0 for x in Xij]
        # y_bool0 = [y>=0 for y in Yij]
        # x_bool1 = [x<=1 for x in Xij]
        # y_bool1 = [y<=1 for y in Yij]
        # opt.add([*x_bool0,*y_bool0,*x_bool1,*y_bool1])
        # No overlapping constraints
        #no = no_overlap(X, Y, Xij, Yij, widths, heights, W, H, n)
        no = no_overlap2(X, Y, widths, heights, W, H, n)
        #s.add(no)
        s.add(no)

    # IF ROTATION

    # VERBOSE
    if verbose:
        #print(s.check())
        #print(s.model())
        pass
    
    # print("sto scrivendo")
    # with open("temp/model.smt2", 'w') as outfile:
    #     outfile.write("(set-logic LIA)\n")
    #     for line in opt.sexpr():
    #         outfile.write(line)
    #     outfile.write("(minimize d)\n")
    #     outfile.write("(get-objectives)\n(exit)")
    # print("ho finito")
    # init = time()
    # h = opt.minimize(d)
    # print(opt.check())
    
    # print("Finished in:", time()-init)
    # print(opt.lower(h))

    #print(opt.model())
    


    #print(format_solution(opt, dim, n, W, h))
    #print(opt.statistics())
    ## SCRIPT DI AMADINI CON OPZIONI

    return s
    
def bisection(instance):

    init = time()

    LB = int(sum([p[0]*p[1] for p in instance['dim']])/instance['w'])

    UB = int(2*max(max([[p[0],p[1]] for p in instance['dim']], key=lambda p:p[0]*p[1])[1],LB))+1

    
    print('lb', LB)

    print('ub', UB)

    o = int((LB+UB)/2)

    while LB<UB and time()-init<301:
        
        s = buildModel(instance, o)
        s.set("timeout", 300)
        if(s.check() == sat):
            
            UB = o
            #print("sat, UB:", UB)
        else:
            LB = o +1
            #print("unsat, LB:", LB)
        
        o = int((LB+UB)/2)
        #print("O:",o)

    print(time()-init)
    print(s.check())
    #s.check()
    m = s.model()
    return o, m, time()-init

if __name__=="__main__":
    # with open("report", 'w') as outfile:
    #     outfile.write("REPORT:\n\n")
    i=15
    o, m, t = bisection(loadInstance(i))
    if(t<300):
        with open("report", 'a') as outfile:
            outfile.write("Instance:{}  Height:{}  Time:{}\n".format(i,o,t))
    else:
        with open("report", 'w') as outfile:
            outfile.write("Instance:{}  Height:NO  Time:{}\n".format(i,t))
    #print("Finished in:", t)    

