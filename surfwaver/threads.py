from scipy.fft import rfft, rfftfreq
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QPixmap
import os
import time
import swprocess
import json
from modswpro.modmasw import modMasw
import matplotlib.pyplot as plt
import numpy as np
import shutil
from res import aquGeomPlot, mkcmpcc, mkcmp
from attrdict import AttrDict
from evodcinv import EarthModel, Layer, Curve

filename = "log/settings.json"
def Prefdata():        
    try:
        file= open(filename, "r")
        data = AttrDict(json.load(file))
        return data
    except:
        print(f"Preference settings file -> {filename} not found")
        return None

class InversionThread(QtCore.QThread):
    thread_msg = QtCore.pyqtSignal(str) 
    imgnames = QtCore.pyqtSignal(list)
    sindx = QtCore.pyqtSignal(list)

    def __init__(self, method="cpso", maxrun=1, root="tmp", parent=None):
        super().__init__(parent)
        self.ROOT = root
        self.method = method.lower()
        self.maxrun = maxrun
        self.prefdata = Prefdata()
                
        
    
    def getZnVS(self):
        thickness = []
        vs = []; nu=[]
        try:
            m = open(self.ROOT + "/initmodel/model_params.json", "r")
            modeldata = json.load(m)
            m.close()
    
            thickness.append([-modeldata["z"][1][0], -modeldata["z"][0][0]])
            #for i in range(len(modeldata["z"][0])-1):


            for i in range(len(modeldata["z"][0])):
                if i!=len(modeldata["z"][0])-1:
                    low = -(modeldata["z"][1][i+1] - modeldata["z"][1][i])
                    high = -(modeldata["z"][0][i+1]-modeldata["z"][0][i])
                    if low < high:
                        thickness.append([low, high])
                    else:
                        thickness.append([high, low])
                vs.append([modeldata["vs"][0][i], modeldata["vs"][1][i]])
                low = modeldata["nu"][0][i]
                high = modeldata["nu"][1][i]
                if low < high:
                    nu.append([low, high])
                else:
                    nu.append([high, low])
            return thickness, vs, nu
        except:
            self.thread_msg.emit("model_params.json file not found")  
            time.sleep(0.005)
            raise "model_params.json file not found"
    
    def run(self):
        try:            
            f = open(self.ROOT + "/inversion/inver.json", "r")
            inverdata = json.load(f)
            f.close()

            self.slocs = list(inverdata.keys()) 
            self.vels = []
            self.pers = []
            for l in self.slocs:
                d = inverdata[l]
                if 0 not in d['frequency']:
                    per = np.round([1/x for x in d['frequency']], 7)
                    period = per[::-1]
                    vel = np.round(d['velocity'], 7)
                    velocity = vel[::-1]/1000       # evodcinv prefers things in km/s
                else:
                    per = np.round([1/x for x in d['frequency'][1:]], 7)
                    period = per[::-1]
                    vel = np.round(d['velocity'][1:], 7)
                    velocity = vel[::-1]/1000       # evodcinv prefers things in km/s
                self.vels.append(velocity)
                self.pers.append(period)
            self.thread_msg.emit("Inversion process initiated")   
                
        
            th, vs, nu = self.getZnVS()
            iframeData = self.prefdata.iframe
            dirs = [self.ROOT+"/inversion/model", self.ROOT+"/inversion/misfit", 
                    self.ROOT+"/inversion/curve", self.ROOT+"/inversion/model/vp",
                    self.ROOT+"/inversion/model/vs", self.ROOT+"/inversion/model/rh"]
            for dirc in dirs:
                if not os.path.exists(dirc): os.mkdir(dirc)

            self.thread_msg.emit("folder creation done")        
            inverRes = dict()

            for i in range(len(self.slocs)):
                tmpdict = {
                    "z":[], "vp" : [], "vs":[], "rh":[]
                }
                inverRes.update({self.slocs[i] : tmpdict})
                self.thread_msg.emit(f"src: {self.slocs[i]}")
                fnames = [self.slocs[i]]
                self.curves = []
                self.model = EarthModel()            
                for l in range(len(th)):
                    self.model.add(Layer(th[l], vs[l], nu[l]))

                self.model.configure(
                optimizer=self.method,  # Evolutionary algorithm
                misfit="rmse",  # Misfit function type
                optimizer_args={
                    "popsize": 10,  # Population size
                    "maxiter": 100,  # Number of iterations
                    "workers": -1,  # Number of cores
                    "seed": 0,
                },
                )
                time.sleep(0.005)
                self.curves.append(Curve(self.pers[i], self.vels[i], 0, "rayleigh", "phase"))
                self.res = self.model.invert(self.curves, split_results=True, maxrun=self.maxrun)
                #  p-wave velocity model
                figvp, ax = plt.subplots(figsize=(iframeData.model.w, 
                            iframeData.model.h), dpi=iframeData.model.dpi)
                fnames.append(f"{dirs[3]}/vp_{self.slocs[i]}.png")
                for res in self.res:
                    res.plot_model(parameter='vp', ax=ax)
                figvp.tight_layout()
                figvp.savefig(fnames[-1])

                #  s-wave velocity model
                figvs, ax = plt.subplots(figsize=(iframeData.model.w, 
                            iframeData.model.h), dpi=iframeData.model.dpi)
                fnames.append(f"{dirs[4]}/vs_{self.slocs[i]}.png")
                for res in self.res:
                    res.plot_model(parameter='vs', ax=ax)
                figvs.tight_layout()
                figvs.savefig(fnames[-1])

                #  density model
                figrh, ax = plt.subplots(figsize=(iframeData.model.w, 
                            iframeData.model.h), dpi=iframeData.model.dpi)
                fnames.append(f"{dirs[5]}/rho_{self.slocs[i]}.png")
                for res in self.res:
                    res.plot_model(parameter='rho', ax=ax)
                figrh.tight_layout()
                figrh.savefig(fnames[-1])

                # misfits
                figmfit, ax = plt.subplots(figsize=(iframeData.misfit.w, 
                                iframeData.misfit.h), dpi=iframeData.misfit.dpi)
                fnames.append(f"{dirs[1]}/misfit_{self.slocs[i]}.png")
                for res in self.res:
                    res.plot_misfit(ax=ax)
                figmfit.tight_layout()
                figmfit.savefig(fnames[-1])

                # curve
                figcurve, ax = plt.subplots(figsize=(iframeData.dispCurve.w, 
                                iframeData.dispCurve.h), dpi=iframeData.dispCurve.dpi)
                fnames.append(f"{dirs[2]}/curve_{self.slocs[i]}.png")
                ax.set_xscale("log")
                ax.plot(1/self.pers[i], self.vels[i], 'k')
                for res in self.res:
                    res.plot_curve(self.pers[i], 0, "rayleigh", "phase", 
                            ax=ax, plot_args={"xaxis": "frequency","type": "semilogx"})
                figcurve.tight_layout()
                figcurve.savefig(fnames[-1])


                print(fnames)

                for res in self.res:
                    for j in range(len(th)):
                        inverRes[self.slocs[i]]["z"].append(round(res.model[j][0], 5))
                        inverRes[self.slocs[i]]["vp"].append(round(res.model[j][1], 5))
                        inverRes[self.slocs[i]]["vs"].append(round(res.model[j][2], 5))
                        inverRes[self.slocs[i]]["rh"].append(round(res.model[j][3], 5))

                self.imgnames.emit(fnames)            

                time.sleep(0.01)

            jobj = json.dumps(inverRes)
            inverResfile = self.ROOT+"/inversion/inverRes.json"
            with open(inverResfile, "w") as f:
                f.write(jobj)
                f.close()
            self.sindx.emit(self.slocs)
            self.thread_msg.emit("Done")
        except:
            self.thread_msg.emit("inver.json file not found")
            time.sleep(0.005)               

            
            
class Inversion2dThread(QtCore.QThread):
    thread_msg = QtCore.pyqtSignal(str) 
    setplot = QtCore.pyqtSignal(list)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.prfdata = Prefdata()
        self.ROOT = self.prfdata.gframe.rootdir
        try:
            with open(self.ROOT+"/inversion/inverRes.json", "r") as f:
                self.jobj = json.load(f)
                f.close()
            if not os.path.exists(self.ROOT+"/Result"):
                os.mkdir(self.ROOT+"/Result")
        except:
            self.thread_msg.emit("*** inverRes.json file not found ****")

    def run(self):       
        self.thread_msg.emit("Process initiated")
        fnames= []
        fldr = self.ROOT+"/Result"

        cmps = np.array(list(map(float, self.jobj.keys())))
        cmps = np.short(cmps)
        cmp_model, z_model, vp_model, vs_model, rh_model = np.array([]), np.array([]), np.array([]), np.array([]), np.array([])
        levels = 100
        xlabel = "Common mid-points (Meter)"
        ylabel = "Depth (Km)"
        #print( jobj)
        for cmp in cmps:
            data = self.jobj[f"{float(cmp)}"]  # data -> dict() , contained keys -> z, vp, vs, rh
            z = data["z"]
            vp = data["vp"]
            vs = data["vs"]
            rh = data["rh"]
            z_model = np.hstack((z_model, z))
            vp_model = np.hstack((vp_model, vp))
            vs_model = np.hstack((vs_model, vs))
            rh_model = np.hstack((rh_model, rh))
            cmp_model =  np.hstack((cmp_model, np.ones(len(z))*cmp))

        # density model
        figdensity, ax = plt.subplots(figsize=(self.prfdata.rframe.w, self.prfdata.rframe.h),
                                               dpi=self.prfdata.rframe.dpi) 
        cc = ax.tricontourf(cmp_model, z_model, rh_model, levels=levels, cmap="jet")
        ax.invert_yaxis()
        ax.xaxis.tick_top()
        ax.set_title("density model")
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        cbar = plt.colorbar(cc, ax=ax)
        cbar.set_label(r"Density,$\rho (g/cm^3)$")
        fnames.append(fldr+"/density_2dmodel.png")
        figdensity.tight_layout()
        figdensity.savefig(fnames[-1])

        # vp model
        figvp, ax = plt.subplots(figsize=(self.prfdata.rframe.w, self.prfdata.rframe.h),
                                               dpi=self.prfdata.rframe.dpi) 
        cc2 = ax.tricontourf(cmp_model, z_model, vp_model, levels=levels, cmap="jet")
        ax.invert_yaxis()
        ax.xaxis.tick_top()
        ax.set_title("Vp model")
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        cbar1 = plt.colorbar(cc2, ax=ax)
        cbar1.set_label(r"P-wave velocity (km/s)")
        fnames.append(fldr+"/vp_2dmodel.png")
        figvp.tight_layout()
        figvp.savefig(fnames[-1])


        # vs model
        figvs, ax = plt.subplots(figsize=(self.prfdata.rframe.w, self.prfdata.rframe.h),
                                               dpi=self.prfdata.rframe.dpi) 
        cc1 = ax.tricontourf(cmp_model, z_model, vs_model, levels=levels, cmap="jet")
        ax.invert_yaxis()
        ax.xaxis.tick_top()
        ax.set_title("Vs model")
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        cbar2 = plt.colorbar(cc1, ax=ax)
        cbar2.set_label(r"S-wave velocity (km/s)")

        fnames.append(fldr+"/vs_2dmodel.png")
        figvs.tight_layout()
        figvs.savefig(fnames[-1])

        self.setplot.emit(fnames)
        time.sleep(0.005)
        self.thread_msg.emit("Done")



class DispersionThread(QtCore.QThread):
    thread_msg = QtCore.pyqtSignal(str) 
    setplot = QtCore.pyqtSignal(str)
    sindx = QtCore.pyqtSignal(list)
    def __init__(self, dispdata, gatherDict, traceDict, sint,parent=None):
        super().__init__(parent)
        self.dispdata = dispdata
        self.dt = sint
        self.gatherDict=gatherDict
        self.traceDict = traceDict
        self.prfdata = Prefdata()
        self.ROOT = self.prfdata.gframe.rootdir

    def run(self):
        if self.checkdataoOk():
            #dirs = [ROOT+'/dispersion/positional', ROOT+'/dispersion/snr', ROOT+'/dispersion/signal',
			#			ROOT+'/dispersion/dispOri', ROOT+'/dispersion/disp']
                     
            dirs = [self.ROOT+'/dispersion', self.ROOT+"/inversion", self.ROOT+'/dispersion/signal', self.ROOT+'/dispersion/dispOri', self.ROOT+'/dispersion/disp']
            for dir in dirs:
                if not os.path.exists(dir):os.mkdir(dir) 
            
            invf = dirs[1]+"/inver.json"
            if os.path.isfile(invf):os.remove(invf)
            time.sleep(0.005)
            self.thread_msg.emit("Temporal Folder ready")


            settings = swprocess.Masw.create_settings_dict(workflow="time-domain",
        	        trim=self.dispdata["trimstat"], trim_begin=self.dispdata["trim_begin"], trim_end=self.dispdata["trim_end"],
        	        mute=False, method="interactive", window_kwargs={},
        	        transform="fk", fmin=self.dispdata["fmin"], fmax=self.dispdata["fmax"], pad=True, df=0.5,
        	        vmin=self.dispdata["vmin"], vmax=self.dispdata["vmax"], nvel=self.dispdata["nvel"], vspace=self.dispdata["vspace"],
        	        snr=True, noise_begin=self.dispdata["noise_begin"], noise_end=self.dispdata["noise_end"],
        	        signal_begin=self.dispdata["signal_begin"], signal_end=self.dispdata["signal_end"],
        	        pad_snr = True, df_snr=1)
            
            wavefieldtransforms = []
            subps = list(self.gatherDict.keys())
            sourceloc = []
            # Image normalization {"none", "absolute-maximum" "frequency-maximum"} -> "frequency-maximum" is recommended.
            wavefield_normalization = "frequency-maximum"
            # Display the wavelength resolution limit.
            display_lambda_res = True
            # Display Yoon and Rix (2009) near-field criteria
            display_nearfield = False
            number_of_array_center_distances = 1
            disp_dict = {}
            jobj = {}
            append = False

            time.sleep(0.005)
            self.thread_msg.emit("Setting parameters ready")


            for i in range(len(subps)):
                if len(self.gatherDict[subps[i]]) > 1:
                    wavefieldtransforms.append(modMasw.run(cmpcc_strm=self.traceDict[i], sloc=subps[i], rloc= self.gatherDict[subps[i]], dt=self.dt, settings=settings))
                    sourceloc.append(subps[i])


            time.sleep(0.005)
            self.thread_msg.emit("Graph Plotting initiated...")

            for i,wavefieldtransform in enumerate(wavefieldtransforms):
                """
                fig1 = positional figure
                fig2 = snr figure
                fig3 = signal figure
                fig4 = disperesion figure original
                fig5 = dispersion figure with picks
                """
                #print(str(wavefieldtransform.array.source.x))
                fnames = [dir + "/src-"+ str(wavefieldtransform.array.source.x) + ".png" for dir in dirs[2:]]
    #   #   # positional figure
                #fig1,ax1 = plt.subplots(figsize=(5,1), dpi=300)
                #wavefieldtransform.array.plot(ax=ax1)
                #ax1.set_yticks([])
                #ax1.legend(ncol=2)
                #fig1.savefig(fnames[0])
                
    #   #   # snr figure
                #fig2, ax2 = plt.subplots(figsize=(5, 2), dpi=80)
                #wavefieldtransform.plot_snr(ax=ax2)
                #ax2.set_xticklabels([])
                #ax2.set_xlabel("")
                #ax2.set_ylabel("SNR")
                #fig2.savefig(fnames[1])
    
    #   #   # signal figure
                fig3, ax3 = plt.subplots(figsize=(self.prfdata.dframe.gather.w, self.prfdata.dframe.gather.h), dpi=self.prfdata.dframe.gather.dpi)
                wavefieldtransform.array.waterfall(ax=ax3, amplitude_detrend=False, amplitude_normalization="each")
                fig3.tight_layout()
                fig3.savefig(fnames[0])
    
    #   #   # Dispersion curve figure
                fig4, ax4 = plt.subplots(figsize=(self.prfdata.dframe.dispCurve.w,self.prfdata.dframe.dispCurve.h), dpi=self.prfdata.dframe.dispCurve.dpi)
                nearfield = number_of_array_center_distances if display_nearfield else None
                ax4.set_xscale("log")
                wavefieldtransform.plot(fig=fig4, ax=ax4, normalization=wavefield_normalization, nearfield=nearfield, fname=fnames[1])
                xlim = ax4.get_xlim()
                ylim = ax4.get_ylim()
		
                if display_lambda_res:
                    kres_format = dict(linewidth=1.5, color="#000", linestyle="--")
                    kres = wavefieldtransform.array.kres
                    kvelocity = 2*np.pi*wavefieldtransform.frequencies / kres
                    ax4.plot(wavefieldtransform.frequencies, kvelocity, label=r"$\lambda_{a,min}$" + f"={np.round(2*np.pi/kres,2)} m", **kres_format)
                    ax4.legend(loc="upper right")
                ax4.set_xlim(xlim)
                ax4.set_ylim(ylim)	

                fig4.tight_layout()
                fig4.savefig(fnames[2])

                peak = swprocess.peaks.Peaks(wavefieldtransform.frequencies,
                                 wavefieldtransform.find_peak_power(by="frequency-maximum"),
                                 identifier=f"{wavefieldtransform.array.source.x}")
                peak.to_json(fname=invf, append=append)
                append = True		
                disp_dict.update({str(wavefieldtransform.array.source.x): fnames})
                
                
                self.setplot.emit(f'{wavefieldtransform.array.source.x}')
                self.thread_msg.emit(f'src: {wavefieldtransform.array.source.x} done')
                time.sleep(0.005)

            self.sindx.emit(sourceloc)
            jobj.update({'disp_dict': disp_dict})
            jsonob = json.dumps(jobj, indent=1)
            with open(self.ROOT+"/dispersion/dispdata.json", 'w') as f:
                f.write(jsonob)
                f.close()
            
            time.sleep(0.005)
                

            self.thread_msg.emit('complete')


        else:
            self.thread_msg.emit("Data Error!!")

    def checkdataoOk(self):
        if (self.dispdata["fmin"] < self.dispdata["fmax"]) and (self.dispdata["signal_begin"]< self.dispdata["signal_end"]) and (self.dispdata["noise_begin"] < self.dispdata["noise_end"]) and (self.dispdata["vmin"]<self.dispdata["vmax"]) and self.dispdata["nvel"]> 0:
            if not self.dispdata["trimstat"]:
                return True			#### need to check sstrt, nstrt >= signal to send, nend<= signal
            else:
                if self.dispdata["trim_begin"] < self.dispdata["trim_end"]:
                    return True
        return False



class ApplyThread(QtCore.QThread):
    thread_msg = QtCore.pyqtSignal(str) 
    file_info = QtCore.pyqtSignal(dict) 

    def __init__(self, filePaths, gType, parent=None):
        super().__init__(parent)
        self.filePaths = filePaths
        self.gType = gType
        prfdata = Prefdata()
        self.ROOT = prfdata.gframe.rootdir

    def run(self):
        
        tmp = self.ROOT
        if os.path.exists(tmp):
            shutil.rmtree(tmp, ignore_errors=False)
        os.mkdir(tmp)
        gatherPath = tmp+"/gatherdata"
        os.mkdir(gatherPath)
        srcJsonFile = gatherPath +"/srcdata.json"
        trcjsonfname = gatherPath+ "/trcdata.json"
        self.flder = tmp + "/gather_img"
        os.mkdir(self.flder)
        for flder in ["/inversion", "/dispersion", "/initmodel", "/inversion/model",
                      "/inversion/misfit", "/inversion/curve", "/inversion/model/vp",
                       "/inversion/model/vs", "/inversion/model/density",
                       "/dispersion/disp", "/dispersion/dispOri", "/dispersion/signal"]:
            os.mkdir(tmp+flder)

        time.sleep(0.005)
        self.thread_msg.emit("Temporal Folder made successfull")

        msg = aquGeomPlot.original(self.filePaths, gatherPath)
        time.sleep(0.005)
        self.thread_msg.emit(msg)

        if self.gType == 0:
            gather = mkcmpcc.CMPCC(self.filePaths, srcJsonFile, trcjsonfname)
        elif self.gType == 1:
            self.cmpccAquGeom_Canv.setEnable(False)
            gather = mkcmp.CMP(self.filePaths, srcJsonFile, trcjsonfname)
        
        flg4, sint, ns, ntr = gather.mkgather()
        """
        sint = sampling interval
        ns = number of samples in each trace
        ntr = number of traces in cmpcc gather
        """
        time.sleep(0.005)        
        self.thread_msg.emit("Apply successful")
        self.file_info.emit({"flg4": flg4,"sint": sint,"ns": ns,"ntr": ntr })



class GatherImgThread(QtCore.QThread):
    thread_msg = QtCore.pyqtSignal(str)
    fnameEmit = QtCore.pyqtSignal(str, int, int, int) 

    def __init__(self,num_of_plots_in_a_Row, gatherDict, traceDict, gtype, sampSize, Sint, root="tmp", parent=None):
        """
        canvas : gatherGraphicsView
        gatherDict: gather dictionary
        traceDict : trace dictionary
        gtype: gather type
        samSize : number of samples
        Sint : sampling interval
        """
        super().__init__(parent)
        self.num_of_plots_in_a_Row  = num_of_plots_in_a_Row
        self.gatherDict = gatherDict
        self.traceDict = traceDict
        self.gtype = gtype
        self.sampsize= sampSize
        self.sint=Sint
        self.ROOT = root
        self.flder=self.ROOT+"/gathers_img"
        if not os.path.exists(self.flder):
            os.mkdir(self.flder)
        self.ampfactor = 1
        self.unit = "meter"        
        self.prfdata = Prefdata()
        

    def run(self):
        
        sources = list(self.gatherDict.keys())
        t = np.arange(0, self.sampsize*self.sint, self.sint)
        j = 1
        rnum = 0
        cnum = 0
        for i, src in enumerate(sources):

            fig, ax = plt.subplots(figsize=(self.prfdata.gframe.gather.w,self.prfdata.gframe.gather.h), dpi=self.prfdata.gframe.gather.dpi)

            rcvrs = self.gatherDict[src]
            for k in range(len(rcvrs)):
                traceData = np.array(self.traceDict[i][k])
                traceData = (self.ampfactor  * traceData / max(traceData)) + rcvrs[k]

                ax.plot(traceData,t, 'k', linewidth="0.5")
                ax.fill_betweenx(t, rcvrs[k], x2=traceData, where=traceData>rcvrs[k], interpolate=True, color="black")
                ax.grid(linestyle="--", linewidth="0.3", color="g")
                ax.set_ylim([np.min(t), np.max(t)])

            ax.invert_yaxis()
            ax.xaxis.tick_top()
            if self.gtype==0:
                labels = ["Reciver location", "Source location at ", "/cmp-"]
            else:
                labels = ["Spacing", "CMP location at ", "/cmpcc-"]
            ax.set_ylabel("Time (s)")
            ax.set_xlabel(labels[0])
            ax.set_title(labels[1]+str(src)+" "+self.unit)
            fname = self.flder+labels[2]+str(src)+".jpg"
            fig.tight_layout()
            fig.savefig(fname)

            self.fnameEmit.emit(fname, i, rnum , cnum)
            if j < self.num_of_plots_in_a_Row:
                j+=1; cnum += 1
            else:
                j = 1; cnum=0; rnum += 1
            self.thread_msg.emit(f"src = {src}")
            time.sleep(0.005)
            

        self.thread_msg.emit("done")
            
        


    #def makeGraphicsScene(self):
    #    """
    #    make graphics scene and multiple pixmaps within gather_scrlArea
    #    """
    #    scene = QtWidgets.QGraphicsScene(self)
    #    
    #    #for i, src in enumerate(sources):
    #    #    self.mekeplots(src, i)
#
    #    pass

    def makePlot(self, src, i):
        """
        generate gather plots 
        """
        t = np.arange(0, self.sampsize*self.sint, self.sint)
        
        #return fname

    
    #def setPlots(self, scene):
    #    """
    #    set generated plots in the pixmaps made by makeGraphicsScene function
    #    """
    #    self.canvas.setScene(scene)
    #    self.canvas.fitInView(scene.sceneRect(), QtCore.Qt.KeepAspectRatio)
    #    pass 

    #def AmpUp(self):
    #    """
    #    Amplitude up
    #    """
    #    pass
#
    #def AmpDown(self):
    #    """
    #    Amplitude down
    #    """
#
    #def Zoomin(self):
    #    """
    #    scaled up width of the pixmaps and rearrenge pixmap location
    #    """
    #    pass
#
    #def zoomout(self):
    #    """
    #    scaled down width of the pixmaps and rearrenge pixmap location
    #    """
    #    pass

class fftImgThread(QtCore.QThread):
    thread_msg = QtCore.pyqtSignal(str)
    fnameEmit = QtCore.pyqtSignal(str, int, int, int) 

    def __init__(self, num_of_plots_in_a_Row, gatherDict, traceDict, gtype, sampSize, Sint, root="tmp", parent=None):
        """
        canvas : gatherGraphicsView
        gatherDict: gather dictionary
        traceDict : trace dictionary
        gtype: gather type
        samSize : number of samples
        Sint : sampling interval
        """
        super().__init__(parent)
        self.num_of_plots_in_a_Row  = num_of_plots_in_a_Row
        self.gatherDict = gatherDict
        self.traceDict = traceDict
        self.gtype = gtype
        self.sampsize = sampSize
        self.sint=Sint
        self.ROOT = root
        self.flder=self.ROOT+"/ampSpec_img"
        if not os.path.exists(self.flder):
            os.mkdir(self.flder)
        self.ampfactor = 1
        self.unit = "meter"        
        self.prfdata = Prefdata()

    def run(self):
        sources = list(self.gatherDict.keys())
        j = 1
        rnum = 0
        cnum = 0
        for i, src in enumerate(sources):
            fig, ax = plt.subplots(figsize=(self.prfdata.gframe.AmpSpec.w, self.prfdata.gframe.AmpSpec.h), dpi= self.prfdata.gframe.AmpSpec.dpi)
            
            rcvrs = self.gatherDict[src]
            for k in range(len(rcvrs)):
                traceData = np.array(self.traceDict[i][k])     
                ffttraceData = rfft(traceData)
                ffttraceDataMeg = abs(ffttraceData)[:200]

                freqx = rfftfreq(traceData.size, self.sint)[:200]          
                ffttraceDataMeg = (self.ampfactor  * ffttraceDataMeg / max(ffttraceDataMeg)) + rcvrs[k]
                ax.fill_between(freqx, rcvrs[k], y2=ffttraceDataMeg, where=ffttraceDataMeg>rcvrs[k], interpolate=True, color="black")
                ax.grid(linestyle="--", linewidth="0.3", color="g")
                ax.set_xlim([np.min(freqx), np.max(freqx)])

            if self.gtype==0:
                labels = ["Reciver location", "Source location at ", "/cmp-"]
            else:
                labels = ["Spacing", "CMP location at ", "/cmpcc-"]
            ax.set_xlabel("Frequency (Hz)")
            ax.set_ylabel(labels[0])
            ax.set_title(labels[1]+str(src)+" "+self.unit)
            fname = self.flder+labels[2]+str(src)+".jpg"
            fig.tight_layout()
            fig.savefig(fname)

            self.fnameEmit.emit(fname, i, rnum , cnum)
            if j < self.num_of_plots_in_a_Row:
                j+=1; cnum += 1
            else:
                j = 1; cnum=0; rnum += 1
            self.thread_msg.emit(f"src = {src}")
            time.sleep(0.005)

        self.thread_msg.emit("Done")
        

class ModelPlots(QtCore.QThread):
    thread_msg = QtCore.pyqtSignal(str)
    setter = QtCore.pyqtSignal(int, str)
    #zstep=QtCore.pyqtSignal(object, np.ndarray)
    #step=QtCore.pyqtSignal(object, np.ndarray)

    def __init__(self, inflist, suplist, path, parent=None):
        
        super().__init__(parent)
        self.inflist = inflist
        self.suplist = suplist
        self.path = path
        self.prfdata = Prefdata().dframe.gather

    def step(self, array):
        data=np.array([])
        for d in array:
            data = np.hstack((data, (d,d)))
        return data
    
    def zstep(self, array):
        depthdata=np.array([0])
        for d in array[:-1]:
            depthdata = np.hstack((depthdata, (d,d)))
        depthdata = np.hstack((depthdata, array[-1]))
        return depthdata
    
    def run(self):
        depthsup =  self.zstep(self.suplist[0]) 
        depthinf =  self.zstep(self.inflist[0])
        depthmean = (depthsup + depthinf)/2

        listitem = ["z", "Vp", "Vs", "Density", "PR"]
        units = ["km", "km/s", "km/s", "kg/m3", ""]

        for i in range(1, len(self.inflist)):
            filename= f"{self.path}/{listitem[i]}_model.svg"
            fig, ax = plt.subplots(figsize=(4.8, 6.5), dpi=self.prfdata.dpi)            
            
            ax.plot(self.step(self.inflist[i]), depthinf, "k--o")
            ax.plot(self.step(self.suplist[i]), depthsup, "k--o") 
            mean = [(self.inflist[i][x] + self.suplist[i][x])/2 for x in range(len(self.suplist[i]))] 
            ax.plot(np.around(self.step(mean),3), depthmean, "r--o")
            
            ax.set_ylabel("Depth (km)")
            ax.set_xlabel(f"{listitem[i]} {units[i]}")
            #ax.set_ylim([0, depthmean[-1]])

            ax.grid(True)
            #ax.invert_yaxis()

            fig.tight_layout()
            fig.savefig(filename, format='svg')

            self.setter.emit(i, filename)
            self.thread_msg.emit(f"{listitem[i]} done")
            time.sleep(0.005)