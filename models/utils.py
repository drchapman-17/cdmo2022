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

def computeUpperBound(instance):
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

    n=instance['n']
    W=instance['w']
    dim=instance['dim']
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
                if(x>W-p[i]):
                    x=0
                    y+=1
                else:
                    x+=1
            else: 
                res.append([p[i],q[i],x,y])
                appended=True
    H=max([b[1]+b[3] for b in res])
    return H

def write_out(filename,to_write):
    with open(filename,"w") as f:
        f.write(to_write)
        f.close()

if __name__=="__main__":
    for i in range(1,41):
        ins=loadInstance(f"instances/ins-{i}.txt")
    # print("N={};\nWC={};\np={};\nq={};".format(ins['n'],ins['w'],[d[0] for d in ins['dim']],[d[1] for d in ins['dim']]))
        ub=computeUpperBound(ins)
    # l=[[60, 90], [34, 6, 1, 1], [13, 3, 1, 1], [13, 5, 1, 1], [10, 12, 1, 1], [10, 12, 1, 1], [6, 7, 1, 1], [6, 15, 1, 1], [25, 7, 1, 1], [25, 15, 1, 1], [21, 12, 1, 1], [16, 7, 1, 1], [16, 5, 1, 1], [21, 3, 1, 1], [21, 5, 1, 1], [5, 7, 1, 1], [5, 5, 1, 1], [4, 1, 1, 1], [4, 10, 1, 1], [6, 13, 1, 1], [12, 13, 1, 1], [12, 9, 1, 1], [23, 6, 1, 1], [7, 3, 1, 1], [7, 5, 1, 1], [2, 1, 1, 1], [2, 10, 1, 1], [6, 6, 1, 1], [6, 5, 1, 1], [14, 7, 1, 1], [14, 6, 1, 1], [16, 3, 1, 1], [16, 5, 1, 1], [14, 6, 1, 1], [14, 5, 1, 1], [14, 13, 1, 1], [3, 2, 1, 1], [3, 7, 1, 1], [11, 2, 1, 1], [11, 7, 1, 1], [6, 7, 1, 1], [6, 6, 1, 1], [33, 14, 1, 1], [12, 4, 1, 1], [12, 3, 1, 1], [16, 18, 1, 1], [12, 3, 1, 1], [12, 18, 1, 1], [4, 4, 1, 1], [4, 3, 1, 1], [3, 1, 1, 1], [3, 2, 1, 1], [6, 9, 1, 1], [6, 9, 1, 1], [6, 1, 1, 1], [6, 2, 1, 1], [5, 7, 1, 1], [5, 18, 1, 1], [3, 9, 1, 1], [3, 9, 1, 1], [9, 18, 1, 1], [6, 5, 1, 1], [6, 2, 1, 1], [2, 12, 1, 1], [2, 9, 1, 1], [8, 3, 1, 1], [8, 9, 1, 1], [10, 9, 1, 1], [3, 5, 1, 1], [3, 2, 1, 1], [3, 18, 1, 1], [3, 7, 1, 1], [2, 3, 1, 1], [2, 9, 1, 1]]
        print(f"Ins{i}: ub={ub}")
    # show(,lw=0)
