import matplotlib.pyplot as plt
import os
import numpy as np
import obspy
import json
import matplotlib as mpl
mpl.rcParams.update({'figure.max_open_warning': 0})



def findIndex(value, v):
        for i in range(len(value)):
            if value[i] == v:
                return True, i

        return False, 0

def update(dict, key, value):
    arr = dict[key]
    arr.append(value)
    dict.update({key : arr})    
    return dict

def stack(original, new):
    for i in range(new.size):
        original[i] = (original[i] + new[i])/2
    return original


class CMP():

    def __init__(self, files, srfname, trfname):
        self.files = files
        self.srfname= srfname
        self.trfname = trfname
        self.srdata = dict()
        self.trdata = dict()
        self.cmp_dict = dict()
        self.cmp_tr = []
        self.sint = 0
        self.smpsize = 0
        self.unit = ""
        

    

    def mkgather(self):
        shot_locs = []          # shot source location        
        laynum = dict()        
        soi = -1
        l = 0
        segyunit = {1: "METER", 2: "FEET", 0 : "UNKNOWN"}

        for file in self.files:
            if os.path.getsize(file)<5000000:  #only active file

                # Check file type
                if file.endswith(".dat"):
                    f = obspy.read(file)
                    segyfile = 0
                    shot_loc = f[0].stats.seg2["SOURCE_LOCATION"]  #firtshot
                elif file.endswith(".segy"):
                    f = obspy.read(file, unpack_trace_headers=True)   
                    segyfile = 1
                    shot_loc = f[0].stats.segy.trace_header.source_coordinate_x         #firtshot
                    if segyunit[f.stats.binary_file_header.measurement_system] is not None:
                        self.unit = segyunit[f.stats.binary_file_header.measurement_system]                 
                else:
                    raise TypeError("Unsupported File type")

                # Sample Interval and unit
                if soi==-1:
                    if segyfile:
                        self.sint=float(f[0].stats.segy.trace_header.sample_interval_in_ms_for_this_trace) * 10**(-6)
                    else:
                        self.sint=float(f[0].stats.seg2['SAMPLE_INTERVAL'])
                        self.unit = f[0].stats.seg2.UNITS
                
                if float(shot_loc) not in shot_locs:
                    soi+=1
                #print(fnum)
                n_tr = len(f)

                if segyfile:
                    shot_locs.append(float(f[0].stats.segy.trace_header.source_coordinate_x))
                    recvr_locs = [float(f[i].stats.segy.trace_header.group_coordinate_x) for i in range(n_tr)]
                else:
                    shot_locs.append(float(f[0].stats.seg2["SOURCE_LOCATION"]))
                    recvr_locs = [float(f[i].stats.seg2["RECEIVER_LOCATION"]) for i in range(n_tr)]
                source = shot_locs[-1]
                for s in range(n_tr):

                    shot = f[s].data/max(f[s].data)   # normalizing s-th trace data
                    rcvr = recvr_locs[s]
                    if source in self.cmp_dict:
                        exist, ind = findIndex(self.cmp_dict[source], rcvr)
                        if exist:
                            #print(source, rcvr) #, self.cmp_tr[laynum[source]])
                            self.cmp_tr[laynum[source]][ind] = stack(self.cmp_tr[laynum[source]][ind], shot)
                        else:
                            self.cmp_tr[laynum[source]].append(shot.tolist())
                            self.cmp_dict = update(self.cmp_dict, source, rcvr)
                            #print(cmp_dict)
                    else:
                        self.cmp_tr.append([shot.tolist()])
                        laynum.update({source:int(l)})
                        self.cmp_dict.update({source : [rcvr]})
                        l+=1
        
        self.srdata.update({"cmp_dict": self.cmp_dict})
        self.trdata.update({"cmp_stream": self.cmp_tr})
        jsonobj1 = json.dumps(self.srdata, indent=1)
        jsonobj2 = json.dumps(self.trdata, indent=1)
        self.sampsize = shot.size

        try:

            with open(self.srfname, 'w') as f:
                f.write(jsonobj1)
                f.close()
            with open(self.trfname, 'w') as f2:
                f2.write(jsonobj2)
                f2.close()
            return (True,self.sint, self.sampsize, len(list(self.cmp_dict.keys())))
        except:
            print("json file made unsuccessful")
            return (False,self.sint, self.sampsize, len(list(self.cmp_dict.keys())))

    def saveplot(self, flder):
        
        subps = list(self.cmp_dict.keys())
        
        t = np.arange(0, self.sampsize*self.sint, self.sint)
        for i in range(len(subps)):
            fig, ax = plt.subplots(1,1)
            rcvrs = self.cmp_dict[subps[i]]
            for k in range(len(rcvrs)):
                rcvloc = np.array(self.cmp_tr[i][k])                
                rcvloc = rcvloc + rcvrs[k]
                ax.plot(t, rcvloc, 'k')

            ax.set_xlabel("Time")
            ax.set_ylabel("Reciver location "+self.unit)
            ax.set_title("Source location "+str(subps[i])+self.unit)
            #ax.grid()
            fname = flder+"/cmpcc-"+str(subps[i])+".png"
            fig.savefig(fname)
        
        return True

    


        

