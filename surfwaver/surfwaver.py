from plugin.maswGui import Ui_MainWindow
from prefwinc import PrefWin
from manualpicking import ManPick
from setmodel import SetModel

import sys
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QApplication 
from PyQt5 import QtCore, QtWidgets, QtGui
import os
from res import aquGeomPlot, writelog, threads
import shutil
from PyQt5.QtGui import QPixmap
import json
import numpy as np
import matplotlib.pyplot as plt 
import webbrowser
import subprocess


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
        
        self.setGlobalVariables()
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
        self.manPick_btn.clicked.connect(self.OpenManpickWin)
        self.Zmin_3.clicked.connect(self.zoomin_2)
        self.Zmot_3.clicked.connect(self.zoomout_2)
        self.actionpreferences.triggered.connect(self.openPrefWin)
        self.actionOpen_browser.triggered.connect(self.oponDocs)
        self.rootdir.clicked.connect(self.setrootdir)
        self.binSz = 1
        self.Dright.clicked.connect(self.disNext)
        self.Dleft.clicked.connect(self.disPrev)
        self.right.clicked.connect(self.invNxt)
        self.left.clicked.connect(self.invPrev)


        self.doInv_btn.clicked.connect(self.StartInversion)
        self.do2dinv.clicked.connect(self.start2dinv)

        self.gatherScrollArea.setWidgetResizable(True)
        self.gridLayout_g = QtWidgets.QGridLayout(self.scrollAreaWidgetContents_2)
        self.gridLayout_g.setContentsMargins(2, 2, 2, 2)
        self.gridLayout_g.setObjectName("gather_gridLayout")

        self.ampSpecScrollArea.setWidgetResizable(True)
        self.gridLayout_a = QtWidgets.QGridLayout(self.scrollAreaWidgetContents_3)
        self.gridLayout_a.setContentsMargins(2, 2, 2, 2)
        self.gridLayout_a.setObjectName("ampli_gridLayout")

        self.slocindx= -1
        self.maxsrcs = -1
        
    def setrootdir(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(None, "Select a folder")
        self.ROOT = folder
        f = self.pref.setrootdir(folder)
        if f:
            self.statusBar.setStyleSheet("color: green")
            self.statusBar.showMessage("Rootdir updated")
        else:
            self.statusBar.setStyleSheet("color: red")
            self.statusBar.showMessage("Error occurred during new root settings")
        
    def setGlobalVariables(self):
        self.start_inv = True

        self.pref = writelog.sysParam()
        self.ROOT = self.pref.getrootdir()

        self.start_dispersion =True
        self.gType = 0
        self.ns = 0
        self.sint = 0


    def setSintNsGtype(self):
        try:
            with open(self.ROOT+"/logdata.json", "r") as f:
                jobj = json.load(f)
                f.close()
                self.ns = jobj["ns"]
                self.sint = jobj["sint"]
                self.gType = jobj["gtype"]
        except:
            print("logdata.json fie not found!!")
            raise FileNotFoundError
        

    def setModelParam(self):
        if self.numLay_spin.value() >=2: 
            self.setmodel = SetModel(self, nlayer=self.numLay_spin.value())
            self.setmodel.show()
        else:
            self.statusBar.setStyleSheet("color: red")
            self.statusBar.showMessage("*** Number of layers must be atleast 2 of more then 2 *****")
            #self.statusBar.setStyleSheet("color: black")
#
    def OpenManpickWin(self):
        if os.path.exists(self.ROOT+"/dispersion//dispdata.json"):
            subprocess.Popen(["python", "plugin/manpikwtk.py"])
        else:
            self.statusBar.setStyleSheet("color: red")
            self.statusBar.showMessage("***Dispersion data is not found*****")
        #self.manpick = ManPick(self)
        #self.manpick.show()

    def openPrefWin(self):
        self.prefwin = PrefWin(self)
        self.prefwin.show()

    def oponDocs(self):
        webbrowser.open("https://github.com/Shanu911/SurfWaver/tree/main/docs")
        

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
        print(self.gType)
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
        if os.path.exists(self.ROOT):
            shutil.rmtree(self.ROOT, ignore_errors=False)

        self.showStatus("Clearing done")

    def showStatus(self, msg):
        self.statusBar.showMessage(msg)

    def plotOriginalAquGeom(self):
        jfile = self.ROOT+"/gatherdata/originalLocData.json"
        if os.path.exists(jfile):
            aquGeomPlot.plot(jfile)
            self.statusBar.showMessage("Image saved")
            scene = QtWidgets.QGraphicsScene(self)
            pixmap = QPixmap(self.ROOT+"/gather_img/oriaqugraph.jpg")
            item = QtWidgets.QGraphicsPixmapItem(pixmap)
            scene.addItem(item)
            self.oriAquGeom_Canv.setScene(scene)
            #self.oriAquGeom_Canv.fitInView(scene.sceneRect(), QtCore.Qt.KeepAspectRatio)
        else:
            self.statusBar.showMessage("No data found !!")

    def zoomin_1(self):
        self.oriAquGeom_Canv.scale(1.2, 1.2)

    def zoomout_1(self):
        self.oriAquGeom_Canv.scale(0.8, 0.8)

    def plotCMPCCAquGeom(self):
        jfile = self.ROOT+"/gatherdata/srcdata.json"
        if os.path.exists(jfile):
            offset, spacings = binning(self.binsize_sbx.value(), jfile)
            #print(offset, spacings)
            aquGeomPlot.plotCMPCCgeom(offset, spacings)
            self.statusBar.showMessage("Image saved")
            scene = QtWidgets.QGraphicsScene(self)
            pixmap = QPixmap(self.ROOT+"/gather_img/cmpccGeomgraph.jpg")
            item = QtWidgets.QGraphicsPixmapItem(pixmap)
            scene.addItem(item)
            self.cmpccAquGeom_Canv.setScene(scene)
            #self.cmpccAquGeom_Canv.fitInView(scene.sceneRect(), QtCore.Qt.KeepAspectRatio)

        else:
            self.statusBar.showMessage("No data found !!")

    def zoomin_2(self):
        self.cmpccAquGeom_Canv.scale(1.2, 1.2)

    def zoomout_2(self):
        self.cmpccAquGeom_Canv.scale(0.8, 0.8)

    def ShowGather(self):
        self.labelNames = []        
        if (self.ns==0 or self.sint== 0):
            self.setSintNsGtype()
        
        W = self.gatherScrollArea.viewport().width()
        self.w, num_of_plots_in_a_Row = findWidth(W, 400)

        srcDictFile = self.ROOT+"/gatherdata/srcdata.json"
        traceDictFile = self.ROOT+"/gatherdata/trcdata.json"
        if os.path.exists(srcDictFile) and os.path.exists(traceDictFile):
            gatherDict_f = open(srcDictFile, "r")
            traceDict_f = open(traceDictFile, "r")
            gatherDict = json.load(gatherDict_f)["gather_dict"]
            traceDict  = json.load(traceDict_f)["TraceData"]
            
            self.gatherTask = threads.GatherImgThread(num_of_plots_in_a_Row=num_of_plots_in_a_Row, 
                                gatherDict=gatherDict, traceDict=traceDict, gtype=self.gType, sampSize=self.ns , 
                                Sint=self.sint)         # 1, sampSize=self.ns, Sint=0.001) #
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
        #print(pixmap.width(), pixmap.height())  #get size hint
        self.gatherPlotlabel.resize(self.w, pixmap.height()+2)
        self.gatherPlotlabel.setPixmap(pixmap)
        self.gridLayout_g.addWidget(self.gatherPlotlabel, rnum, cnum) 
        self.gatherPlotlabel.show()
        self.labelNames.append(label)

        
###############   Amplitude Spectrum Functionality ######################        


    def ShowAmpSpecGather(self):
        self.labelNames = []
        if (self.ns==0 or self.sint==0):
            self.setSintNsGtype()
        
        W = self.ampSpecScrollArea.viewport().width()
        self.w, num_of_plots_in_a_Row = findWidth(W, 800)

        srcDictFile = self.ROOT+"/gatherdata/srcdata.json"
        traceDictFile = self.ROOT+"/gatherdata/trcdata.json"
        if os.path.exists(srcDictFile) and os.path.exists(traceDictFile):
            gatherDict_f = open(srcDictFile, "r")
            traceDict_f = open(traceDictFile, "r")
            gatherDict = json.load(gatherDict_f)["gather_dict"]
            traceDict  = json.load(traceDict_f)["TraceData"]

            self.ampSpecTask = threads.fftImgThread(num_of_plots_in_a_Row=num_of_plots_in_a_Row,
                        gatherDict=gatherDict, traceDict=traceDict, 
                        gtype=self.gType, sampSize=self.ns , Sint=self.sint)
                            #1, sampSize=1500, Sint=0.001) #
            self.ampSpecTask.start()
            self.ampSpecTask.fnameEmit.connect(self.setPlotinAmpSpecCanvas)
            self.ampSpecTask.thread_msg.connect(self.statusBar.showMessage)

        else:
            self.statusBar.showMessage("No data found !!")

        
    def setPlotinAmpSpecCanvas(self, fname, i, rnum, cnum):

        label = f"ampSpecPlotlabel_{i}"
        self.ampSpecPlotlabel = QtWidgets.QLabel(label, self.ampSpecScrollArea)
        pixmap = QPixmap(fname)
        # pixmap = pixmap.scaledToWidth(self.w)
        #print(pixmap.width(), pixmap.height())  #get size hint
        self.ampSpecPlotlabel.resize(pixmap.width()+4, pixmap.height()+2)
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
        
        if self.start_dispersion:
            dispdata = {
                "trimstat": self.trim_chk.isChecked(),"trim_begin" : float(self.trStrt_edt.text()),
                "trim_end" : float(self.trEnd_edt.text()),"fmin":float(self.fMin_edt.text()),"fmax":float(self.fmax_edt.text()),
                "vmin": float(self.vMin_edt.text()),"vmax": float(self.vMax_edt.text()),"signal_begin": float(self.sigStrt_edt.text()),
                "signal_end":float(self.sigEnd_edt.text()),"noise_begin":float(self.nStrt_edt.text()),
                "transform": self.TransformType.currentText(), "noise_end":float(self.nEnd_edt.text()),
                "vspace":self.vspace_edt.currentText(),"nvel": 400, "mintrace":self.minTraces.value()
            }
            
            try:
                with open(self.ROOT + "/logdata.json", "r") as f:
                    logdata = json.load(f)
                    logdata["v_phase_lim"] = [float(self.vMin_edt.text()), float(self.vMax_edt.text())]
                    logdata["freq_lim"] = [float(self.fMin_edt.text()), float(self.fmax_edt.text())]
                    new_logdata = json.dumps(logdata)
                    f.close()

                with open(self.ROOT + "/logdata.json", "w") as f:            
                    f.write(new_logdata)
                    f.close()
            except:
                print("logdata file not found!!")
                raise FileNotFoundError()
                

            srcDictFile = self.ROOT+"/gatherdata/srcdata.json"
            traceDictFile = self.ROOT+"/gatherdata/trcdata.json"
            if os.path.exists(srcDictFile) and os.path.exists(traceDictFile):
                gatherDict_f = open(srcDictFile, "r")
                traceDict_f = open(traceDictFile, "r")
                gatherDict = json.load(gatherDict_f)["gather_dict"]
                traceDict  = json.load(traceDict_f)["TraceData"]

                self.Disptask = threads.DispersionThread(dispdata=dispdata, gatherDict=gatherDict, 
                                    traceDict=traceDict, filterWidth=self.filterWidth.value(), 
                                    sint=logdata["sint"])
                self.Disptask.start()
                self.Disptask.setplot.connect(self.setDispPlots) 
                self.Disptask.thread_msg.connect(self.statusBar.showMessage)    
                self.Disptask.sindx.connect(self.setslocnmaxsloc)
                self.Disptask.endprocss.connect(self.endDisp)

                self.doDisp_btn.setText("Stop\nProcess")
                self.doDisp_btn.setStyleSheet("font: 75 11pt \"Calibri\";\n"
                                            "background: rgb(255, 150, 190)")
                self.start_dispersion = False

            else:
                self.statusBar.showMessage("No data found !!")
        else:
            self.Disptask.stop()
            self.endDisp()

        
    def endDisp(self):
        # make "Generate Dispersion Curves" btn to initial stage
        self.doDisp_btn.setText("Generate\nDispersion Curves")
        self.doDisp_btn.setStyleSheet("font: 75 11pt \"Calibri\";\n"
"background: rgb(85, 255, 127)")
        self.start_dispersion = True
        
    def setslocnmaxsloc(self, lst):
        self.sourcelocs = lst
        self.slocindx = len(lst) - 1
        self.maxsrcs = len(lst)

    def setDispPlots(self, sloc):
        dirs = [self.ROOT + '/dispersion/signal', self.ROOT + '/dispersion/disp']
        
        tfw = self.traces_Canv.viewport().width()
        dcw = self.DisperCurve_Canvas.viewport().width()
        dch = self.DisperCurve_Canvas.viewport().height()

        fnames = [f"{dir}/src-{sloc}.png" for dir in dirs]

        self.loca_edt.setText(sloc)
        
        pixmap_1 = QPixmap(fnames[0])
        pixmap_1 = pixmap_1.scaledToWidth(tfw-10)
        #print(pixmap_1.width(), pixmap_1.height())
        self.traces_Canvlabel.resize(tfw - 10, pixmap_1.height()+2)
        self.traces_Canvlabel.setPixmap(pixmap_1)
        #self.gridLayout_td.addWidget(self.traces_Canvlabel) #, rnum, cnum) 
        
        
        pixmap_2 = QPixmap(fnames[1])
        pixmap_2 = pixmap_2.scaledToHeight(dch-10)
        self.DisperCurve_Canvaslabel.resize(pixmap_2.width()+2 , dch-10)
        self.DisperCurve_Canvaslabel.setPixmap(pixmap_2)
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
        try:
            if self.slocindx<self.maxsrcs-1:
                self.slocindx += 1   
                print(f"disnexet if{self.slocindx}")            
                self.setDispPlots(self.sourcelocs[self.slocindx])


            else:
                self.slocindx=1
                self.setDispPlots(self.sourcelocs[self.slocindx])
                print(f"disnexet if flase{self.slocindx}")    
            pass
        except:
            print("Error occured at disNext()")
            self.statusBar.showMessage("No Source locations registered!!")

    def disPrev(self):
        """
        goto previous dispersion plot, set locaton of the 
        shot (if gtype=1 i.e. cmp) or cmp (if gtype=2 i.e. cmpcc)
        set dispersion plots to traces_Canv, geomCanv, dispCurveCanv 
        this frames
        """
        try:
            if self.slocindx>1:

                self.slocindx -= 1   
                print(self.slocindx)         
                self.setDispPlots(self.sourcelocs[self.slocindx])
            else:
                self.slocindx=self.maxsrcs-1
                self.setDispPlots(self.sourcelocs[self.slocindx])
                print(f"disprev if{self.slocindx}")    
        except:
            print("Error occured at disPrev()")
            self.statusBar.showMessage("No Source locations registered!!")
# --------------------------------------------------------------#
################## Inversion functionality ######################
# --------------------------------------------------------------#

    def StartInversion(self):
        self.statusBar.showMessage("%")        
        #print(self.optimType_comb.currentText())
        if self.start_inv:
            self.inversion = threads.InversionThread(method=self.optimType_comb.currentText(),
                                     maxrun=self.numIter_spin.value(), root=self.ROOT)
            self.inversion.start()
            self.inversion.thread_msg.connect(self.statusBar.showMessage)
            self.inversion.imgnames.connect(self.setInversionPlot)
            self.inversion.sindx.connect(self.setslocnmaxsloc)
            self.inversion.endprocss.connect(self.endINV)
            self.doInv_btn.setText("Stop Inversion")
            self.doInv_btn.setStyleSheet("font: 75 11pt \"Calibri\";\n"
"background: rgb(255, 150, 190)")
            self.start_inv = False

        else:
            self.inversion.stop()
            self.endINV()
            
            
    def endINV(self):
        self.doInv_btn.setText("Start Inversion")
        self.doInv_btn.setStyleSheet("font: 75 11pt \"Calibri\";\n"
                            "background: rgb(85, 255, 127)")
        self.start_inv = True

    def setInversionPlot(self, fllist):
        """     index   string type
        fllist: 0:      source loca (str)
                1:      vp
                2:      vs
                3:      rho
                4:      misfit
                5:      curve
                    or
                0:      source loca (str)
        """
        if len(fllist)==1:
            dirs = [self.ROOT+"/inversion/model/vp", self.ROOT+"/inversion/model/vs", 
                    self.ROOT+"/inversion/model/rho",
                    self.ROOT+"/inversion/misfit", self.ROOT+"/inversion/curve"]
            for d in dirs:
                fllist.append(f"{d}/{d.split('/')[-1]}_{fllist[0]}.png")
        mdfw = self.scrollArea_4.viewport().width()
        dcfh = self.scrollArea_6.viewport().height()
        mffh = self.scrollArea_7.viewport().height()

        modlist = [self.Modellabel0, self.Modellabel1, self.Modellabel2]
        layout = [self.verticalLayout_14, self.verticalLayout_15, self.verticalLayout_16]
        # source loca in line edit
        self.lineEdit_12.setText(fllist[0])
        # curve
        pixmap_1 = QPixmap(fllist[5])
        pixmap_1 = pixmap_1.scaledToHeight(dcfh-10)
        #print(f"curve: w {pixmap_1.width()}, h {pixmap_1.height()}")
        self.dispCanv_2.resize(pixmap_1.width(), pixmap_1.height())
        self.dispCanv_2.setPixmap(pixmap_1)
        #self.gridLayout_td.addWidget(self.traces_Canvlabel) #, rnum, cnum) 
        
        # misfit
        pixmap_2 = QPixmap(fllist[4])
        pixmap_2 = pixmap_2.scaledToHeight(mffh-10)
        #print(f"misfit: w {pixmap_2.width()}, h {pixmap_2.height()}")
        self.misfitCanv.resize(pixmap_2.width(), pixmap_2.height())
        self.misfitCanv.setPixmap(pixmap_2)

        # model
        for m in range(3):
            pixmap = QPixmap(fllist[m+1])
            #pixmap = pixmap.scaledToHeight(mdfh-10)

            modlist[m].resize(pixmap.width(), pixmap.height())
            modlist[m].setPixmap(pixmap)
            if (mdfw+10) > pixmap.width():
                layout[m].setContentsMargins((mdfw+10 - pixmap.width())//2, 5, 5, 5)

        #print(pixmap.width(), pixmap.height())
            


    def invNxt(self):
        try:
            if self.slocindx<self.maxsrcs-1:
                self.slocindx += 1   
                #print(f"disnexet if{self.slocindx}")            
                self.setInversionPlot([self.sourcelocs[self.slocindx]])       
            else:
                self.slocindx=1
                self.setInversionPlot([self.sourcelocs[self.slocindx]])
                #print(f"disnexet if flase{self.slocindx}")    
        except:
            print("Error occured at invNxt()")
            self.statusBar.showMessage("No Source locations registered!!")

    def invPrev(self):
        try:
            if self.slocindx>1:
                self.slocindx -= 1   
                #print(self.slocindx)         
                self.setInversionPlot([self.sourcelocs[self.slocindx]])
            else:
                self.slocindx=self.maxsrcs-1
                self.setInversionPlot([self.sourcelocs[self.slocindx]])
                #print(f"disprev if{self.slocindx}")    
        except:
            print("Error occured at invPrev()")
            self.statusBar.showMessage("No Source locations registered!!")
# --------------------------------------------------------------#
################## 2D Inversion functionality ####################
# --------------------------------------------------------------#
    def start2dinv(self):
        self.inv2dthread = threads.Inversion2dThread()
        self.inv2dthread.start()
        self.inv2dthread.thread_msg.connect(self.statusBar.showMessage)
        self.inv2dthread.setplot.connect(self.set2dinvplot)


    def set2dinvplot(self, imgfnames):
        canvas = [self.rh_canvas, self.vp_canvas, self.vs_canvas]
        for i in range(len(canvas)):
            pixmap = QPixmap(imgfnames[i])
            canvas[i].resize(pixmap.width(), pixmap.height())
            canvas[i].setPixmap(pixmap)


#class GatherImages(QtCore.QThread):
#
#    def __init__(self, gatherDict, traceDict, gtype, sampSize, Sint,parent=None):
#        super().__init__(parent)
#        self.gatherDict = gatherDict
#        self.traceDict = traceDict
#        self.gType = gtype
#        self.sampsize= sampSize
#        self.sint=Sint
#        self.flder=self.ROOT+"/gathers_img"
#        self.ampfactor = 1
#
#    def GeneratePlot(self):
#        source = list(self.gatherDict.keys())
#        t = np.arange(0, self.sampsize*self.sint, self.sint)
#
#        for i in range(source):
#            fig, ax = plt.subplots(figsize=(10,5))
#
#            rcvrs = self.gatherDict[source[i]]
#            for k in range(len(rcvrs)):
#                traceData = np.array(self.traceDict[i][k])                
#                traceData = ( traceData + rcvrs[k])*self.ampfactor
#                ax.fill_between(t,rcvrs[k], traceData, where=traceData>rcvrs[k], interpolate=True, color="black")
#                ax.grid(linestyle="--", linewidth="1", color="g")
#                ax.set_xlim([np.min(t), np.max(t)])
#                
#            if self.gtype==0:
#                labels = ["Reciver location", "Source location ", "/cmp-"]
#            elif self.gtype==1:
#                labels = ["Spacing in ", "CMP location ", "/cmpcc-"]
#            else:
#                raise ValueError()
#
#            ax.set_xlabel("Time")
#            ax.set_ylabel(labels[0]+self.unit)
#            ax.set_title(labels[1]+str(source[i])+self.unit)
#            #ax.grid()
#            fname = self.flder+labels[2]+str(source[i])+".png"
#            fig.savefig(fname)
#
#    def ampUp(self):
#        self.ampfactor += 1
#        self.GeneratePlot()
#
#    def ampDown(self):
#        self.ampfactor += 1
#        self.GeneratePlot()
#
#    def setInCanvas(self):
#        pass
#    



if __name__ == "__main__":    
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())
