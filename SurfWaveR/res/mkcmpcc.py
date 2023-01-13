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

class CMPCC():

    def __init__(self, files, srfname, trfname):
        self.files = files
        self.srfname= srfname
        self.trfname = trfname
        self.srdata = dict()
        self.trdata = dict()
        self.cmpcc_dict = dict()
        self.cmpcc_tr = []
        self.sint = 0
        self.smpsize = 0
        self.unit = ""
        

    

    def mkgather(self):
        so_loc = []          # shot source location        
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
                    firtshot = f[0].stats.seg2["SOURCE_LOCATION"]
                elif file.endswith(".segy"):
                    f = obspy.read(file, unpack_trace_headers=True)   
                    segyfile = 1
                    firtshot = f[0].stats.segy.trace_header.source_coordinate_x
                    if segyunit[f.stats.binary_file_header.measurement_system] is not None:
                        self.unit = segyunit[f.stats.binary_file_header.measurement_system]                 
                else:
                    raise TypeError("Unsupported File type")

                # Sample Interval and unit
                if soi==-1:
                    if segyfile:
                        self.sint=float(f[0].stats.segy.trace_header.sample_interval_in_ms_for_this_trace) # * 10**(-6) #  why i did this i don't know?...
                    else:
                        self.sint=float(f[0].stats.seg2['SAMPLE_INTERVAL'])
                        self.unit = f[0].stats.seg2.UNITS
                
                if float(firtshot) not in so_loc:
                    soi+=1
                #print(fnum)
                n_tr = len(f)

                if segyfile:
                    so_loc.append(float(f[0].stats.segy.trace_header.source_coordinate_x))
                    recvr_locs = [abs(so_loc[soi] - float(f[i].stats.segy.trace_header.group_coordinate_x)) for i in range(len(f))]
                else:
                    so_loc.append(float(f[0].stats.seg2["SOURCE_LOCATION"]))
                    recvr_locs = [abs(so_loc[soi] - float(f[i].stats.seg2["RECEIVER_LOCATION"])) for i in range(len(f))]
        
                for s in range(1,n_tr):
                    b=0
                    while (b+s)<=n_tr-1:
                        xcorr = np.correlate(f[b+s].data, f[b].data, mode='full')
                        xcorr_len = int(xcorr.size/2)
                        xcorr = xcorr[xcorr_len:]
                        xcorr = xcorr/max(xcorr)
                        offset = (recvr_locs[b] + recvr_locs[b+s])/2
                        space = abs((recvr_locs[b] - recvr_locs[b+s]))
                        if offset in self.cmpcc_dict:
                            exist, ind = findIndex(self.cmpcc_dict[offset], space)
                            if exist:
                                #print(offset, space) #, self.cmpcc_tr[laynum[offset]])
                                self.cmpcc_tr[laynum[offset]][ind] = stack(self.cmpcc_tr[laynum[offset]][ind] + xcorr) # for k in range(xcorr.size)]
                            else:
                                #print(offset, space)
                                self.cmpcc_tr[laynum[offset]].append(xcorr.tolist())
                                self.cmpcc_dict = update(self.cmpcc_dict, offset, space)
                                #print(cmpcc_dict)
                        else:
                            self.cmpcc_tr.append([xcorr.tolist()])
                            laynum.update({offset:int(l)})
                            self.cmpcc_dict.update({offset : [space]})
                            #print(self.cmpcc_dict)
                            #print(offset, space)
                            l+=1
                        b+=1
        print(self.cmpcc_dict)
        self.srdata.update({"gather_dict": self.cmpcc_dict})
        self.trdata.update({"TraceData": self.cmpcc_tr})
        jsonobj1 = json.dumps(self.srdata, indent=1)
        jsonobj2 = json.dumps(self.trdata, indent=1)
        self.sampsize = xcorr.size

        try:

            with open(self.srfname, 'w') as f:
                f.write(jsonobj1)
                f.close()
            with open(self.trfname, 'w') as f2:
                f2.write(jsonobj2)
                f2.close()
            return (True,self.sint, self.sampsize, len(list(self.cmpcc_dict.keys())))
        except:
            print("json file made unsuccessful")
            return (False,self.sint, self.sampsize, len(list(self.cmpcc_dict.keys())))

    def saveplot(self, flder):
        
        subps = list(self.cmpcc_dict.keys())
        
        t = np.arange(0, self.sampsize*self.sint, self.sint)
        for i in range(len(subps)):
            fig, ax = plt.subplots(1,1)
            spaces = self.cmpcc_dict[subps[i]]
            for k in range(len(spaces)):
                rcvloc = np.array(self.cmpcc_tr[i][k])                
                rcvloc = rcvloc/max(rcvloc) + spaces[k]
                ax.plot(t, rcvloc, 'k')
                ax.fill_between(t,spaces[k], rcvloc, where=rcvloc>spaces[k], interpolate=True, color="black")
                ax.grid(linestyle="--", linewidth="1", color="g")
                ax.set_xlim([np.min(t), np.max(t)])

            ax.set_xlabel("Time")
            ax.set_ylabel("Spacing in "+self.unit)
            ax.set_title("cmp location "+str(subps[i])+self.unit)
            #ax.grid()
            fname = flder+"/cmpcc-"+str(subps[i])+".png"
            fig.savefig(fname)
        
        return True

    


        

