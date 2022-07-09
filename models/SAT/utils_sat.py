from z3 import *

def large_rectangles(w_i, w_j, h_i, h_j, W, H):
    if w_i + w_j <= W and h_i + h_j <= H:
        return False
    elif w_i + w_j > W and h_i + h_j <= H:
        return "W"
    elif w_i + w_j <= W and h_i + h_j > H:
        return "H"

def same_rectangles(w1,w2,h1,h2):
    if w1 == w2 and h1 == h2:
        return True
    else:
        return False

def largest_rectangle(idx, max_idx):
    if idx == max_idx:
        return True
    else:
        return False
    
def no_overlap(W, H, widths, heights, i, j, flip, px, py, lr, ud):            
    dim1,dim2=(widths[i],heights[i]) if not flip else (heights[i],widths[i])
    cts=[]
    
    if lr:
        # lr(r_i,r_j)-> x_j > w_i
        cts.append(Or(
                Not(lr[i][j]),
                Not(px[j][dim1-1]),
            )) 

        for e in range(0,W-dim1):
            cts.append(Or(
                Not(lr[i][j]),
                Not(px[j][e+dim1]),
                px[i][e]
            ))

    if ud:
        # ud(r_i,r_j)-> y_j > h_i
        cts.append(Or(
                Not(ud[i][j]),
                Not(py[j][dim2-1])
            ))

        for f in range(0,H-dim2):
            cts.append(Or(
                Not(ud[i][j]),
                Not(py[j][f+dim2]),
                py[i][f]
            ))

    return cts

def getCoords(vars_dict, W, H, n, widths, heights, rot = False):
    x_sol = []
    y_sol = [] 
    w=[]
    h=[]
                
    for i in range(n):
        if rot:
            if vars_dict[f"f{i+1}"]:  
                w.append(heights[i])
                h.append(widths[i])
            else:
                w.append(widths[i])
                h.append(heights[i])
                
        x = 0
        while x < W:
            try:
                if vars_dict[f"px{i+1}_{x}"]:                
                    x_sol.append(x)
                    break
            except:
                pass
            x += 1
        y = 0
        
        while y < H:
            try:
                if vars_dict[f"py{i+1}_{y}"]:                
                    y_sol.append(y)
                    break
            except:
                pass
            y += 1
        
    return x_sol, y_sol, w, h