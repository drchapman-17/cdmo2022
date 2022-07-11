import time
import utils
from utils_sat import *
from z3 import *
import math
import sys


class vlsi_SAT_problem_rotations():
    def __init__(self,instance):
        self.instance=instance 
        self.model=None

    def solve(self, timeLimit = sys.maxsize, verbose=False):
        ''' VARIABLES '''

        n = self.instance['n']
        W = self.instance['w']
        widths  = [i[0] for i in self.instance['dim']]
        heights = [i[1] for i in self.instance['dim']]
        largest_idx = [w*h for w,h in zip(widths,heights)].index(max([w*h for w,h in\
                                                                            zip(widths,heights)]))   
        tot_area=sum([w*h for w,h in zip(widths,heights)])
        self.model = None
        
        naiveSolution = utils.computeNaiveSolution(self.instance)
        
        if not naiveSolution:
            return None

        lb = int(math.ceil(tot_area/W))
        ub = naiveSolution[0][1]+1
        
        if verbose:
            print("\n>Starting Lower Bound:", lb)
            print(">Starting Upper Bound:", ub)
        
        H = int((lb+ub)/2)
        
        s_time = time.time()
        
        while (lb < ub):
            ''' SOLVER WITH 5 MINUTES TIMEOUT'''
            self.s = Solver()

            self.s.set("timeout", int((timeLimit-(time.time()-s_time))*1000))

            if (time.time() > s_time + timeLimit):
                break
            elif verbose:
                print(f"\t>Trying H:{H}")
            '''
            ==================================================================
            The variable "f" points wether a component is flipped or not.
            ==================================================================
            '''
            px = [[Bool(f"px{i+1}_{x}") for x in range(W)] for i in range(n)] # x[i][i]: block i has y coordinate <=j
            py = [[Bool(f"py{i+1}_{y}") for y in range(H)] for i in range(n)] # x[i][i]: block i has y coordinate <=j
            lr = [[Bool(f"lr_{i+1}_{j+1}") if j!=i else 0 for j in range(n)] for i in range(n)]
            ud = [[Bool(f"ud_{i+1}_{j+1}") if i!=j else 0 for j in range(n)] for i in range(n)]
            f = [Bool(f"f{i+1}") for i in range(n)] # f[i]: block i is flipped

            # Exactly One constraint
            for i in range(n): 
                '''
                ==================================================================
                Ranges of each component change depending on "f".
                ==================================================================
                '''
                if largest_rectangle(i, largest_idx):
                    self.s.add(Or(
                            And (Not(f[i]), And([px[i][e] for e in range(int((W-widths[i])/2),W)])),
                            And ( f[i],      And([px[i][e] for e in range(int((W-heights[i])/2),W)]))
                        )) # block i starts for sure before position W-wi-> x[i][j]=True for all j > W-wi 

                    self.s.add(Or(
                        And (Not(f[i]), And([py[i][f] for f in range(int((H-heights[i])/2),H)])),
                        And (f[i],      And([py[i][f] for f in range(int((H-widths[i])/2),H)]))
                        ))
                        # same for the y coordinate 
                else:
                    self.s.add(Or(
                            And (Not(f[i]), And([px[i][e] for e in range(W-widths[i],W)])),
                            And ( f[i],      And([px[i][e] for e in range(W-heights[i],W)]))
                        )) # block i starts for sure before position W-wi-> x[i][j]=True for all j > W-wi 

                    self.s.add(Or(
                        And (Not(f[i]), And([py[i][f] for f in range(H-heights[i],H)])),
                        And (f[i],      And([py[i][f] for f in range(H-widths[i],H)]))
                        ))
                        # same for the y coordinate  

                self.s.add([Or(Not(px[i][e]),px[i][e+1]) for e in range(W-1)]) #x[i][j] implies x[i][j+1]
                self.s.add([Or(Not(py[i][f]),py[i][f+1]) for f in range(H-1)]) #y[i][j] implies y[i][j+1]

                for j in range(n):
                    '''
                    ==================================================================
                    We must take in account the four possible orientations of
                    two components.
                    ==================================================================
                    '''
                    wi,wj,hi,hj=widths[i],widths[j],heights[i],heights[j]    
                    cts=[] 
                    if i<j:
                        if large_rectangles(widths[i],widths[j],heights[i],heights[j], W, H) == False:
                                if same_rectangles(widths[i],widths[j],heights[i],heights[j]):
                                    self.s.add(Or(lr[i][j],ud[i][j],ud[j][i]))
                                    
                                    if wi<=W and hi<=H and wj<=W and hj<=H: 
                                        cts.append(And(Not(f[i]),Not(f[j]),
                                                    *no_overlap(W,H,widths,heights,\
                                                                            i,j,False,px,py,lr,ud),
                                                    *no_overlap(W,H,widths,heights,\
                                                                            j,i,False,px,py,False,ud),
                                                    ))
                                    if wi<=H and hi<=W and wj<=W and hj<=H:
                                        cts.append(And(f[i],Not(f[j]),
                                                    *no_overlap(W,H,widths,heights,\
                                                                            i,j,True,px,py,lr,ud),
                                                    *no_overlap(W,H,widths,heights,\
                                                                            j,i,False,px,py,False,ud),
                                                    ))
                                    if wi<=W and hi<=H and wj<=H and hj<=W:                        
                                        cts.append(And(Not(f[i]),f[j],
                                                    *no_overlap(W,H,widths,heights,\
                                                                            i,j,False,px,py,lr,ud),
                                                    *no_overlap(W,H,widths,heights,\
                                                                            j,i,True,px,py,False,ud),
                                                    ))
                                    if wi<=H and hi<=W and wj<=H and hj<=W:                        
                                        cts.append(And(f[i],f[j],
                                                    *no_overlap(W,H,widths,heights,\
                                                                            i,j,True,px,py,lr,ud),
                                                    *no_overlap(W,H,widths,heights,\
                                                                            j,i,True,px,py,False,ud),
                                                    ))
                                    self.s.add(Or(cts))

                                    self.s.add(Or(
                                            Not(ud[i][j]),
                                            lr[j][i]
                                    ))
                                else:
                                    if not largest_rectangle(j, largest_idx):
                                        self.s.add(Or(lr[i][j],lr[j][i],ud[i][j],ud[j][i]))     
                                        
                                        if wi<=W and hi<=H and wj<=W and hj<=H: 
                                            cts.append(And(Not(f[i]),Not(f[j]),
                                                        *no_overlap(W,H,widths,heights,\
                                                                                i,j,False,px,py,lr,ud),
                                                        *no_overlap(W,H,widths,heights,\
                                                                                j,i,False,px,py,lr,ud),
                                                        ))
                                        if wi<=H and hi<=W and wj<=W and hj<=H:
                                            cts.append(And(f[i],Not(f[j]),
                                                        *no_overlap(W,H,widths,heights,\
                                                                                i,j,True,px,py,lr,ud),
                                                        *no_overlap(W,H,widths,heights,\
                                                                                j,i,False,px,py,lr,ud),
                                                        ))
                                        if wi<=W and hi<=H and wj<=H and hj<=W:                        
                                            cts.append(And(Not(f[i]),f[j],
                                                        *no_overlap(W,H,widths,heights,\
                                                                                i,j,False,px,py,lr,ud),
                                                        *no_overlap(W,H,widths,heights,\
                                                                                j,i,True,px,py,lr,ud),
                                                        ))
                                        if wi<=H and hi<=W and wj<=H and hj<=W:                        
                                            cts.append(And(f[i],f[j],
                                                        *no_overlap(W,H,widths,heights,\
                                                                                i,j,True,px,py,lr,ud),
                                                        *no_overlap(W,H,widths,heights,\
                                                                                j,i,True,px,py,lr,ud),
                                                        ))
                                        self.s.add(Or(cts))
                                    else:
                                        self.s.add(Or(lr[j][i],ud[i][j],ud[j][i]))
                                        
                                        if wi<=W and hi<=H and wj<=W and hj<=H: 
                                            cts.append(And(Not(f[i]),Not(f[j]),
                                                        *no_overlap(W,H,widths,heights,\
                                                                                i,j,False,px,py,False,ud),
                                                        *no_overlap(W,H,widths,heights,\
                                                                                j,i,False,px,py,lr,ud),
                                                        ))
                                        if wi<=H and hi<=W and wj<=W and hj<=H:
                                            cts.append(And(f[i],Not(f[j]),
                                                        *no_overlap(W,H,widths,heights,\
                                                                                i,j,True,px,py,False,ud),
                                                        *no_overlap(W,H,widths,heights,\
                                                                                j,i,False,px,py,lr,ud),
                                                        ))
                                        if wi<=W and hi<=H and wj<=H and hj<=W:                        
                                            cts.append(And(Not(f[i]),f[j],
                                                        *no_overlap(W,H,widths,heights,\
                                                                                i,j,False,px,py,False,ud),
                                                        *no_overlap(W,H,widths,heights,\
                                                                                j,i,True,px,py,lr,ud),
                                                        ))
                                        if wi<=H and hi<=W and wj<=H and hj<=W:                        
                                            cts.append(And(f[i],f[j],
                                                        *no_overlap(W,H,widths,heights,\
                                                                                i,j,True,px,py,False,ud),
                                                        *no_overlap(W,H,widths,heights,\
                                                                                j,i,True,px,py,lr,ud),
                                                        ))
                                        self.s.add(Or(cts))
                                        
                        elif large_rectangles(widths[i],widths[j],heights[i],heights[j], W, H) == "W":
                            self.s.add(Or(lr[j][i],ud[i][j],ud[j][i]))

                            if wi<=W and hi<=H and wj<=W and hj<=H: 
                                cts.append(And(Not(f[i]),Not(f[j]),
                                            *no_overlap(W,H,widths,heights,\
                                                                    i,j,False,px,py,False,ud),
                                            *no_overlap(W,H,widths,heights,\
                                                                    j,i,False,px,py,lr,ud),
                                            ))
                            if wi<=H and hi<=W and wj<=W and hj<=H:
                                cts.append(And(f[i],Not(f[j]),
                                            *no_overlap(W,H,widths,heights,\
                                                                    i,j,True,px,py,False,ud),
                                            *no_overlap(W,H,widths,heights,\
                                                                    j,i,False,px,py,lr,ud),
                                            ))
                            if wi<=W and hi<=H and wj<=H and hj<=W:                        
                                cts.append(And(Not(f[i]),f[j],
                                            *no_overlap(W,H,widths,heights,\
                                                                    i,j,False,px,py,False,ud),
                                            *no_overlap(W,H,widths,heights,\
                                                                    j,i,True,px,py,lr,ud),
                                            ))
                            if wi<=H and hi<=W and wj<=H and hj<=W:                        
                                cts.append(And(f[i],f[j],
                                            *no_overlap(W,H,widths,heights,\
                                                                    i,j,True,px,py,False,ud),
                                            *no_overlap(W,H,widths,heights,\
                                                                    j,i,True,px,py,lr,ud),
                                            ))
                            self.s.add(Or(cts))

                        elif large_rectangles(widths[i],widths[j],heights[i],heights[j], W, H) == "H":
                            if same_rectangles(widths[i],widths[j],heights[i],heights[j]):
                                self.s.add(lr[i][j])

                                if wi<=W and hi<=H and wj<=W and hj<=H: 
                                    cts.append(And(Not(f[i]),Not(f[j]),
                                                *no_overlap(W,H,widths,heights,\
                                                                        i,j,False,px,py,lr,False)
                                                ))
                                if wi<=H and hi<=W and wj<=W and hj<=H:
                                    cts.append(And(f[i],Not(f[j]),
                                                *no_overlap(W,H,widths,heights,\
                                                                        i,j,True,px,py,lr,False)
                                                ))
                                if wi<=W and hi<=H and wj<=H and hj<=W:                        
                                    cts.append(And(Not(f[i]),f[j],
                                                *no_overlap(W,H,widths,heights,\
                                                                        i,j,False,px,py,lr,False)
                                                ))
                                if wi<=H and hi<=W and wj<=H and hj<=W:                        
                                    cts.append(And(f[i],f[j],
                                                *no_overlap(W,H,widths,heights,\
                                                                        i,j,True,px,py,lr,False)
                                                ))
                                self.s.add(Or(cts))

                                self.s.add(Or(
                                        Not(ud[i][j]),
                                        lr[j][i]
                                ))  
                            else:                            
                                self.s.add(Or(lr[i][j],lr[j][i]))

                                if wi<=W and hi<=H and wj<=W and hj<=H: 
                                    cts.append(And(Not(f[i]),Not(f[j]),
                                                *no_overlap(W,H,widths,heights,\
                                                                        i,j,False,px,py,lr,False),
                                                *no_overlap(W,H,widths,heights,\
                                                                        j,i,False,px,py,lr,False),
                                                ))
                                if wi<=H and hi<=W and wj<=W and hj<=H:
                                    cts.append(And(f[i],Not(f[j]),
                                                *no_overlap(W,H,widths,heights,\
                                                                        i,j,True,px,py,lr,False),
                                                *no_overlap(W,H,widths,heights,\
                                                                        j,i,False,px,py,lr,False),
                                                ))
                                if wi<=W and hi<=H and wj<=H and hj<=W:                        
                                    cts.append(And(Not(f[i]),f[j],
                                                *no_overlap(W,H,widths,heights,\
                                                                        i,j,False,px,py,lr,False),
                                                *no_overlap(W,H,widths,heights,\
                                                                        j,i,True,px,py,lr,False),
                                                ))
                                if wi<=H and hi<=W and wj<=H and hj<=W:                        
                                    cts.append(And(f[i],f[j],
                                                *no_overlap(W,H,widths,heights,\
                                                                        i,j,True,px,py,lr,False),
                                                *no_overlap(W,H,widths,heights,\
                                                                        j,i,True,px,py,lr,False),
                                                ))
                                self.s.add(Or(cts))

            if self.s.check() == sat:
                if (time.time() - s_time <= timeLimit): 
                    ub = H
                    self.model = self.s.model()            
                    if verbose:
                        print(f'\t\t>SAT - ub: {ub}, {time.time() - s_time} s')
                
            else:
                lb = H + 1
                if (time.time() - s_time <= timeLimit) and verbose:
                    print(f'\t\t>UNSAT - lb: {lb}, {time.time() - s_time} s')

                
            H =  int((lb+ub)/2)
            
            '''
            ==================================================================
            'Bisection Method':
                while lb < ub
                    o := (lb + ub)/2;
                    result := Ψ ∪ {ph_o};
                    if result is SAT
                        then ub := o;
                        else lb := o + 1;
                end while
            ==================================================================
            '''
        
        self.e_time = time.time() - s_time

        
        if self.model == None:
            return None, self.e_time
        elif self.e_time > timeLimit:
            variables = { str(d):self.model.evaluate(self.model[d]) for d in self.model }
            cx,cy,widths,heights = getCoords(variables, W, ub, n, widths, heights, True)

            self.sol = [[W,ub]]+[[widths[i],heights[i],cx[i]+1,cy[i]+1]\
                        for i in range(min(len(cx),len(cy),len(widths),len(heights)))]
            
            return self.sol, self.e_time
        else:
            variables = { str(d):self.model.evaluate(self.model[d]) for d in self.model }
                    
            cx,cy,widths,heights = getCoords(variables, W, H, n, widths, heights, True)
            self.sol=[[W,H]]+[[widths[i],heights[i],cx[i]+1,cy[i]+1] for i in range(n)]
            
            return self.sol, self.e_time

    
    def getModel():
        return self.model
    
    def getElapsedTime():
        return self.e_time

    def getSolution():
        return self.sol

    def getSolver():
        return self.s