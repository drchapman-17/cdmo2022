import getopt,sys
import datetime
from minizinc import Instance,Model,Solver
from optional import Optional
import utils

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:vi:t:", ["help", "output=","timeout"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)
        usage()
        sys.exit(2)
    output = None #by default the result is showed in stdout
    verbose = False
    timeout=None #default timeout 5 minutes
    instn=[]
    for o, a in opts:
        if o == "-v":
            verbose = True
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
        elif o in ("-i"):
            try: 
                instn=[int(a)]
                if instn[0]<1 or instn[0] > 40: raise Exception
            except Exception as e:
                print("Error: instn must be an integer between 1 and 40")
                usage()
                sys.exit(2)
        else:
            assert False, "unhandled option"
    
    # check if model name is valid
    if(len(args)<1):
        print("Error: you must specify a model")
        usage()
        sys.exit(2)

    args=[model.upper() for model in args]
    for model in args:
        if model not in ["CP","SAT","SMT","ILP"]:
            print(f"Error: solving strategy \"{model}\" not recognized")
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
        "output":output
    }

    # Print useful informations
    if verbose: print("Verbose output activated")
    print("Timeout={}".format(timeout if timeout else "Not set"))
    print("Solving instance(s): {}".format(*instn))
    
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
    print("Usage: python {} [-i instn] [-t timeout] <strategy>".format(sys.argv[0]))

def runCPInstance(inst,options):
    if(options["verbose"]):
        verbose=True
    else: verbose=False
    if options["timeout"]:
        timeout=datetime.timedelta(seconds=options["timeout"])
    else: 
        timeout=None
    
    """
    # VERSIONE DI DAVIDE
    vlsi = Model("./CP/vlsi_diffn.mzn")
    chuffed=Solver.lookup("chuffed")
    instance=Instance(chuffed,vlsi)
    instance["n"]=inst["n"]
    instance["w"]=inst["w"]
    instance["dim"]=inst["dim"]
    """
    # VERSIONE DI TOTI
    vlsi = Model("./CP/vlsi_diffn_clean.mzn")
    chuffed=Solver.lookup("chuffed")
    instance=Instance(chuffed,vlsi)
    instance["n"]=inst["n"]
    instance["w"]=inst["w"]
    instance["w_c"]=[i[0] for i in inst["dim"]]
    instance["h_c"]=[i[1] for i in inst["dim"]]
    result=instance.solve(timeout=timeout,free_search=True)
    print(result)
    if(verbose):
        print("\n____STATISTICS____")
        for key,val in result.statistics.items():
            print(key,"=",val) 
        print("\n__________________")


def runSATInstance(instance,options):
    pass
def runSMTInstance(instance,options):
    pass
def runILPInstance(instance,options):
    pass

if __name__=="__main__":
    main()