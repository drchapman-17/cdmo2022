from ctypes import util
from matplotlib import pyplot as plt
import pandas as pd
import os,inspect,sys
import json
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
sys.path.insert(0, currentdir) 
import utils

"""
METTIMI NELLA CARTELLA DEL TUO MODELLO
ASSICURATI CHE CI SIANO DENTRO I CSV
CAMBIA I NOMI DEI FILE QUI SOTTO
LANCIAMI 
"""
csv_no_rotation = currentdir+'/report_def.csv'   # CAMBIA QUI
csv_rotation = currentdir+'/report_rotation.csv'  # CAMBIA QUI

def saveFig(output,sol,title):
    W=sol[0][0]
    H=sol[0][1]
    n=len(sol[1:])
    sizes_circuits=[[s[0],s[1]] for s in sol[1:]]
    pos_circuits=[[s[2],s[3]] for s in sol[1:]]
    fig, ax = plt.subplots()
    cmap = plt.cm.get_cmap('Set3', n)
    plt.title(title)
    if len(pos_circuits) > 0:
        for i in range(n):
            rect = plt.Rectangle([pos_circuits[i][0]-1,pos_circuits[i][1]-1], *sizes_circuits[i], edgecolor="#333", facecolor=cmap(i))
            ax.add_patch(rect)
            rx, ry = rect.get_xy()
            cx = rx + rect.get_width()/2.0
            cy = ry + rect.get_height()/2.0
            ax.annotate(i+1, (cx, cy), color='black', weight='bold', ha='center', va='center')
            ratio = 1.0
    x_left, x_right = ax.get_xlim()
    y_low, y_high = ax.get_ylim()
    ax.set_aspect(abs((x_right-x_left)/(y_low-y_high))*ratio)
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    
    plt.xticks([])
    plt.yticks([])
    plt.savefig(output)
    plt.close()

df = pd.read_csv(csv_no_rotation, sep=';')
df_flip = pd.read_csv(csv_rotation, sep=';')

if not os.path.exists(currentdir+"/out") or not os.path.isdir(currentdir+"/out"):
    os.mkdir(currentdir+"/out")
if not os.path.exists(currentdir+"/out/images") or not os.path.isdir(currentdir+"/out/images"):
    os.mkdir(currentdir+"/out/images")
outfile=currentdir+"/out/ins_{}_sol.txt"
outfile_rot=currentdir+"/out/ins_{}_rot_sol.txt"
imgfile=currentdir+"/out/images/ins_{}_sol.png"
imgfile_rot=currentdir+"/out/images/ins_{}_rot_sol.png"

for index, row in df.iterrows():
    instn=row['Instance']
    sol=json.loads(row['Solution'])
    utils.writeSolution(outfile.format(instn),sol)
    saveFig(imgfile.format(instn),sol,"Plate_{}".format(instn))
for index, row in df_flip.iterrows():
    instn=row['Instance']
    sol=json.loads(row['Solution'])
    utils.writeSolution(outfile_rot.format(instn),sol)
    saveFig(imgfile_rot.format(instn),sol,"Plate_{}".format(instn))
