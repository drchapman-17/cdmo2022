import datetime
from minizinc import Instance,Model,Solver
import minizinc
import os,sys,inspect
import json
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
sys.path.insert(0, currentdir) 
import utils

def solveInstance(inst,options):
    verbose=False
    timeout=None
    if options["verbose"]:
        verbose=True
    if options["timeout"]:
        timeout=datetime.timedelta(seconds=options["timeout"])
    
    show=options["show"]
    output=options["output"]          
    rotationsAllowed=options["rotationsAllowed"]

    # VERSIONE DI DAVIDE
    if rotationsAllowed:
        vlsi = Model(currentdir+"/vlsi_diffn_flip.mzn")
    else:
        vlsi = Model(currentdir+"/vlsi_diffn.mzn")

    chuffed=Solver.lookup("chuffed")
    instance=Instance(chuffed,vlsi)
    instance["n"]=inst["n"]
    instance["w"]=inst["w"]
    instance["dim"]=inst["dim"]

    # SOLVE THE INSTANCE
    try:
        result=instance.solve(timeout=timeout,free_search=True)
        print(result)
        if(verbose):
            print("\n____STATISTICS____")
            for key,val in result.statistics.items():
                print(key,"=",val) 
            print("\n__________________")
        if show:
            utils.displaySolution(json.loads(str(result)))
        if output:
            utils.write_out(output,str(result))
    except minizinc.error.MiniZincWarning as e:
        print(e)
    except minizinc.error.MiniZincError as e:
        print(e)