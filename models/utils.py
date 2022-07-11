import matplotlib.pyplot as plt
import sys 

def loadInstance(path):
    try:
        with open(path) as f:
            lines=f.readlines()
            w=int(lines[0])
            n=int(lines[1])
            elements=[]
            for i in range(n):
                x,y=lines[2+i].split()
                x=int(x)
                y=int(y)
                elements.append([x,y])
            return({"n":n,"w":w,"dim":elements})
    except Exception as e: 
        print(e)
        sys.exit(2)

def displaySolution(sol,**kwargs):
    title=""
    for key, value in kwargs.items():
        if key=="title": title=kwargs["title"]
        else: assert False, f"Argument \"{key}\" not recognized"

    W=sol[0][0]
    H=sol[0][1]
    n=len(sol[1:])
    sizes_circuits=[[s[0],s[1]] for s in sol[1:]]
    pos_circuits=[[s[2],s[3]] for s in sol[1:]]
    _, ax = plt.subplots()
    cmap = plt.cm.get_cmap('Set3', n)
    #ax = plt.gca()
    plt.title(title)
    
    if len(pos_circuits) > 0:
        for i in range(n):
            rect = plt.Rectangle([pos_circuits[i][0]-1,pos_circuits[i][1]-1], *sizes_circuits[i], edgecolor="#333", facecolor=cmap(i))
            ax.add_patch(rect)
    x_left, x_right = ax.get_xlim()
    y_low, y_high = ax.get_ylim()
    ax.set_aspect(abs((x_right-x_left)/(y_low-y_high))*1.0)
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    
    plt.xticks([])
    plt.yticks([])

    plt.savefig("plot.png", edgecolor='w', facecolor = 'w')


def isFeasible(sol): 
    w=sol[0][0]
    h=sol[0][1]
    blocks=sol[1:]
    n=len(blocks)
    for i in range(n):
        w1,h1,x1,y1=blocks[i]
        x1-=1
        y1-=1
        if w1<=0 or h1<=0: 
            return False 
        if x1<0 or y1<0 or x1+w1>w or y1+h1>h: 
            return False 
        for j in range(n):
            if i!=j:
                w2,h2,x2,y2=blocks[j]
                x2-=1
                y2-=1
                if (isOverlap([x1,y1,x1+w1,y1+h1],[x2,y2,x2+w2,y2+h2])):
                    print(x1,x1+w1,x2,x2+w2)
                    print(f"{i} and {j} overlap")
                    return False 
    return True

def isOverlap(R1, R2):
    if (R1[0]>=R2[2]) or (R1[2]<=R2[0]) or (R1[3]<=R2[1]) or(R1[1]>=R2[3]):
        return False
    else:
        return True

def existsOverlap(x1,y1,w1,h1,res):
    for b in res:
        x2=b[2]
        y2=b[3]
        w2=b[0]
        h2=b[1]        
        if isOverlap([x1,y1,x1+w1,y1+h1],[x2,y2,x2+w2,y2+h2]): return True
    return False

def computeNaiveSolution(instance,rotationsAllowed=False):
    n=instance['n']
    W=instance['w']
    dim=instance['dim']
    for el in dim:
        if el[0]>W and el[1]>W:
            return None
        elif el[0]>W:
            if rotationsAllowed: el[0],el[1]=el[1],el[0]
            else: return None
    a=sorted(enumerate(dim), key=lambda b:(b[1][1],b[1][0]) ,reverse=True)
    dim=[i[1] for i in a]
    idx=[i[0] for i in a]
    p=[d[0] for d in dim]
    q=[d[1] for d in dim]
    res=[]
    res.append([p[0],q[0],0,0])
    for i in range(1,n):
        appended=False
        x=0
        y=0
        while not appended:
            if existsOverlap(x,y,p[i],q[i],res):
                if(x>=W-p[i]):
                    x=0
                    y+=1
                else:
                    x+=1
            else: 
                res.append([p[i],q[i],x,y])
                appended=True
    res=[res[i] for i in idx] #Sort back the array to the original ordering
    H=max([b[1]+b[3] for b in res])
    sol=[[W,H]]+[[r[0],r[1],r[2]+1,r[3]+1]for r in res]
    return sol

def writeSolution(filename,sol):
    W=sol[0][0]
    H=sol[0][1]
    n=len(sol[1:])
    w=[s[0] for s in sol[1:]]
    h=[s[1] for s in sol[1:]]
    x=[s[2]-1 for s in sol[1:]]
    y=[s[3]-1 for s in sol[1:]]
    with open(filename, 'w+') as f_out:
        f_out.write('{} {}\n'.format(W, H))
        f_out.write('{}\n'.format(n))
        for i in range(n):
            f_out.write('{} {} {} {}\n'.format(w[i], h[i], x[i], y[i]))

def readSolution(filename):
    with open(filename) as file:  # Use file to refer to the file object
        first_line = file.readline().split()
        w = int(first_line[0])
        h= int(first_line[1])
        n = int(file.readline())
        # Read all the remaining lines which contains the horizontal and vertical dimension of the i-th circuit
        # and its bottom left corner coordinate
        remaining_lines = file.readlines()
        sol=[[w,h]]
        for i in range(n):
            b = remaining_lines[i].split()
            sol.append([int(b[0]),int(b[1]),int(b[2])+1,int(b[3])+1])
    return sol 