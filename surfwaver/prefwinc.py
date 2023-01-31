from plugin.preferWin import Ui_MainWindow as UI_prefWin
from PyQt5.QtWidgets import QMainWindow 
from PyQt5 import QtGui, QtWidgets
import json
from attrdict import AttrDict
import os
from res.writelog import sysParam

settings_file = "log\settings.json"
default_settings_file = "log\default_settings.json"

class PrefWin(QMainWindow, UI_prefWin):
    def __init__(self, parent=None):
        super(PrefWin, self).__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('icons/logo.png'))
        
        self.updatedata()
        self.apply_btn.clicked.connect(self.Apply)
        self.reset_btn.clicked.connect(self.Reset)
        self.gs_selct_dir_btn.clicked.connect(self.openfm)

    def Apply(self):
        self.data["gframe"]["rootdir"] = self.rootdir.text()
        self.data["gframe"]["AquGeom"]["original"]["w"] = float(self.gsagoriw.text())
        self.data["gframe"]["AquGeom"]["original"]["h"] = float(self.gsagorih.text())
        self.data["gframe"]["AquGeom"]["original"]["dpi"] = float(self.gsagoridpi.text())

        self.data["gframe"]["AquGeom"]["cmpcc"]["w"] =     float(self.gsagcmpccw.text())
        self.data["gframe"]["AquGeom"]["cmpcc"]["h"] =     float(self.gsagcmpcch.text())
        self.data["gframe"]["AquGeom"]["cmpcc"]["dpi"] =   float(self.gsagcmpccdpi.text())

        self.data["gframe"]["gather"]["w"] =     float(self.gsgtw.text())
        self.data["gframe"]["gather"]["h"] =     float(self.gsgth.text())
        self.data["gframe"]["gather"]["dpi"] =   float(self.gsgtdpi.text())

        self.data["gframe"]["AmpSpec"]["w"] =     float(self.gsastw.text())
        self.data["gframe"]["AmpSpec"]["h"] =     float(self.gsasth.text())
        self.data["gframe"]["AmpSpec"]["dpi"] =   float(self.gsastdpi.text())



        self.data["dframe"]["gather"]["w"] =     float(self.dsgsw.text())
        self.data["dframe"]["gather"]["h"] =     float(self.dsgsh.text())
        self.data["dframe"]["gather"]["dpi"] =   float(self.dsgsdpi.text())

        self.data["dframe"]["AquGeom"]["w"] =     float(self.dsgeosw.text())
        self.data["dframe"]["AquGeom"]["h"] =     float(self.dsgeosh.text())
        self.data["dframe"]["AquGeom"]["dpi"] =   float(self.dsgeosdpi.text())

        self.data["dframe"]["dispCurve"]["w"] =     float(self.dsdcsw.text())
        self.data["dframe"]["dispCurve"]["h"] =     float(self.dsdcsh.text())
        self.data["dframe"]["dispCurve"]["dpi"] =   float(self.dsdcsdpi.text())

        self.data["dframe"]["init_data"]["trim"] =      [float(self.trStrt_edt.text()), float(self.trEnd_edt.text())]
        self.data["dframe"]["init_data"]["frequency"]=  [float(self.fMin_edt.text()), float(self.fmax_edt.text())]
        self.data["dframe"]["init_data"]["signal"] =    [float(self.sigStrt_edt.text()), float(self.sigEnd_edt.text())]
        self.data["dframe"]["init_data"]["noise"] =     [float(self.nStrt_edt.text()), float(self.nEnd_edt.text())]
        self.data["dframe"]["init_data"]["velocity"] =  [float(self.vMin_edt.text()), float(self.vMax_edt.text())]
        self.data["dframe"]["init_data"]["vstep"] =     float(self.vstep.text())



        self.data["iframe"]["dispCurve"]["w"] =     float(self.isdccw.text())
        self.data["iframe"]["dispCurve"]["h"] =     float(self.isdcch.text())
        self.data["iframe"]["dispCurve"]["dpi"] =   float(self.isdccdpi.text())

        self.data["iframe"]["model"]["w"] =     float(self.isfmcw.text())
        self.data["iframe"]["model"]["h"] =     float(self.isfmch.text())
        self.data["iframe"]["model"]["dpi"] =   float(self.isfmcdpi.text())

        self.data["iframe"]["misfit"]["w"] =     float(self.ismcw.text())
        self.data["iframe"]["misfit"]["h"] =     float(self.ismch.text())
        self.data["iframe"]["misfit"]["dpi"] =   float(self.ismcdpi.text())

        self.data["rframe"]["w"] =     float(self.is2dmcw.text())
        self.data["rframe"]["h"] =     float(self.is2dmch.text())
        self.data["rframe"]["dpi"] =   float(self.is2dmcdpi.text())


        f = self.pref.setall(self.data)
        if f:     
            self.statusBar().setStyleSheet("color: green")
            self.statusBar().showMessage("Applied!!")
        else:
            self.statusBar().setStyleSheet("color: red")
            self.statusBar().showMessage("Error occured!!")

    def Reset(self):
        f = self.pref.reset()
        if f:
            self.updatedata()
            self.statusBar().setStyleSheet("color: blue")
            self.statusBar().showMessage("Data reset to default value")
        else:
            self.statusBar().setStyleSheet("color: red")
            self.statusBar().showMessage("Error occured!!")

        

    def openfm(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(None, "Select a folder")
        self.rootdir.setText(os.path.expanduser(folder))


    def updatedata(self):
        try:     
            self.pref = sysParam()       
            self.data = self.pref.datade()            
            #### gather section ####
            if self.data.gframe.rootdir is not None:
                self.rootdir.setText(self.data.gframe.rootdir)
            else:
                self.rootdir.setText(os.path.expanduser('~'))

            self.gsagorih.setText(str(self.data.gframe.AquGeom.original.h))
            self.gsagoriw.setText(str(self.data.gframe.AquGeom.original.w))
            self.gsagoridpi.setText(str(self.data.gframe.AquGeom.original.dpi))
            self.gsagcmpcch.setText(str(self.data.gframe.AquGeom.cmpcc.h))
            self.gsagcmpccw.setText(str(self.data.gframe.AquGeom.cmpcc.w))
            self.gsagcmpccdpi.setText(str(self.data.gframe.AquGeom.cmpcc.dpi))
            self.gsgth.setText(str(self.data.gframe.gather.h))
            self.gsgtw.setText(str(self.data.gframe.gather.w))
            self.gsgtdpi.setText(str(self.data.gframe.gather.dpi))
            self.gsasth.setText(str(self.data.gframe.AmpSpec.h))
            self.gsastw.setText(str(self.data.gframe.AmpSpec.w))
            self.gsastdpi.setText(str(self.data.gframe.AmpSpec.dpi))


            ##### Disp section ####
            self.trStrt_edt.setText(str(self.data.dframe.init_data.trim[0]))
            self.trEnd_edt.setText(str(self.data.dframe.init_data.trim[1]))
            self.fMin_edt.setText(str(self.data.dframe.init_data.frequency[0]))
            self.fmax_edt.setText(str(self.data.dframe.init_data.frequency[1]))
            self.sigStrt_edt.setText(str(self.data.dframe.init_data.signal[0]))
            self.sigEnd_edt.setText(str(self.data.dframe.init_data.signal[1]))
            self.nStrt_edt.setText(str(self.data.dframe.init_data.noise[0]))
            self.nEnd_edt.setText(str(self.data.dframe.init_data.noise[1]))
            self.vMax_edt.setText(str(self.data.dframe.init_data.velocity[0]))
            self.vMin_edt.setText(str(self.data.dframe.init_data.velocity[1]))
            self.vstep.setText(str(self.data.dframe.init_data.vstep))


            self.dsgsh.setText(str(self.data.dframe.gather.h))
            self.dsgsw.setText(str(self.data.dframe.gather.w))
            self.dsgsdpi.setText(str(self.data.dframe.gather.dpi))
            self.dsgeosh.setText(str(self.data.dframe.AquGeom.h))
            self.dsgeosw.setText(str(self.data.dframe.AquGeom.w))
            self.dsgeosdpi.setText(str(self.data.dframe.AquGeom.dpi))
            self.dsdcsh.setText(str(self.data.dframe.dispCurve.h))
            self.dsdcsw.setText(str(self.data.dframe.dispCurve.w))
            self.dsdcsdpi.setText(str(self.data.dframe.dispCurve.dpi))

            ### inversion Section ####
            self.isdcch.setText(str(self.data.iframe.dispCurve.h))
            self.isdccw.setText(str(self.data.iframe.dispCurve.w))
            self.isdccdpi.setText(str(self.data.iframe.dispCurve.dpi))
            self.ismch.setText(str(self.data.iframe.misfit.h))
            self.ismcw.setText(str(self.data.iframe.misfit.w))
            self.ismcdpi.setText(str(self.data.iframe.misfit.dpi))
            self.isfmch.setText(str(self.data.iframe.model.h))
            self.isfmcw.setText(str(self.data.iframe.model.w))
            self.isfmcdpi.setText(str(self.data.iframe.model.dpi))
            self.is2dmch.setText(str(self.data.rframe.h))
            self.is2dmcw.setText(str(self.data.rframe.w))
            self.is2dmcdpi.setText(str(self.data.rframe.dpi))







            



        except:
            print("File not found")

    

    