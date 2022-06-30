from ctypes import util
import os,sys,inspect,getopt
from pathlib import Path
from z3 import *
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
sys.path.insert(0, currentdir) 
import utils
import json

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

def no_overlap_rotation(Xs, Ys, Ws, Hs, W, d, n): #NON SERVE? BOH
    pass


def solveInstance(instance, options):

    verbose=False
    timeout=None

    if options["verbose"]:
         verbose=True
    if options["timeout"]:
        timeout=options["timeout"] # passare a script di amadini
    show=options["show"]
    output=options["output"]          
    export=options["export"]
    rotationsAllowed=options["rotationsAllowed"]

    n = instance['n']
    W = instance['w']
    dim = instance['dim']
    widths = [d[0] for d in dim]
    heights = [d[1] for d in dim]
    Hmax = sum(heights)

    # DECISION VARIABLES
    X = IntVector('x', n) # X positions vector
    Y = IntVector('y', n) # Y positions vector

    d = Int('d')    # height of the chip
    

    # BUILD SOLVER 
    model = Solver() if False else Optimize() #FIXME POI SI CAMBIA SE VOGLIAMO PROVARE ALTRI SOLVER BOH 

    # CONSTRAINTS   
    model.add(d>0)          # Height >= 0

    # Boundary constraints
    if rotationsAllowed:
        bcf=boundary_constraints_rotation
        nof=no_overlap_rotation
    else:
        bcf=boundary_constraints
        nof=no_overlap

    bc = bcf(X, Y, widths, heights, d, W, n)
    model.add(bc)
    Xij = [Int('x{}_{}'.format(i,j)) for i in range(n) for j in range(n)]
    Yij = [Int('y{}_{}'.format(i,j)) for i in range(n) for j in range(n)]

    x_bool0 = [x>=0 for x in Xij]
    y_bool0 = [y>=0 for y in Yij]
    x_bool1 = [x<=1 for x in Xij]
    y_bool1 = [y<=1 for y in Yij]
    model.add([*x_bool0,*y_bool0,*x_bool1,*y_bool1])
    
    # No overlapping constraints
    no = nof(X, Y, Xij, Yij, widths, heights, W, Hmax, n)
    model.add(no)

    # VERBOSE
    if verbose:
        print(model.check())
        print(model.model())
        pass

    # SOLVE THE INSTSNCE
    h = model.minimize(d)
    print(model.check())
    print(model.lower(h))
   
   # EXTRACT THE SOLUTION FROM THE MODEL
    m = model.model()
    m_dict={str(x[0]):x[1] for x in sorted ([(d, m[d]) for d in m], key = lambda x: str(x[0]))}
    sol=[[W,int(str(m_dict['d']))]]
    for i in range(n):
        sol.append([widths[i],heights[i],int(str(m_dict[f"x__{i}"]))+1,int(str(m_dict[f"y__{i}"]))+1])
    
    print("Solution: ",sol)

    if show:
        utils.show(sol)

    if output:
        utils.write_out(output,str(sol))
        print("Solution saved: ", (Path(currentdir) / output))

    if export:
        outdir=Path(currentdir+"/exported")
        outfile=outdir / (export+".smt2")
        if(not outdir.exists() or not outdir.is_dir()):
            outdir.mkdir()

        with outfile.open("w") as out:
            for line in model.sexpr():
                out.write(line)
            out.write("(check-sat)")
            out.close()
        print("SMT_LIB model exported: "+ str(outfile))

    # EVENTUALMENTE SCRIPT DI AMADINI CON OPZIONI

def usage():
    print("Usage: python {} [-v] [-h] [-r] [-t timeout] [-i infile] [-o outfile] [instn]".format(sys.argv[0].split("\\")[-1].split("/")[-1]))

def main():

    output = None #by default the result is showed in stdout
    input = None
    export=None
    show=False
    verbose = False
    timeout=None #default timeout 5 minutes
    rotationsAllowed=False
    instn=[]
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:vi:t:r", ["help","input=" "output=","export=","timeout=","show-result"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)
        usage()
        sys.exit(2)
    
    for o, a in opts:
        if o in ("-h", "--help"): #Help
            usage()
            sys.exit()
        elif o == "-v":           #Verbose
            verbose = True
        elif o == "-r":         #Rotations
            rotationsAllowed=True
        elif o in ("-t","--timeout"): #Timeout
            try: timeout=int(a)
            except Exception as e: 
                print(e)
                sys.exit(2) 
        elif o in ("-o", "--output"): # Out file
            output = a
        elif o in ("-i","--input"): # Input file
            input=a
        elif o in ("--export"): # Model export file
            export=a   
        elif o in ("--show-result"): # Plot result
            show=True
        else:           
            assert False, "unhandled option"
    
    if input:
        if len(args): 
            print("Do not specify an instance number if you have already specified an input file")
            usage()
            sys.exit(2)
    elif len(args)!=1:
        print("You need to specify an instance number or an input file")
        usage()
        sys.exit(2)
    else:     
        try:             
            instn=int(args[0])
            if instn<1 or instn> 40: raise Exception
            input=f"../instances/ins-{instn}.txt" 
        except Exception as e:
            print("Error: instn must be an integer between 1 and 40")
            usage()
            sys.exit(2)

    instance=utils.loadInstance(currentdir+"/"+input)
   
    print("VLSI floorplanning problem\n")
    print("Rotations: "+("allowed" if rotationsAllowed else "not allowed"))
    print("Timeout={}".format(timeout if timeout else "Not set"))

    options={
        "verbose":verbose,
        "output":output,
        "timeout":timeout,
        "show" : show,
        "rotationsAllowed":rotationsAllowed,
        "export":export   
    }

    solveInstance(instance,options)

if __name__=="__main__":
    main()
