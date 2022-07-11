import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
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
        img_out[i[2]-1:i[2]-1+i[0],i[3]-1:i[3]-1+i[1]]=c        

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
            # cx = rx + rect.get_width()/2.0
            # cy = ry + rect.get_height()/2.0
            # ax.annotate(i+1, (cx, cy), color='black', weight='bold', ha='center', va='center')
            ratio = 1.0
    x_left, x_right = ax.get_xlim()
    y_low, y_high = ax.get_ylim()
    ax.set_aspect(abs((x_right-x_left)/(y_low-y_high))*ratio)
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    
    plt.xticks([])
    plt.yticks([])
    #ax.set_xticks(range(W + 1))
    #ax.set_yticks(range(H + 1))
    #ax.set_yticklabels([])
    #ax.set_xticklabels([])
    
    plt.savefig("plot.png", edgecolor='w', facecolor = 'w')
    #plt.show()


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

def computeMostStupidSolution(instance,rotationsAllowed=False):
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

def report_barplot(model, save_image = True):
    # model must be a string between: CP, SAT, SMT, MIP
    # the csv must be have as columns: Instance, Time, Solution
    # The instances that can't be resolved in time must have in 'Time' None
    # The name of the csv must be i.e. report_CP.csv, report_rotation_CP.csv

    csv_no_rotation = 'report_'+model+'.csv'
    csv_rotation = 'report_rotation_'+model+'.csv'
    name_image = 'report_'+model+'.png'

    df = pd.read_csv(csv_no_rotation, sep=';')
    df_flip = pd.read_csv(csv_rotation, sep=';')

    df['mode'] = 'no rotation'
    df_flip['mode'] = 'rotation'
    df = pd.concat([df, df_flip])

    T = df.loc[~df.isna().any(axis = 1), 'Time'].astype(float).max()

    df.loc[df.isna().any(axis = 1), 'mode']='failure'
    df.loc[df.isna().any(axis = 1), 'Time']=T
    df['Time'] = df['Time'].astype(float)

    colors = ['g', 'b', 'r']
    sns.set_palette(sns.color_palette(colors))
    plt.figure(figsize = (15,10))
    sns.barplot(data = df, x = 'Instance', y = 'Time', hue = 'mode', orient = 'v', hue_order=['no rotation', 'rotation', 'failure'])

    plt.xticks(fontsize = 'large')
    plt.yticks(fontsize = 'large')
    plt.xlabel('N instance', size = 15)
    plt.ylabel('Execution time', size = 15)
    plt.title(model+' execution time', size = 20)
    plt.legend(loc = 'upper left', fontsize='x-large')

    if save_image:
        plt.savefig(name_image, edgecolor='w', facecolor = 'w')

    plt.show()

def report_barplot_v2(model, save_image = True):
    # model must be a string between: CP, SAT, SMT, MIP
    # the csv must be have as columns: Instance, Time, Solution
    # The instances that can't be resolved in time must have in 'Time' None
    # The name of the csv must be i.e. report_CP.csv, report_rotation_CP.csv

    csv_no_rotation = 'report_'+model+'.csv'
    csv_rotation = 'report_rotation_'+model+'.csv'
    name_image = 'report_'+model+'.png'

    df = pd.read_csv(csv_no_rotation, sep=';')
    df_flip = pd.read_csv(csv_rotation, sep=';')

    df['mode'] = 'No rotation'
    df_flip['mode'] = 'Rotation'

    df.loc[df['Time'] > 300, 'mode']= 'Timeout no rotation'
    df_flip.loc[df_flip['Time'] > 300, 'mode']= 'Timeout rotation'

    df = pd.concat([df, df_flip])

    sns.set_palette(sns.color_palette("tab10"))
    plt.figure(figsize = (15,10))
    sns.barplot(data = df, x = 'Instance', y = 'Time', hue = 'mode', hue_order=['No rotation', 'Timeout no rotation'\
                                                                                ,'Rotation', 'Timeout rotation'])

    plt.xticks(fontsize = 'large')
    plt.yticks(fontsize = 'large')
    plt.xlabel('Instance', size = 15)
    plt.ylabel('Execution time', size = 15)
    plt.title('SAT execution time', size = 20)
    plt.legend(loc = 'upper left', fontsize='x-large')

    threshold = 300
    plt.axhline(threshold, color='red', ls='dotted')

    if save_image:
        plt.savefig(name_image, edgecolor='w', facecolor = 'w')

    plt.show()

if __name__=="__main__":
    # for i in range(1,41):
    #     ins=loadInstance(f"instances/ins-{i}.txt")
    #     ub=computeMostStupidSolution(ins)[0][1]
    #     print(f"Ins{i}: ub={ub}")
    i=41
    ins=loadInstance(f"instances/ins-{i}.txt")
    print(ins)
    sol=computeMostStupidSolution(ins,rotationsAllowed=True)
    if sol:
        show(sol)
        print("H:",sol[0][1])
    else:
        print("Unfeasible!")
