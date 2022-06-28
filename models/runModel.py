import getopt,sys
import datetime
from minizinc import Instance,Model,Solver

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:vi:", ["help", "output="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)
        usage()
        sys.exit(2)
    output = None #by default the result is showed in stdout
    verbose = False
    timeout=3000 #default timeout 5 minutes
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
    
    if(len(args)<1):
        print("Error: you must specify a model")
        usage()
        sys.exit(2)
                
    #load problem instances 
    if(len(instn)<1):
        print("Warning: no instance number is specified. The program will proceed loading and solving all the instances")
        instn=[i for i in range(1,41)]
    instances=loadInstances(instn)

    options={
        "verbose":verbose,
        "timeout":timeout,
        "output":output
    }


    for model in args:
        if model.upper() not in ["CP","SAT","SMT","ILP"]:
            print(f"Error: solving strategy \"{model}\" not recognized")
            sys.exit(2)
    print(f"Solving instance(s): {instn}")
    functions={
        "CP":runCPInstance,
        "SAT":runSATInstance,
        "SMT":runSMTInstance,
        "ILP":runILPInstance
    }
    for model in args:
        model=model.upper()
        print(f"Solving strategy: {model}")
        run=functions[model]
        for instance in instances:
            run(instance,options)

def usage(): 
    print("Usage: python {} [-i instn] [-t timeout] <strategy>".format(sys.argv[0]))

def loadInstances(numbers):
    instances=[]
    for nn in numbers:
        with open(f"instances/ins-{nn}.txt") as f:
            lines=f.readlines()
            w=int(lines[0])
            n=int(lines[1])
            elements=[]
            for i in range(n):
                x,y=lines[2+i].split()
                x=int(x)
                y=int(y)
                elements.append([x,y])
            instances.append({"n":n,"w":w,"dim":elements})
    return instances

def runCPInstance(inst,options):
    print("CP")
    if(options["verbose"]):
        verbose=True
    else: verbose=False
    timeout=datetime.timedelta(seconds=options["timeout"])


    vlsi = Model("./CP/vlsi_diffn.mzn")
    chuffed=Solver.lookup("chuffed")
    instance=Instance(chuffed,vlsi)
    instance["n"]=inst["n"]
    instance["w"]=inst["w"]
    instance["dim"]=inst["dim"]
    result=instance.solve(timeout=timeout,free_search=True)
    print(result)
    if(verbose):
        print("____SOLVING_STATISTICS____")
        for key,val in result.statistics.items():
            print(key,"=",val) 


def runSATInstance(instance,options):
    pass
def runSMTInstance(instance,options):
    pass
def runILPInstance(instance,options):
    pass

if __name__=="__main__":
    main()