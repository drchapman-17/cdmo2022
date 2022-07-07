import datetime
from minizinc import Instance,Model,Solver
import minizinc
import utils
import json

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

    print(inst)


    # VERSIONE DI DAVIDE
    if rotationsAllowed:
        vlsi = Model("./CP/vlsi_diffn_flip.mzn")
    else:
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
    try:
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
    except minizinc.error.MiniZincWarning as e:
        print(e)
    except minizinc.error.MiniZincError as e:
        print(e)