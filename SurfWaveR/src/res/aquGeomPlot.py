import matplotlib.pyplot as plt
import obspy
import os
import json
import numpy as np
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)

def original(filespath, jsonpath):
    srclocs = []
    rcvrlocs = []
    originalLocData = dict()
    jsonfileName = jsonpath+"/originalLocData.json"
    for fpath in filespath:
        isSeg2 = fpath.endswith(".dat")
        stream = obspy.read(fpath)
        locs = FindLocs(stream, isSeg2)
        srclocs.append(locs[0])
        rcvrlocs.append(locs[1])
    originalLocData.update({"src_locs": srclocs})
    originalLocData.update({"rcvr_locs": rcvrlocs})
    jsonobj = json.dumps(originalLocData, indent=1)
    try:
        with open( jsonfileName, "w") as f:
            f.write(jsonobj)
            f.close()
    except:
        msg = "aquGeomPlot.py Error : Original location json file made unsuccessful"
        return msg
    return "Location read successful"

def FindLocs(strm, isSeg2):
    if isSeg2:
        srcloc = float(strm[0].stats.seg2["SOURCE_LOCATION"])
        rcvrloc = []
        for trace in strm:
            rcvrloc.append(float(trace.stats.seg2["RECEIVER_LOCATION"]))
        return srcloc, rcvrloc
    else:
        srcloc = float(strm[0].stats.segy.trace_header.source_coordinate_x)
        rcvrloc = []
        for trace in strm:
            rcvrloc.append(float(trace.stats.segy.trace_header.group_coordinate_x))
        return srcloc, rcvrloc

def plot(file):

    f = open(file, "r")
    data = json.load(f)
    src = data["src_locs"]
    rcvr = data["rcvr_locs"]    

    fig, ax = plt.subplots(figsize=(10,5), dpi=300)

    for i, sensor in enumerate(rcvr):
        ax1 = ax.plot(src[i], (i+1), 'r*', ms=15, markeredgewidth=0.5, markeredgecolor="k")    
        ycorr = [i+1]*len(sensor)
        ax2 = ax.plot(sensor, ycorr, 'bv', ms=12, markeredgewidth=0.5, markeredgecolor="k")

    ax.set_xlabel("Survey line")
    ax.set_ylabel("Data Aquisition")
    ax.set_title("Data Aquisition Geometry", pad=6, fontsize = 12, fontweight="bold")
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')
    ax.xaxis.set_label_coords(0.05, 1.08)
    ax.invert_yaxis()
    #ax.spines['right'].set_visible(False)
    #ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    #ax.xaxis.set_minor_locator(MultipleLocator(5))
    #ax.yaxis.set_minor_locator(MultipleLocator(.5))
    #ax.grid(True, which="both", linewidth=0.8) # color='#999', linestyle='--', 
            
    ax.legend((ax1[0], ax2[0]), ("Source", "Receiver"), loc='upper center', bbox_to_anchor=(0.5, -0.05),
          fancybox=False, shadow=False, ncol=2, frameon=False)

    fig.savefig("tmp/gather_img/oriaqugraph.jpg", dpi=300, bbox_inches='tight', pad_inches=0.2)
    f.close()
    
    return


def plotCMPCCgeom(offset, spacings):   

    fig, ax = plt.subplots(figsize=(10,5), dpi=300)

    for i, sensor in enumerate(spacings):
        ycorr = [offset[i]]*len(sensor)
        ax.plot(sensor, ycorr, 'X')

    ax.set_yticks(offset[::5])
    ax.set_xlabel("Spacings")
    ax.set_ylabel("Common mid-points")
    ax.set_title("CMPCC Geometry", pad=6, fontsize = 12, fontweight="bold")
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')
    ax.xaxis.set_label_coords(0.05, 1.08)
    ax.invert_yaxis()
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    #ax.xaxis.set_minor_locator(MultipleLocator(5))
    #ax.yaxis.set_minor_locator(MultipleLocator(.5))
    #ax.grid(True, which="both", linewidth=0.8) # color='#999', linestyle='--', 
            
    #ax.legend((ax1[0]), ("Cross corelated trace"), loc='upper center', bbox_to_anchor=(0.5, -0.05),
    #      fancybox=False, shadow=False, ncol=1, frameon=False)
    fig.savefig("tmp/gather_img/cmpccGeomgraph.jpg", dpi=300, bbox_inches='tight', pad_inches=0.2)
    plt.ioff()
    plt.clf()
    plt.close(fig)
 

