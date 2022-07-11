import time
import utils
from utils_sat import *
from z3 import *
import math
import sys

class vlsi_SAT_problem():
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
            return None,0.0

        lb = int(math.ceil(tot_area/W))
        ub = naiveSolution[0][1]+1
        
        if verbose:
            print("\n>Starting Lower Bound:", lb)
            print(">Starting Upper Bound:", ub)
            
        H = int((lb+ub)/2)
        
        
        s_time = time.time()
        while (lb < ub):
            self.s = Solver()
            
            ''' SOLVER WITH 5 MINUTES TIMEOUT'''
            self.s.set("timeout", int((timeLimit-(time.time()-s_time))*1000))


            if (time.time() > s_time + timeLimit):
                break
            elif verbose:
                print(f"\t>Trying H:{H}")
            
            '''
            ==================================================================
            Let x_i and y_i be integer variables such that the pair (x_i, y_i)
            represents the position of lower left coordinates of the rectangle
            ri in the strip.
            The domains of x_i and y_i are as folbows.
                                D(x_i) = {a ∈ N | 0 ≤ a ≤ W − w_i}
                                D(y_i) = {a ∈ N | 0 ≤ a ≤ H − h_i}
            ==================================================================
            Let r_i, r_j ∈ R(i != j) be two rectangles. We use two
            kinds of propositional variables: lr_i,j and ud_i,j.
            lr_i,j is true if r_i are placed at the left to the r_j.
            ud_i,j is true if r_i are placed at the downward to the r_j.

            ==================================================================
            For each rectangles r_i,r_j (i < j), we have the non-overlapping
            constraints:
                                lr_i,j ∨ lr_j,i ∨ ud_i,j ∨ ud_j,i
                                    ¬lr_i,j ∨ (x_i + w_i ≤ x_j)
                                    ¬lr_j,i ∨ (x_j + w_j ≤ x_i)
                                    ¬ud_i,j ∨ (y_i + h_i ≤ y_j)
                                    ¬ud_j,i ∨ (y_j + h_j ≤ y_i)
            The parts between parentheses are encoded into SAT by using order
            encoding.
            '''
            px = [[Bool(f"px{i+1}_{x}") for x in range(W)] for i in range(n)] # x[i][i]: block i has y coordinate <=j
            py = [[Bool(f"py{i+1}_{y}") for y in range(H)] for i in range(n)] # x[i][i]: block i has y coordinate <=j
            lr = [[Bool(f"lr_{i+1}_{j+1}") if j!=i else 0 for j in range(n)] for i in range(n)]
            ud = [[Bool(f"ud_{i+1}_{j+1}") if i!=j else 0 for j in range(n)] for i in range(n)]

            # Exactly One constraint
            for i in range(n): 
                '''
                ==================================================================
                Order encoding is a generalization of the encoding method
                originally used by Crawford and Baker for Job-Shop
                Scheduling problems.
                It uses a different Boolean variable P_x,a representing x ≤ a
                for each integer variable x and integer value a.
                
                For each rectangle r_i, and integer e and f such that
                0 ≤ e ≤ W − wi and 0 ≤ f ≤ H − h_i, we have the 2-literal
                axiom clauses due to order encoding,
                                    ¬ px_i,e ∨ px_i,e+1
                                    ¬ py_i, f ∨ py_i, f +1
                ==================================================================
                '''         
                if largest_rectangle(i, largest_idx):
                    self.s.add([px[i][e] for e in range(int((W-widths[i])/2),W)]) # block i starts for sure before position W-wi-> x[i][j]=True for all j > W-wi 
                    self.s.add([py[i][f] for f in range(int((H-heights[i])/2),H)]) # same for the y coordinate 
                else:
                    self.s.add([px[i][e] for e in range(W-widths[i],W)]) # block i starts for sure before position W-wi-> x[i][j]=True for all j > W-wi 
                    self.s.add([py[i][f] for f in range(H-heights[i],H)]) # same for the y coordinate 
                
                self.s.add([Or(Not(px[i][e]),px[i][e+1]) for e in range(W-1)]) #x[i][j] implies x[i][j+1]
                self.s.add([Or(Not(py[i][f]),py[i][f+1]) for f in range(H-1)]) #y[i][j] implies y[i][j+1]

                for j in range(n):
                    '''
                    ==================================================================
                    For each rectangles i,j (i < j), we have the non-overlapping
                    constraints as the 4-literal clauses:
                                    lr_i,j ∨ lr_j,i ∨ ud_i,j ∨ ud_j,i 
                                    
                    For each rectangles i, j (i < j), and integer e and f such that
                    0 ≤ e < W − wi and 0 ≤ f < H − h j, we also have the
                    non-overlapping constraints as the 3-literal clauses:
                                    ¬lr_i,j ∨ px_i,e ∨ ¬px_j,e + w_i
                                    ¬lr_j,i ∨ px_j,e ∨ ¬px_i,e + w_j
                                    ¬ud_i,j ∨ py_i,f ∨ ¬py_j,f + h_i
                                    ¬ud_j,i ∨ py_j,f ∨ ¬py_i,f + h_j
                    ==================================================================
                    '''
                    if i<j:  
                        if large_rectangles(widths[i],widths[j],heights[i],heights[j], W, H) == False:
                            if same_rectangles(widths[i],widths[j],heights[i],heights[j]):
                                self.s.add(Or(lr[i][j],ud[i][j],ud[j][i]))

                                self.s.add(
                                    *no_overlap(W,H,widths,heights,i,j,False,px,py,lr,ud),
                                    *no_overlap(W,H,widths,heights,j,i,False,px,py,False,ud)
                                )

                                self.s.add(Or(
                                        Not(ud[i][j]),
                                        lr[j][i]
                                ))
                            else:
                                if not largest_rectangle(j, largest_idx):
                                    self.s.add(Or(lr[i][j],lr[j][i],ud[i][j],ud[j][i]))

                                    self.s.add(
                                        *no_overlap(W,H,widths,heights,i,j,False,px,py,lr,ud),
                                        *no_overlap(W,H,widths,heights,j,i,False,px,py,lr,ud)
                                    )
                                else:
                                    self.s.add(Or(lr[j][i],ud[i][j],ud[j][i]))

                                    self.s.add(
                                        *no_overlap(W,H,widths,heights,i,j,False,px,py,False,ud),
                                        *no_overlap(W,H,widths,heights,j,i,False,px,py,lr,ud)
                                    )
                        elif large_rectangles(widths[i],widths[j],heights[i],heights[j], W, H) == "W":
                            self.s.add(Or(ud[i][j],ud[j][i]))

                            self.s.add(
                                *no_overlap(W,H,widths,heights,i,j,False,px,py,False,ud),
                                *no_overlap(W,H,widths,heights,j,i,False,px,py,False,ud)
                            )

                        elif large_rectangles(widths[i],widths[j],heights[i],heights[j], W, H) == "H":
                            if same_rectangles(widths[i],widths[j],heights[i],heights[j]):
                                self.s.add(lr[i][j])

                                self.s.add(
                                    *no_overlap(W,H,widths,heights,i,j,False,px,py,lr,False)
                                )

                                self.s.add(Or(
                                        Not(ud[i][j]),
                                        lr[j][i]
                                ))  
                            else:                            
                                self.s.add(Or(lr[i][j],lr[j][i]))

                                self.s.add(
                                    *no_overlap(W,H,widths,heights,i,j,False,px,py,lr,False),
                                    *no_overlap(W,H,widths,heights,j,i,False,px,py,lr,False)
                                )
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
            cx,cy,_,_ = getCoords(variables, W, ub, n, widths, heights)

            self.sol = [[W,ub]]+[[widths[i],heights[i],cx[i]+1,cy[i]+1]\
                        for i in range(min(len(cx),len(cy),len(widths),len(heights)))]
            
            return self.sol, self.e_time
        else:
            variables = { str(d):self.model.evaluate(self.model[d]) for d in self.model }
            cx,cy,_,_ = getCoords(variables, W, H, n, widths, heights)
            
            self.sol=[[W,H]]+[[widths[i],heights[i],cx[i]+1,cy[i]+1]\
                        for i in range(n)]
            
            return self.sol, self.e_time
    
    def getModel():
        return self.model
    
    def getElapsedTime():
        return self.e_time
    
    def getSolution():
        return self.sol

    def getSolver():
        return self.s