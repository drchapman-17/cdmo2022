import os,sys 
import inspect
import getopt
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
sys.path.insert(0, currentdir) 
from vlsi_MIP_problem import VLSI_Problem
import utils

def solveInstance(instance,options):
    verbose=False
    show=False
    timeout=None
    rotationsAllowed=False

    if options["verbose"]:
        verbose=True
    if options["timeout"]:
        timeout=options["timeout"] 
    if options["show"]:
        show=True  
    rotationsAllowed=options["rotationsAllowed"]
    output=options["output"]

    print("Instance:")
    for key,val in instance.items():
        print(f"{key} = {val}")
    problem=VLSI_Problem(instance,rotationsAllowed)
    print("Solving..",end="")
    problem.solve(timeLimit=timeout,verbose=verbose)  
    print("Solved!\nStatus:", problem.getStatusMessage())
    print("Elapsed time:",problem.getElapsedTime())
    solution=problem.getSolution()
    if(solution):
        print("Solution:",solution)
        if(show):
            utils.displaySolution(solution)
        if(output):
            utils.writeSolution(output,solution)

def usage():
    print("Usage: python {} [-v] [-t timeout] [-i infile] [-o outfile] [--show] [-r] [instn]".format(sys.argv[0].split("\\")[-1].split("/")[-1]))

def main():

    output = None #by default the result is showed in stdout
    input = None
    show=False
    verbose = False
    timeout=None #default timeout 5 minutes
    rotationsAllowed=False
    instn=[]
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:vi:t:r", ["help","input=" "output=","timeout=","show-result"])
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
        elif o in ("-o", "--output"): #Out file
            output = a
        elif o in ("-i","--input"): #Input file
            input=a
        elif o in ("--show-result"): #Plot result
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
        "rotationsAllowed":rotationsAllowed
    }

    solveInstance(instance,options)

if __name__=="__main__":
    main()