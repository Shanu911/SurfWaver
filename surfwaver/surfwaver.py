from maswGui import Ui_MainWindow
import sys
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QApplication 
from PyQt5 import QtCore, QtWidgets, QtGui
import os
from res import aquGeomPlot
import threads
import shutil
from PyQt5.QtGui import QPixmap
import json
import numpy as np
import matplotlib.pyplot as plt 


def binning(binsize, file):
    f = open(file, "r")
    cmpcc_dict = json.load(f)["gather_dict"]
    offset = np.array(list(cmpcc_dict.keys()))
    spacings = []
    f.close()
    toff = offset.size
    for i in range(toff):
        spacings.append(cmpcc_dict[offset[i]])
    offset = np.array([float(x) for x in offset])
    if binsize==1:
        return offset, spacings
    else:
        modoff = []
        modspace = []
        i=0
        offset = np.sort(offset, kind="mergesort")
        while toff>binsize:
            mtyset = set()            
            modoff.append(np.mean(offset[i: i+binsize]))
            for j in range(binsize*i, binsize*(i+1)):
                mtyset = mtyset.union(set(cmpcc_dict[str(offset[j])]))
            modspace.append(mtyset)
            toff-=binsize
            i+=1
        
        
        if toff > 0:
            mtyset = set()
            modoff.append(np.mean(offset[i:i+toff]))
            #for j in range(i, toff-1):
            #    spacings[i+toff-1] += spacings[i+toff-1-j]
            #modspace.append(spacings[i+toff-1].sort())
            for j in range(i, toff):
                mtyset = mtyset.union(set(spacings[j]))
            modspace.append(mtyset)
        #print(modspace)
        return modoff, modspace

def findWidth(WS, ww):
    n = WS//ww
    m = ww/5
    if WS-ww*n >= ww*0.7:
        m -= 1
        ww = 5*m
        n += 1
    return ww, n

class Main(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('icons/logo.png'))
        self.OpenFiles_btn.clicked.connect(self.OpenFile)
        self.apply_btn.clicked.connect(self.apply)
        self.clrAll_btn.clicked.connect(self.clearAll)
        self.textArea.setReadOnly(True)
        self.Show_btn.clicked.connect(self.plotOriginalAquGeom)
        self.Zmin_2.clicked.connect(self.zoomin_1)
        self.Zmot_2.clicked.connect(self.zoomout_1)
        self.Show_btn_2.clicked.connect(self.plotCMPCCAquGeom)
        self.Show_btn_3.clicked.connect(self.ShowGather)
        self.Show_btn_4.clicked.connect(self.ShowAmpSpecGather)
        self.doDisp_btn.clicked.connect(self.generateDispersion)
        self.setrModelParam_btn.clicked.connect(self.setModelParam)
        self.Zmin_3.clicked.connect(self.zoomin_2)
        self.Zmot_3.clicked.connect(self.zoomout_2)
        self.binSz = 1
        self.Dright.clicked.connect(self.disNext)
        self.Dleft.clicked.connect(self.disPrev)

        self.gatherScrollArea.setWidgetResizable(True)
        self.gridLayout_g = QtWidgets.QGridLayout(self.scrollAreaWidgetContents_2)
        self.gridLayout_g.setContentsMargins(2, 2, 2, 2)
        self.gridLayout_g.setObjectName("gather_gridLayout")

        self.ampSpecScrollArea.setWidgetResizable(True)
        self.gridLayout_a = QtWidgets.QGridLayout(self.scrollAreaWidgetContents_3)
        self.gridLayout_a.setContentsMargins(2, 2, 2, 2)
        self.gridLayout_a.setObjectName("ampli_gridLayout")


    def OpenFile(self):
        self.filePaths, type = QFileDialog.getOpenFileNames(self,"Select files","C:\\Users\\Admin\\Desktop\\all file _ folder\\wghs","SEG2 files (*.dat);;SEGY files (*.segy)")
        self.tableWidget.setRowCount(len(self.filePaths))
        for ind, fpath in enumerate(self.filePaths):
            item = QtWidgets.QTableWidgetItem()
            self.tableWidget.setItem(ind, 0, item)
            file_name = os.path.basename(fpath)
            self.setFnamesInTable(file_name, ind)

    def setFnamesInTable(self, fname, i):
        _translate = QtCore.QCoreApplication.translate
        item = self.tableWidget.item(i, 0)
        item.setText(_translate("MainWindow", fname))

    def apply(self):
        self.gType = self.GatherComboBox.currentIndex()         #gtype: 0-> CMPCC 1-> CMP
        self.task = threads.ApplyThread(self.filePaths, self.gType)
        self.task.start()
        self.task.thread_msg.connect(self.statusBar.showMessage)
        self.task.file_info.connect(self.showMsg)

    def showMsg(self, info):
        self.sint = info["sint"]; self.ns = info["ns"]
        text = "> Sampling interval: {0}\n> Number of samples in each trace: {1}\n> Number of traces in cmpcc gather: {2}".format(info["sint"], self.ns, info["ntr"])
        self.textArea.appendPlainText(text)

    def clearAll(self):
        self.showStatus("Clearing initiated")
        self.tableWidget.clearContents()
        if os.path.exists("tmp"):
            shutil.rmtree("tmp", ignore_errors=False)

        self.showStatus("Clearing done")

    def showStatus(self, msg):
        self.statusBar.showMessage(msg)

    def plotOriginalAquGeom(self):
        jfile = "tmp/gatherdata/originalLocData.json"
        if os.path.exists(jfile):
            aquGeomPlot.plot(jfile)
            self.statusBar.showMessage("Image saved")
            scene = QtWidgets.QGraphicsScene(self)
            pixmap = QPixmap("tmp/gather_img/oriaqugraph.jpg")
            item = QtWidgets.QGraphicsPixmapItem(pixmap)
            scene.addItem(item)
            self.oriAquGeom_Canv.setScene(scene)
            self.oriAquGeom_Canv.fitInView(scene.sceneRect(), QtCore.Qt.KeepAspectRatio)
        else:
            self.statusBar.showMessage("No data found !!")

    def zoomin_1(self):
        self.oriAquGeom_Canv.scale(1.2, 1.2)

    def zoomout_1(self):
        self.oriAquGeom_Canv.scale(0.8, 0.8)

    def plotCMPCCAquGeom(self):
        jfile = "tmp/gatherdata/srcdata.json"
        if os.path.exists(jfile):
            offset, spacings = binning(self.binsize_sbx.value(), jfile)
            print(offset, spacings)
            aquGeomPlot.plotCMPCCgeom(offset, spacings)
            self.statusBar.showMessage("Image saved")
            scene = QtWidgets.QGraphicsScene(self)
            pixmap = QPixmap("tmp/gather_img/cmpccGeomgraph.jpg")
            item = QtWidgets.QGraphicsPixmapItem(pixmap)
            scene.addItem(item)
            self.cmpccAquGeom_Canv.setScene(scene)
            self.cmpccAquGeom_Canv.fitInView(scene.sceneRect(), QtCore.Qt.KeepAspectRatio)

        else:
            self.statusBar.showMessage("No data found !!")

    def zoomin_2(self):
        self.cmpccAquGeom_Canv.scale(1.2, 1.2)

    def zoomout_2(self):
        self.cmpccAquGeom_Canv.scale(0.8, 0.8)

    def ShowGather(self):
        self.labelNames = []
        
        
        W = self.gatherScrollArea.viewport().width()
        self.w, num_of_plots_in_a_Row = findWidth(W, 400)

        srcDictFile = "tmp/gatherdata/srcdata.json"
        traceDictFile = "tmp/gatherdata/trcdata.json"
        if os.path.exists(srcDictFile) and os.path.exists(traceDictFile):
            gatherDict_f = open(srcDictFile, "r")
            traceDict_f = open(traceDictFile, "r")
            gatherDict = json.load(gatherDict_f)["gather_dict"]
            traceDict  = json.load(traceDict_f)["TraceData"]
            
            self.gatherTask = threads.GatherImgThread(num_of_plots_in_a_Row=num_of_plots_in_a_Row,gatherDict=gatherDict, traceDict=traceDict, gtype=1, sampSize=1500, Sint=0.001) #self.gType, sampSize=self.ns , Sint=self.sint)
            self.gatherTask.start()
            self.gatherTask.fnameEmit.connect(self.setPlotinGatherCanvas)
            self.gatherTask.thread_msg.connect(self.statusBar.showMessage)

        else:
            self.statusBar.showMessage("No data found !!")

        
    def setPlotinGatherCanvas(self, fname, i, rnum, cnum):

        label = f"gatherPlotlabel_{i}"
        self.gatherPlotlabel = QtWidgets.QLabel(label, self.gatherScrollArea)
        pixmap = QPixmap(fname)
        pixmap = pixmap.scaledToWidth(self.w)
        self.gatherPlotlabel.resize(self.w, pixmap.height()+2)
        self.gatherPlotlabel.setPixmap(pixmap)
        self.gridLayout_g.addWidget(self.gatherPlotlabel, rnum, cnum) 
        self.gatherPlotlabel.show()
        self.labelNames.append(label)

        
###############   Amplitude Spectrum Functionality ######################        


    def ShowAmpSpecGather(self):
        self.labelNames = []
        
        
        W = self.ampSpecScrollArea.viewport().width()
        self.w, num_of_plots_in_a_Row = findWidth(W, 500)

        srcDictFile = "tmp/gatherdata/srcdata.json"
        traceDictFile = "tmp/gatherdata/trcdata.json"
        if os.path.exists(srcDictFile) and os.path.exists(traceDictFile):
            gatherDict_f = open(srcDictFile, "r")
            traceDict_f = open(traceDictFile, "r")
            gatherDict = json.load(gatherDict_f)["gather_dict"]
            traceDict  = json.load(traceDict_f)["TraceData"]

            self.ampSpecTask = threads.fftImgThread(num_of_plots_in_a_Row=num_of_plots_in_a_Row,gatherDict=gatherDict, traceDict=traceDict, gtype=1, sampSize=1500, Sint=0.001) #self.gType, sampSize=self.ns , Sint=self.sint)
            self.ampSpecTask.start()
            self.ampSpecTask.fnameEmit.connect(self.setPlotinAmpSpecCanvas)
            self.ampSpecTask.thread_msg.connect(self.statusBar.showMessage)

        else:
            self.statusBar.showMessage("No data found !!")

        
    def setPlotinAmpSpecCanvas(self, fname, i, rnum, cnum):

        label = f"ampSpecPlotlabel_{i}"
        self.ampSpecPlotlabel = QtWidgets.QLabel(label, self.ampSpecScrollArea)
        pixmap = QPixmap(fname)
        pixmap = pixmap.scaledToWidth(self.w)
        self.ampSpecPlotlabel.resize(self.w, pixmap.height()+2)
        self.ampSpecPlotlabel.setPixmap(pixmap)
        self.gridLayout_a.addWidget(self.ampSpecPlotlabel, rnum, cnum) 
        self.ampSpecPlotlabel.show()
        self.labelNames.append(label)

# --------------------------------------------------------------#
################ Dispersion fuctionality ######################
# --------------------------------------------------------------#

    def generateDispersion(self):
        """
        Generate dispersion curve plots
        set them to -> traces_Canv, geomCanv, dispCurveCanv

        """
        

        dispdata = {
            "trimstat": self.trim_chk.isChecked(),"trim_begin" : self.trStrt_edt.text(),
            "trim_end" : self.trEnd_edt.text(),"fmin":self.fMin_edt.text(),"fmax":self.fmax_edt.text(),
            "vmin":self.vMin_edt.text(),"vmax":self.vMax_edt.text(),"signal_begin":self.sigStrt_edt.text(),
            "signal_end":self.sigEnd_edt.text(),"noise_begin":self.nStrt_edt.text(),
            "noise_end":self.nEnd_edt.text(),"vspace":self.vspace_edt.currentText(),"nvel": 400
        }

        srcDictFile = "tmp/gatherdata/srcdata.json"
        traceDictFile = "tmp/gatherdata/trcdata.json"
        if os.path.exists(srcDictFile) and os.path.exists(traceDictFile):
            gatherDict_f = open(srcDictFile, "r")
            traceDict_f = open(traceDictFile, "r")
            gatherDict = json.load(gatherDict_f)["gather_dict"]
            traceDict  = json.load(traceDict_f)["TraceData"]
            self.slocs = list(gatherDict.keys())
            
            self.Disptask = threads.DispersionThread(dispdata=dispdata, gatherDict=gatherDict, traceDict=traceDict, sint=0.001)
            self.Disptask.start()
            self.Disptask.setplot.connect(self.setDispPlots) 
            self.Disptask.thread_msg.connect(self.statusBar.showMessage)      


        else:
            self.statusBar.showMessage("No data found !!")
        

    def setDispPlots(self, sloc):
        dirs = ['tmp/dispersion/signal', 'tmp/dispersion/disp']
        
        tfw = self.traces_Canv.viewport().width()
        dcw = self.DisperCurve_Canvas.viewport().width()
        dch = self.DisperCurve_Canvas.viewport().height()

        fnames = [dir + "/src-"+ sloc + ".jpg" for dir in dirs]

        self.loca_edt.setText(sloc)
        
        pixmap_1 = QPixmap(fnames[0])
        pixmap_1 = pixmap_1.scaledToWidth(tfw-10)
        self.traces_Canvlabel.resize(tfw - 10, pixmap_1.height()+2)
        self.traces_Canvlabel.setPixmap(pixmap_1)
        #self.gridLayout_td.addWidget(self.traces_Canvlabel) #, rnum, cnum) 
        
        
        pixmap_2 = QPixmap(fnames[1])
        pixmap_2 = pixmap_2.scaledToHeight(dch-10)
        self.DisperCurve_Canvaslabel.resize(pixmap_2.width()+2 , dch-10)
        self.DisperCurve_Canvaslabel.setPixmap(pixmap_2)
        #self.gridLayout_dd.addWidget(self.DisperCurve_Canvaslabel) #, 0, 0) 
        if (dcw+10) > pixmap_2.width():
            self.verticalLayout_6.setContentsMargins((dcw+10 - pixmap_2.width())//2, 5, 5, 5)

        self.traces_Canvlabel.show()
        self.DisperCurve_Canvaslabel.show()

        

    def makePositioanlplots(self):

        pass

    def disNext(self):
        """
        goto next dispersion plot, set locaton of the 
        shot (if gtype=1 i.e. cmp) or cmp (if gtype=2 i.e. cmpcc)
        set dispersion plots to traces_Canv, geomCanv, dispCurveCanv 
        this frames
        """
        pass

    def disPrev(self):
        """
        goto previous dispersion plot, set locaton of the 
        shot (if gtype=1 i.e. cmp) or cmp (if gtype=2 i.e. cmpcc)
        set dispersion plots to traces_Canv, geomCanv, dispCurveCanv 
        this frames
        """
        pass
# --------------------------------------------------------------#
################## Inversion functionality ######################
# --------------------------------------------------------------#

    def setModelParam(self):
        pass




class GatherImages(QtCore.QThread):

    def __init__(self, gatherDict, traceDict, gtype, sampSize, Sint,parent=None):
        super().__init__(parent)
        self.gatherDict = gatherDict
        self.traceDict = traceDict
        self.gType = gtype
        self.sampsize= sampSize
        self.sint=Sint
        self.flder="tmp/gathers_img"
        self.ampfactor = 1

    def GeneratePlot(self):
        source = list(self.gatherDict.keys())
        t = np.arange(0, self.sampsize*self.sint, self.sint)

        for i in range(source):
            fig, ax = plt.subplots(figsize=(10,5))

            rcvrs = self.gatherDict[source[i]]
            for k in range(len(rcvrs)):
                traceData = np.array(self.traceDict[i][k])                
                traceData = ( traceData + rcvrs[k])*self.ampfactor
                ax.fill_between(t,rcvrs[k], traceData, where=traceData>rcvrs[k], interpolate=True, color="black")
                ax.grid(linestyle="--", linewidth="1", color="g")
                ax.set_xlim([np.min(t), np.max(t)])
                
            if self.gtype==0:
                labels = ["Reciver location", "Source location ", "/cmp-"]
            else:
                labels = ["Spacing in ", "CMP location ", "/cmpcc-"]

            ax.set_xlabel("Time")
            ax.set_ylabel(labels[0]+self.unit)
            ax.set_title(labels[1]+str(source[i])+self.unit)
            #ax.grid()
            fname = self.flder+labels[2]+str(source[i])+".png"
            fig.savefig(fname)

    def ampUp(self):
        self.ampfactor += 1
        self.GeneratePlot()

    def ampDown(self):
        self.ampfactor += 1
        self.GeneratePlot()

    def setInCanvas(self):
        pass
    



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())
