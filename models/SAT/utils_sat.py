from z3 import *

def large_rectangles(w_i, w_j, h_i, h_j, W, H):
    if w_i + w_j <= W and h_i + h_j <= H:
        return ""
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

def no_overlap(W, H, widths, heights, i, j, fi, fj, px, py, lr, ud):    
    dim1i,dim2i=(widths[i],heights[i]) if not fi else (heights[i],widths[i])
    dim1j,dim2j=(widths[j],heights[j]) if not fj else (heights[j],widths[j])
    cts=[]
    
    if lr:
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

    if ud:
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

    return cts

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