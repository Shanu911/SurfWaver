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
from src import aquGeomPlot, mkcmpcc, mkcmp


class DispersionThread(QtCore.QThread):
    thread_msg = QtCore.pyqtSignal(str) 
    setplot = QtCore.pyqtSignal(str)
    def __init__(self, dispdata, gatherDict, traceDict, sint,parent=None):
        super().__init__(parent)
        self.dispdata = dispdata
        self.dt = sint
        self.gatherDict=gatherDict
        self.traceDict = traceDict

    def run(self):
        if self.checkdataoOk():
            #dirs = ['tmp/dispersion/positional', 'tmp/dispersion/snr', 'tmp/dispersion/signal',
			#			'tmp/dispersion/dispOri', 'tmp/dispersion/disp']
                     
            dirs = ['tmp/dispersion', "tmp/inversion", 'tmp/dispersion/signal', 'tmp/dispersion/dispOri', 'tmp/dispersion/disp']
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


            for i in range(10): #len(subps)):
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
                fnames = [dir + "/src-"+ str(wavefieldtransform.array.source.x) + ".jpg" for dir in dirs[2:]]
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
                fig3, ax3 = plt.subplots(figsize=(5, 7), dpi=80)
                wavefieldtransform.array.waterfall(ax=ax3, amplitude_detrend=False, amplitude_normalization="each")
                fig3.tight_layout()
                fig3.savefig(fnames[0])
    
    #   #   # Dispersion curve figure
                fig4, ax4 = plt.subplots(figsize=(8,5), dpi=100)
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

            jobj.update({'disp_dict': disp_dict})
            jsonob = json.dumps(jobj, indent=1)
            with open("tmp/dispersion/dispdata.json", 'w') as f:
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

    def run(self):
        
        tmp = "tmp"
        if os.path.exists(tmp):
            shutil.rmtree(tmp, ignore_errors=False)
        os.mkdir(tmp)
        gatherPath = tmp+"/gatherdata"
        os.mkdir(gatherPath)
        srcJsonFile = gatherPath +"/srcdata.json"
        trcjsonfname = gatherPath+ "/trcdata.json"
        self.flder = tmp + "/gather_img"
        os.mkdir(self.flder)

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

    def __init__(self,num_of_plots_in_a_Row, gatherDict, traceDict, gtype, sampSize, Sint, parent=None):
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
        self.flder="tmp/gathers_img"
        if not os.path.exists(self.flder):
            os.mkdir(self.flder)
        self.ampfactor = 1
        self.unit = "meter"
        

    def run(self):
        
        sources = list(self.gatherDict.keys())
        t = np.arange(0, self.sampsize*self.sint, self.sint)
        j = 1
        rnum = 0
        cnum = 0
        for i, src in enumerate(sources):

            fig, ax = plt.subplots(figsize=(5,6), dpi=300)

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

    def __init__(self, num_of_plots_in_a_Row, gatherDict, traceDict, gtype, sampSize, Sint, parent=None):
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
        self.flder="tmp/ampSpec_img"
        if not os.path.exists(self.flder):
            os.mkdir(self.flder)
        self.ampfactor = 1
        self.unit = "meter"

    def run(self):
        sources = list(self.gatherDict.keys())
        j = 1
        rnum = 0
        cnum = 0
        for i, src in enumerate(sources):
            fig, ax = plt.subplots(figsize=(5,4), dpi=300)
            
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
        