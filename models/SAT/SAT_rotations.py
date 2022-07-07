from z3 import * 
import inspect
import numpy as np
import matplotlib.pyplot as plt
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
sys.path.insert(0, currentdir)
import utils
import time

def getNewDims(model,widths,heights,f):
    w=[]
    h=[]
    for i in range(len(widths)):
        if model.evaluate(f[i]):
            w.append(heights[i])
            h.append(widths[i])
        else:
            w.append(widths[i])
            h.append(heights[i])
    return w,h 

def getCoords(m, x, y, W, H, n):
    x_sol = []
    y_sol = [] 
    
    for i in range(n):
        j = 0
        while j < W:
            if m.evaluate(x[i][j]):
                x_sol.append(j)
                break
            j += 1

        j = 0
        while j < H:
            if m.evaluate(y[i][j]):
                y_sol.append(j)
                break
            j += 1
    
    return [x_sol, y_sol]

def write_file(W, H, n, w, h, x, y, out_file):

    with open(out_file, 'w+') as f_out:
        f_out.write('{} {}\n'.format(W, H))
        f_out.write('{}\n'.format(n))

        for i in range(n):
            f_out.write('{} {} {} {}\n'.format(w[i], h[i], x[i], y[i]))

def read(filename):
    with open(filename) as file:  # Use file to refer to the file object
        first_line = file.readline().strip().split(" ")

        width = int(first_line[0])
        height = int(first_line[1])

        n = int(file.readline().strip())

        # Read all the remaining lines which contains the horizontal and vertical dimension of the i-th circuit
        # and its bottom left corner coordinate
        remaining_lines = file.readlines()

        # To remove \n
        remaining_lines = [line.strip() for line in remaining_lines if line.strip()]

        circuits = []
        solution = {'corners': []}

        for i in range(n):
            line = remaining_lines[i]
            line = line.split()
            circuits.append((int(line[0]), int(line[1])))
            solution['corners'].append((int(line[2]), int(line[3])))
        # Solution
    sol = {
        "w": width,
        "h": height,
        "n": n,
        "points" : np.array(circuits,\
                            dtype=[('w','i4'),('h','i4')])
    }

    #print(sol['points'])
    #print([(x+1,y+1) for (x,y) in solution['corners']])

    a = sol['points']
    b = solution['corners']

    l = [[sol['w'], sol['h']]]
    for i in range(len(a)):
        l.append([a[i][0],a[i][1],b[i][0]+1,b[i][1]+1])
    return l 

def solveInstance(instance):
    n = instance['n']
    W = instance['w']
    widths  = [i[0] for i in instance['dim']]
    heights = [i[1] for i in instance['dim']]
    print(instance)
    largest_idx = [w*h for w,h in zip(widths,heights)].index(max([w*h for w,h in\
                                                                        zip(widths,heights)]))
    tot_area=sum([w*h for w,h in zip(widths,heights)])

    stupidSol=utils.computeMostStupidSolution(instance)

    lb = int(tot_area/W)
    #     ub = int(2*max( 
    #                 max([ [p[0],p[1]] for p in instance['dim']],key=lambda p:p[0]*p[1]) [1] #Height of the block with the largest area
    #                 ,lb))+1 
    ub = stupidSol[0][1]+1
    H = int((lb+ub)/2)
    s_time = time.time()
    print(f"lb:{lb},ub:{ub}")
    while (lb < ub):
        s = Solver()
        print(f"Trying H:{H}")
        s.set("timeout", 300000)


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
        f = [Bool(f"f{i+1}") for i in range(n)] # f[i]: block i is flipped


        def no_overlap(i,j,fi,fj):
            dim1i,dim2i=(widths[i],heights[i]) if not fi else (heights[i],widths[i])
            dim1j,dim2j=(widths[j],heights[j]) if not fj else (heights[j],widths[j])
            cts=[]

            if dim1i == 26:
                print(W, dim1i)
                print(len(px))
                print(len(py))

            # lr(r_i,r_j)-> x_j > w_i
            cts.append(Or(
                    Not(lr[i][j]),
                    Not(px[j][dim1i-1]),
                )) 

            for e in range(0,W-dim1i):
                cts.append(Or(
                    Not(lr[i][j]),
                    px[i][e],
                    Not(px[j][e+dim1i]),
                ))

            # lr(r_j,r_i)-> x_i > w_j
            cts.append(Or(
                    Not(lr[j][i]),
                    Not(px[i][dim1j-1])
                ))

            for e in range(0,W-dim1j):
                cts.append(Or(
                    Not(lr[j][i]),
                    px[j][e],
                    Not(px[i][e+dim1j])
                ))

            # ud(r_i,r_j)-> y_j > h_i
            cts.append(Or(
                    Not(ud[i][j]),
                    Not(py[j][dim2i-1])
                ))

            for f in range(0,H-dim2i):
                cts.append(Or(
                    Not(ud[i][j]),
                    py[i][f],
                    Not(py[j][f+dim2i])
                ))

            # ud(r_j,r_i)-> y_i > h_j
            cts.append(Or(
                    Not(ud[j][i]),
                    Not(py[i][dim2j-1])
                ))

            for f in range(0,H-dim2j):
                cts.append(Or(
                    Not(ud[j][i]),
                    py[j][f],
                    Not(py[i][f+dim2j])
                ))
            return cts

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
            if i==largest_idx:
                s.add(Or(
                        And (Not(f[i]), And([px[i][e] for e in range(int((W-widths[i])/2),W)])),
                        And ( f[i],      And([px[i][e] for e in range(int((W-heights[i])/2),W)]))
                    )) # block i starts for sure before position W-wi-> x[i][j]=True for all j > W-wi 

                s.add(Or(
                    And (Not(f[i]), And([py[i][f] for f in range(int((H-heights[i])/2),H)])),
                    And (f[i],      And([py[i][f] for f in range(int((H-widths[i])/2),H)]))
                    ))
                    # same for the y coordinate 
            else:
                s.add(Or(
                        And (Not(f[i]), And([px[i][e] for e in range(W-widths[i],W)])),
                        And ( f[i],      And([px[i][e] for e in range(W-heights[i],W)]))
                    )) # block i starts for sure before position W-wi-> x[i][j]=True for all j > W-wi 

                s.add(Or(
                    And (Not(f[i]), And([py[i][f] for f in range(H-heights[i],H)])),
                    And (f[i],      And([py[i][f] for f in range(H-widths[i],H)]))
                    ))
                    # same for the y coordinate  
                        
            
            s.add([Or(Not(px[i][e]),px[i][e+1]) for e in range(W-1)]) #x[i][j] implies x[i][j+1]
            s.add([Or(Not(py[i][f]),py[i][f+1]) for f in range(H-1)]) #y[i][j] implies y[i][j+1]
                        
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
                if i<j:
                    s.add(Or(lr[i][j],lr[j][i],ud[i][j],ud[j][i]))
                    
                    # lr(r_i,r_j)-> x_j > w_i

                    s.add(Or(
                        And(Not(f[i]),Not(f[j]),*no_overlap(i,j,False,False)),
                        And(Not(f[i]),f[j],*no_overlap(i,j,False,True)),
                        And(f[i],Not(f[j]),*no_overlap(i,j,True,False)),
                        And(f[i],f[j],*no_overlap(i,j,True,True)),
                    ))
                    
        if s.check() == sat:
            ub = H
            print('SAT: ub ->',ub)
        else:
            lb = H + 1
            print("UNSAT: lb ->",lb)

        H =  int((lb+ub)/2)
            
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

    e_time = time.time() - s_time
    print("Time:", e_time)
    model=s.model()
    cx,cy=getCoords(model, px, py, W, H, n)
    new_w,new_h=getNewDims(model,widths,heights,f)

    sol=[[W,H]]+[[new_w[i],new_h[i],cx[i]+1,cy[i]+1] for i in range(n)]
    
    """
    # FOR DEBUGGING PURPOSES ONLY
    print(*["f_{}:{}\n".format(i+1,model.evaluate(f[i])) for i in range(n)])
    for i in range(n):
        for j in range(n):
            if i!=j:
                if model.evaluate(lr[i][j]):
                    print(f"{i+1} to the left of {j+1}")
                if model.evaluate(ud[i][j]):
                    print(f"{i+1} below {j+1}")    
    print(*["B_{}:({},{})\n".format(i+1,cx[i],cy[i]) for i in range(n)])
    print([model.evaluate(px[2][i]) for i in range(W)])
    print([model.evaluate(py[2][i]) for i in range(H)])
    """

    return sol 

if __name__=="__main__": 

    instn=int(sys.argv[1])
    instance=utils.loadInstance(currentdir+f"/../instances/ins-{instn}.txt")
    sol=solveInstance(instance)
    W=sol[0][0]
    H=sol[0][1]
    n=len(sol[1:])
    widths=[s[0] for s in sol[1:]]
    heights=[s[1] for s in sol[1:]]
    cx=[s[2]-1 for s in sol[1:]]
    cy=[s[3]-1 for s in sol[1:]]
    # WRITE OUT
    write_file(W, H, n, widths,
                    heights, cx, cy, currentdir+'./outputs_rot/out-' + str(instn) + '.txt')
    # DISPLAY
    #utils.display_solution(sol,title=f'Plate {instn}')
    print(sol)


