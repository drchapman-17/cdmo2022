import numpy as np
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

def show(l,**kwargs):
    lw=1.5
    figsize=None
    for key, value in kwargs.items():
        if key=="lw": lw=kwargs["lw"]
        elif key=="figsize": figsize=kwargs["figsize"]
        else: assert False, f"Argument \"{key}\" not recognized"
    fig, (ax1, ax2) = plt.subplots(2, 1,figsize=figsize)    
    dim_img_in=(np.sum([i[0] for i in l[1:]])+2*len(l)-4, max([i[1] for i in l[1:]]))
    img_in=np.zeros(shape=dim_img_in)
    pos=0
    c=0
    for i in l[1:]:
        c-=1
        i[2]-=1
        i[3]-=1
        img_in[pos:pos+i[0], 0:i[1]]=c
        pos+=i[0]+2
    
    ax1.imshow(np.transpose(img_in), cmap='terrain')
    ax1.set_xticks(np.arange(dim_img_in[0]+1)-0.5)
    ax1.set_xticklabels([])
    ax1.set_yticks(np.arange(dim_img_in[1]+1)-0.5)
    ax1.set_yticklabels([])
    ax1.set_xlim(-0.5,dim_img_in[0]-0.5)
    ax1.set_ylim(-0.5,dim_img_in[1]-0.5)
    ax1.grid(color='k', linestyle='-', linewidth=lw)
        
    dim_img_out=[l[0][0], l[0][1]+1]
    img_out=np.zeros(shape=dim_img_out)
    c=0
    
    for i in l[1:]:
        c-=1
        img_out[i[2]:i[2]+i[0],i[3]:i[3]+i[1]]=c        

    ax2.imshow(np.transpose(img_out), cmap='terrain')
    ax2.set_xticks(np.arange(dim_img_out[0]+1)-0.5)#,labels=[])
    ax2.set_xticklabels([])
    ax2.set_yticks(np.arange(dim_img_out[1]+1)-0.5)#,labels=[])
    ax2.set_yticklabels([])
    ax2.set_xlim(-0.5,dim_img_out[0]-0.5)
    ax2.set_ylim(-0.5,dim_img_out[1]-0.5)
    ax2.grid(color='k', linestyle='-', linewidth=lw)
    plt.show()

def display_solution(sol,**kwargs):
    title=""
    figsize=None
    for key, value in kwargs.items():
        if key=="title": title=kwargs["title"]
        elif key=="figsize": figsize=kwargs["figsize"]
        else: assert False, f"Argument \"{key}\" not recognized"

    W=sol[0][0]
    H=sol[0][1]
    n=len(sol[1:])
    sizes_circuits=[[s[0],s[1]] for s in sol[1:]]
    pos_circuits=[[s[2],s[3]] for s in sol[1:]]
    fig, ax = plt.subplots()
    cmap = plt.cm.get_cmap('Set3', n)
    #ax = plt.gca()
    plt.title(title)
    
    if len(pos_circuits) > 0:
        for i in range(n):
            rect = plt.Rectangle([pos_circuits[i][0]-1,pos_circuits[i][1]-1], *sizes_circuits[i], edgecolor="#333", facecolor=cmap(i))
            ax.add_patch(rect)
            rx, ry = rect.get_xy()
            cx = rx + rect.get_width()/2.0
            cy = ry + rect.get_height()/2.0
            ax.annotate(i+1, (cx, cy), color='black', weight='bold', ha='center', va='center')
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    
    plt.xticks([])
    plt.yticks([])
    #ax.set_xticks(range(W + 1))
    #ax.set_yticks(range(H + 1))
    #ax.set_yticklabels([])
    #ax.set_xticklabels([])

    plt.show()


def isFeasible(sol): 
    w=sol[0][0] 
    h=sol[0][1]
    rest=sol[1:]
    n=len(rest)
    for i in range(n):
        e1=rest[i]
        if e1[0]<=0 or e1[1]<=0: return False 
        #if e1[2]<0 or e1[3]<0 or e1[2]+e1[0]>w or e1[3]+e1[1]>h: return False 
        for j in range(n):
            if i!=j:
                e2=rest[j]
                # if e2[2]<=e1[2]<=e2[2]+e2[0]:
                #     if e2[3]<=e1[3]<=e2[3]+e2[1]:
                #         return False            
                if (e1[2] < e2[2]+e2[0] and e1[2]+e1[0] > e2[2] and e1[3]+e1[1] > e1[3] and e1[3] < e2[3]+e2[1] ): 
                    print(e1,e2)

                    print(f"{i} and {j} overlap")
                    return False 

    return True

def isRectangleOverlap(R1, R2):
    if (R1[0]>=R2[2]) or (R1[2]<=R2[0]) or (R1[3]<=R2[1]) or(R1[1]>=R2[3]):
        return False
    else:
        return True

def overlap(x1,y1,w1,h1,res):
    for b in res:
        x2=b[2]
        y2=b[3]
        w2=b[0]
        h2=b[1]

        if isRectangleOverlap([x1,y1,x1+w1,y1+h1],[x2,y2,x2+w2,y2+h2]): return True
    return False

def computeMostStupidSolution(instance):
    n=instance['n']
    W=instance['w']
    dim=instance['dim']
    dim=sorted(dim, key=lambda b:(b[1],b[0]) ,reverse=True)
    p=[d[0] for d in dim]
    q=[d[1] for d in dim]
    res=[]
    res.append([p[0],q[0],0,0])
    for i in range(1,n):
        appended=False
        x=0
        y=0
        while not appended:
            if overlap(x,y,p[i],q[i],res):
                if(x>=W-p[i]):
                    x=0
                    y+=1
                else:
                    x+=1
            else: 
                res.append([p[i],q[i],x,y])
                appended=True
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


def write_out(filename,to_write):
    with open(filename,"w") as f:
        f.write(to_write)
        f.close()

if __name__=="__main__":
    # for i in range(1,41):
    #     ins=loadInstance(f"instances/ins-{i}.txt")
    #     ub=computeMostStupidSolution(ins)[0][1]
    #     print(f"Ins{i}: ub={ub}")
    i=11
    ins=loadInstance(f"instances/ins-{i}.txt")
    show(computeMostStupidSolution(ins))
    # print(f"Ins{i}: ub={ub}")
