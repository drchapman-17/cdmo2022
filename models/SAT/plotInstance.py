from matplotlib import pyplot as plt
import os,inspect,sys
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
sys.path.insert(0, currentdir) 
import utils

for instn in range(1, 2):
    instance=utils.loadInstance(currentdir+f"/../instances/ins-{instn}.txt") # CAMBIA IL PATH COME VUOI TU
    print(instance)
    
    W=instance['w']
    w=[d[0] for d in instance['dim']]
    h=[d[1] for d in instance['dim']]
    n=instance['n']
    fig, ax = plt.subplots()
    cmap = plt.cm.get_cmap('Set3', n)
    x=0
    y=0
    max_x=3.5*max(w) # SCEGLI TU LA LARGHEZZA MASSIMA SE VUOI
    bi,bf=0,0
    first_row=True
    y_max=0
    if n> 0:
        for i in range(n):
            if x+w[i]<max_x:
                rect = plt.Rectangle([x,y],w[i],h[i], edgecolor="#333", facecolor=cmap(i))
                x+=w[i]+0.2
                bf+=1
            else:
                first_row=False
                x=0
                y-=max(h[bi:])+1
                rect = plt.Rectangle([x,y],w[i],h[i], edgecolor="#333", facecolor=cmap(i))
                bi=bf
                x+=w[i]+0.2
            if first_row:
                    y_max=max(h[:bf])
            ax.add_patch(rect)
    print(y_max)
    ax.set_xlim(0, max_x-1)
    ax.set_ylim(y,y_max)
    x_left, x_right = ax.get_xlim()
    y_low, y_high = ax.get_ylim()
    ax.set_aspect(1)


    plt.xticks([])
    plt.yticks([])

    plt.show()
    #plt.savefig(f"./report/out-{instn}")

# PER SALVARE LA FIG
# COMMENTA plt.show()
# DECOMMENTA QUESTE LINEE
# SE VUOI CACCIA TUTTO IN UN FOR E VIA
# out=f"instance_{instn}.png"
# plt.savefig(out)
# plt.close()

