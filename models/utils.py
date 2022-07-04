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

def write_out(filename,to_write):
    with open(filename,"w") as f:
        f.write(to_write)
        f.close()

if __name__=="__main__":
    sol=[[8, 8], [3, 3, 1, 6], [3, 5, 6, 1], [5, 3, 4, 6], [5, 5, 1, 1]]

    print(isFeasible(sol))
    
