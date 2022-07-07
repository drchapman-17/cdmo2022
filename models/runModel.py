from ctypes import util
import getopt,sys
import datetime
from minizinc import Instance,Model,Solver
import MIP.vlsi_MINLP as LP
import utils
import json
import SMT.vlsi_SMT as SMT

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:rvi:t:", ["help", "output=","export=","timeout=","show-result"])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)
    output = None # file to which export the solution
    export= None # file to which export the model
    verbose = False
    show=False
    rotationsAllowed=False
    timeout=None 
    instn=[]

    for o, a in opts:
        if o == "-v":
            verbose = True
        elif o == "-r":
            rotationsAllowed = True 
        elif o == "--show-result":
            show = True        
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-o", "--output"):
            output = a
        elif o in ("-t","--timeout"):
            try: timeout=int(a)
            except Exception as e: 
                print(e)
                sys.exit(2) 
        elif o in ("--export"):
            export = a
        elif o in ("-i"):
            try: 
                instn=[int(a)]
                if instn[0]<1 or instn[0] > 40: raise Exception
            except Exception as e:
                print("Error: instn must be an integer between 1 and 40")
                usage()
                sys.exit(2)
        else:
            assert False, "unhandled option \"{}\"".format(o)
    
    # check if model name is valid
    if(len(args)<1):
        print("Error: you must specify a model")
        usage()
        sys.exit(2)

    args=[model.upper() for model in args]
    for model in args:
        if model not in ["CP","SAT","SMT","ILP"]:
            print("Error: solving strategy \"{}\" not recognized. Allowed names are \"CP\",\"SAT\"\"SMT\"\"ILP\"".format(model))
            sys.exit(2)

    #load problem instances 
    if(len(instn)<1):
        print("Warning: no instance number is specified. The program will proceed loading and solving all the instances")
        instn=[i for i in range(1,41)]
    instances=[utils.loadInstance(f"instances/ins-{n}.txt") for n in instn]

    #build options
    options={
        "verbose":verbose,
        "timeout":timeout,
        "output":output,
        "show": show,
        "rotationsAllowed":rotationsAllowed,
        "export":export
    }

    # Print useful informations
    print("Solving instance(s): {}".format(*instn))
    
    print("Rotations: "+("allowed" if rotationsAllowed else "not allowed"))

    print("Timeout={}".format(timeout if timeout else "not set"))
    if verbose: print("Verbose output activated")
    
    # Run the solvers
    functions={
        "CP":runCPInstance,
        "SAT":runSATInstance,
        "SMT":runSMTInstance,
        "ILP":runILPInstance
    }
    for model in args:
        print(f"Solving strategy: {model}")
        run=functions[model]
        for instance in instances:
            run(instance,options)

def usage(): 
    print("Usage: python {} [-i instn] [-t timeout] [-v] [-o outfile] <strategy>".format(sys.argv[0]))

def runCPInstance(inst,options):
    verbose=False
    timeout=None
    if options["verbose"]:
        verbose=True
    if options["timeout"]:
        timeout=datetime.timedelta(seconds=options["timeout"])
    
    show=options["show"]
    output=options["output"]          
    rotationsAllowed=options["rotationsAllowed"]

    print(inst)


    # VERSIONE DI DAVIDE
    vlsi = Model("./CP/vlsi_diffn.mzn")
    chuffed=Solver.lookup("chuffed")
    instance=Instance(chuffed,vlsi)
    instance["n"]=inst["n"]
    instance["w"]=inst["w"]
    instance["dim"]=inst["dim"]
    
    # # VERSIONE DI TOTI
    # if rotationsAllowed:
    #     vlsi = Model("./CP/vlsi_diffn_flip_clean.mzn")
    # else: 
    #     vlsi = Model("./CP/vlsi_diffn_clean.mzn")
    # chuffed=Solver.lookup("chuffed")
    # instance=Instance(chuffed,vlsi)
    # instance["n"]=inst["n"]
    # instance["w"]=inst["w"]
    # instance["w_c"]=[i[0] for i in inst["dim"]]
    # instance["h_c"]=[i[1] for i in inst["dim"]]

    # SOLVE THE INSTANCE
    result=instance.solve(timeout=timeout,free_search=True)
    print(result)
    if(verbose):
        print("\n____STATISTICS____")
        for key,val in result.statistics.items():
            print(key,"=",val) 
        print("\n__________________")
    if show:
        utils.display_solution(json.loads(str(result)))
    if output:
        utils.write_out(output,str(result))

def runSATInstance(instance,options):
    pass

def runSMTInstance(instance,options):
    SMT.solveInstance(instance,options)

def runILPInstance(instance,options):
    LP.solveInstance(instance,options)

if __name__=="__main__":
    main()