import time
import utils
import utils_sat


class VLSI_Problem():
    
    def __init__(self,instance):
        self.instance=instance 
        
        ''' VARIABLES '''
        n = instance['n']
        W = instance['w']
            
        widths  = [i[0] for i in instance['dim']]
        heights = [i[1] for i in instance['dim']]

        largest_idx = [w*h for w,h in zip(widths,heights)].index(max([w*h for w,h in\
                                                                            zip(widths,heights)]))   
        
        tot_area=sum([w*h for w,h in zip(widths,heights)])

        lb = int(tot_area/W)
        naiveSolution = utils.computeMostStupidSolution(instance)
        ub = naiveSolution[0][1]+1
        
        H = lb
        
        s_time = time.time()
        
        ''' SOLVER WITH 5 MINUTES TIMEOUT'''
        self.s = Solver()
        self.s.set("timeout", 300000)

        while (lb < ub):
            if (time.time() > s_time + 300):
                self.model = None
                self.px = None
                self.py = None
                self.H = None
                self.e_time = 0.0
            
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
            self.px = [[Bool(f"px{i+1}_{x}") for x in range(W)] for i in range(n)] # x[i][i]: block i has y coordinate <=j
            self.py = [[Bool(f"py{i+1}_{y}") for y in range(H)] for i in range(n)] # x[i][i]: block i has y coordinate <=j
            self.lr = [[Bool(f"lr_{i+1}_{j+1}") if j!=i else 0 for j in range(n)] for i in range(n)]
            self.ud = [[Bool(f"ud_{i+1}_{j+1}") if i!=j else 0 for j in range(n)] for i in range(n)]

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
                
                # LS 
                if largest_rectangle(i, largest_idx):
                    self.s.add([self.px[i][e] for e in range(int((W-widths[i])/2),W)]) # block i starts for sure before position W-wi-> x[i][j]=True for all j > W-wi 
                    self.s.add([self.py[i][f] for f in range(int((H-heights[i])/2),H)]) # same for the y coordinate 
                else:
                    self.s.add([self.px[i][e] for e in range(W-widths[i],W)]) # block i starts for sure before position W-wi-> x[i][j]=True for all j > W-wi 
                    self.s.add([self.py[i][f] for f in range(H-heights[i],H)]) # same for the y coordinate 
                # LS
                
                self.s.add([Or(Not(self.px[i][e]),self.px[i][e+1]) for e in range(W-1)]) #x[i][j] implies x[i][j+1]
                self.s.add([Or(Not(self.py[i][f]),self.py[i][f+1]) for f in range(H-1)]) #y[i][j] implies y[i][j+1]

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
                    # LR 
                    if utils_sat.large_rectangles(widths[i],widths[j],heights[i],heights[j], W, H) == "":
                        if i<j and not utils_sat.same_rectangles(widths[i],widths[j],heights[i],heights[j]):
                            if not utils_sat.largest_rectangle(j, largest_idx):
                                self.s.add(Or(self.lr[i][j],self.lr[j][i],self.ud[i][j],self.ud[j][i]))

                                self.s.add(
                                    *utils_sat.no_overlap(W,H,widths,heights,i,j,False,False,self.px,self.py,self.lr,self.ud),
                                    *utils_sat.no_overlap(W,H,widths,heights,j,i,False,False,self.px,self.py,self.lr,self.ud)
                                )
                            else:
                                self.s.add(Or(self.lr[j][i],self.ud[i][j],self.ud[j][i]))

                                self.s.add(
                                    *utils_sat.no_overlap(W,H,widths,heights,i,j,False,False,self.px,self.py,False,self.ud),
                                    *utils_sat.no_overlap(W,H,widths,heights,j,i,False,False,self.px,self.py,self.lr,self.ud)
                                )
                                
                        elif i<j and utils_sat.same_rectangles(widths[i],widths[j],heights[i],heights[j]):
                            self.s.add(Or(self.lr[i][j],self.ud[i][j],self.ud[j][i]))

                            self.s.add(
                                *utils_sat.no_overlap(W,H,widths,heights,i,j,False,False,self.px,self.py,self.lr,self.ud),
                                *utils_sat.no_overlap(W,H,widths,heights,j,i,False,False,self.px,self.py,False,self.ud)
                            )
                                
                            self.s.add(Or(
                                    Not(self.ud[i][j]),
                                    self.lr[j][i]
                            ))
                            
                    elif utils_sat.large_rectangles(widths[i],widths[j],heights[i],heights[j], W, H) == "W":
                        if i<j:
                            self.s.add(Or(self.ud[i][j],self.ud[j][i]))

                            self.s.add(
                                *utils_sat.no_overlap(W,H,widths,heights,i,j,False,False,self.px,self.py,False,self.ud),
                                *utils_sat.no_overlap(W,H,widths,heights,j,i,False,False,self.px,self.py,False,self.ud)
                            )
                            
                    elif utils_sat.large_rectangles(widths[i],widths[j],heights[i],heights[j], W, H) == "H":
                        if i<j and not utils_sat.same_rectangles(widths[i],widths[j],heights[i],heights[j]):
                            self.s.add(Or(self.lr[i][j],self.lr[j][i]))
                            
                            self.s.add(
                                *utils_sat.no_overlap(W,H,widths,heights,i,j,False,False,self.px,self.py,self.lr,False),
                                *utils_sat.no_overlap(W,H,widths,heights,j,i,False,False,self.px,self.py,self.lr,False)
                            )
                            
                        elif i<j and utils_sat.same_rectangles(widths[i],widths[j],heights[i],heights[j]):
                            self.s.add(self.lr[i][j])
                            
                            self.s.add(
                                *utils_sat.no_overlap(W,H,widths,heights,i,j,False,False,self.px,self.py,self.lr,False)
                            )
                            
                            self.s.add(Or(
                                    Not(self.ud[i][j]),
                                    self.lr[j][i]
                            ))                    

            if self.s.check() == sat:
                ub = H
            else:
                lb = H + 1

            self.H =  int((lb+ub)/2)
            
            '''
            ==================================================================
            'Bisection Method':
                while lb < ub
                    o := (lb + ub)/2;
                    resubt := Ψ ∪ {ph_o};
                    if resubt is SAT
                        then ub := o;
                        else lb := o + 1;
                end while
            ==================================================================
            '''
        
        self.e_time = time.time() - s_time


    def solve(self,timeLimit=None,verbose=False):
        self.problem.solve(pulp.PULP_CBC_CMD(timeLimit=timeLimit, msg=1 if verbose else 0, gapRel=0))

    def getStatusMessage(self):
        return LpStatus[self.problem.status]+ ("(or maybe time-out idk lol)" if self.problem.status==1 else "")
    
    def getStatusCode(self):
        return self.problem.status

    def getSolution(self):
        if self.problem.status<0:
            return None
        vn=[var.name for var in self.problem.variables()]
        vv=[var.varValue for var in self.problem.variables()]
        solution=[[self.instance["w"],int(vv[vn.index("H_c")])]]
        for i in range(self.instance["n"]):
            solution.append([int(vv[vn.index(f"W_{i}")]) ,int(vv[vn.index(f"H_{i}")]) \
                ,int(vv[vn.index(f"Xl_{i}")])+1 ,int(vv[vn.index(f"Yb_{i}")])+1])
        return solution
        