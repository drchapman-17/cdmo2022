import os,sys 
import inspect
import getopt
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
sys.path.insert(0, currentdir) 
from vlsi_SAT_problem import vlsi_SAT_problem 
from vlsi_SAT_problem_rotations import vlsi_SAT_problem_rotations 
import utils

def solveInstance(instance,options):
    verbose=False
    show=False
    timeout= sys.maxsize
    rotationsAllowed=False

    if options["verbose"]:
        verbose = True
    if options["timeout"]:
        timeout = options["timeout"] 
    if options["show"]:
        show = True  
    rotationsAllowed = options["rotationsAllowed"]
    output = options["output"]

    if rotationsAllowed:
        problem = vlsi_SAT_problem_rotations(instance)
    else:
        problem = vlsi_SAT_problem(instance)
    
    sol, e_time = problem.solve(timeLimit=timeout,verbose=verbose)  
    
    if sol == None and e_time <= timeout:
        print(">Unfeasible.")
    elif e_time > timeout:
        
        if sol is not None:
            if(show):
                utils.display_solution(sol)

            if(output):
                utils.writeSolution(output,sol)

            print(f">Out of time, {round(e_time,3)} s, best height: {sol[0][1]}")
        else:
            print(f">Out of time, {round(e_time,3)} s")
    else:
        if(show):
            utils.display_solution(sol)
        if(output):
            utils.writeSolution(output,sol)
        
        print(f">Instance solved in {round(e_time,3)} s, height: {sol[0][1]}")

def usage():
    print("Usage: python {} [-v] [-t timeout] [-i infile] [-o outfile] [instn]".format(sys.argv[0].split("\\")[-1].split("/")[-1]))

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
    
    solveInstance(instance,instn,options)

if __name__=="__main__":
    main()