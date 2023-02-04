from plugin.setModel import Ui_setModelWin
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QHeaderView, QFileDialog 
import os
import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from multiprocessing import Process
from res.threads import ModelPlots
from PyQt5 import QtWidgets, QtGui
import time

filename = "log/settings.json"
def getrootdir():
    try:
        with open(filename, "r") as f:
            root = json.load(f)["gframe"]["rootdir"]
            f.close()
            if root is not None:
                return root
            else:
                return os.path.expanduser('~')            
    except:
        return os.path.expanduser('~')
    
def getpath():
    path = getrootdir()
    if not os.path.exists(path):
        os.mkdir(path)
    path+="/initmodel"
    if not os.path.exists(path):
        os.mkdir(path)
    return path

def calcPR(vp, vs):
    return np.around((vp**2 - (2*vs)**2)/(2*(vp**2 - vs**2)), 5)


class SetModel(QMainWindow, Ui_setModelWin):
    def __init__(self, parent=None,  nlayer=1):
        super(SetModel, self).__init__(parent)
        self.setupUi(self)

        self.n = nlayer
        self.tableWidget.setRowCount(self.n*5)
        self.initmodelparam()
        self.tableWidget.horizontalHeader()
        header = self.tableWidget.horizontalHeader()       
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        self.open.clicked.connect(self.ChooseFile)
        self.SaveAndClose.clicked.connect(self.Save)
        self.set.clicked.connect(self.SetData)
        self.displayplots_btn.clicked.connect(self.displayPlots)
        self.autofill_btn.clicked.connect(self.autoFill)
        
    def ChooseFile(self):
        self.filePaths, type = QFileDialog.getOpenFileName(self,"Select file", 
                                getrootdir(),"csv files (*.csv);;MS Excel Worksheet (*.xlsx)")
        self.open.setText(self.filePaths.split("/")[-1])
        if "(*.csv)" in type:
            self.dataFrame = pd.read_csv(self.filePaths)
        elif "(*.xlsx)" in type:
            self.dataFrame = pd.read_excel(self.filePaths)

        else:
            self.dataFrame = None
        if self.dataFrame is not None and len(self.dataFrame.columns.values)==8 :
            self.SetData()
            time.sleep(0.005)
            #self.displayPlots()
            


    def Save(self):
        path = getpath()
        model = dict()
        for i, key in enumerate(["z", "vp", "vs", "rh", "nu"]):
            model.update({key : [self.inflist[i], self.suplist[i]]})
        jobj = json.dumps(model)
        try:
            with open(path+"/model_params.json", "w") as f:
                f.write(jobj)
                f.close()
            self.statusbar.setStyleSheet("color: green")
            self.statusbar.showMessage("New data recorded")
        except:
            self.statusbar.setStyleSheet("color: red")
            self.statusbar.showMessage("Data record unsuccessful!!")

    def SetData(self):

        if self.dataFrame is not None:
            
            if len(self.dataFrame.columns.values)==8 :
                header = ["zinf", "zsup", "vpinf", "vpsup", "vsinf", "vssup", "rhinf", "rhsup"]
                self.filter(header)

            elif len(self.dataFrame.columns.values)==4:
                if "," in self.lineEdit.text():
                    ebs = np.array(list(map(float, self.lineEdit.text().split(","))))
                else:
                    ebs = np.ones(4) * float(self.lineEdit.text())

                if np.all(ebs) > 0.0:
                    header=["z", "vp", "vs", "rh"]
                    self.filter(header, ebs=ebs)

                else:
                    self.statusbar.setStyleSheet("color: red")
                    self.statusbar.showMessage("*** Error bound should be greater than Zero % *****")

                #print("format 2")
        
        else:
            self.statusbar.setStyleSheet("color: red")
            self.statusbar.showMessage("*** Parameter file is not selected *****")


    def filter(self, header, ebs=np.array([])):

        inflist = []
        suplist=[]
        if ebs.size:
            for eb, key in zip(ebs, header):
                if key!='-Z':
                    inflist.append(self.dataFrame[key].to_numpy() * (100 - eb)/100)
                    suplist.append(self.dataFrame[key].to_numpy() * (100 + eb)/100)
                else:
                    inflist.append(self.dataFrame[key].to_numpy() * (100 + eb)/100)
                    suplist.append(self.dataFrame[key].to_numpy() * (100 - eb)/100)
        else:
            for key in header:
                if "inf" in key: inflist.append(self.dataFrame[key].to_numpy())
                elif "sup" in key: suplist.append(self.dataFrame[key].to_numpy())

            
        inflist.append(calcPR(inflist[1], inflist[2]))
        suplist.append(calcPR(suplist[1], suplist[2]))

        k=0
        for i in range(5):
            for j in range(0, self.n):
                self.tableWidget.setItem(k,1, QTableWidgetItem(f"{inflist[i][j]}"))
                self.tableWidget.setItem(k,2, QTableWidgetItem(f"{suplist[i][j]}"))
                k+=1


            


    def autoFill(self):

        pass

    def initmodelparam(self):
        listitem = ["-Z", "VP", "VS", "RH", "PR"]
        keylist=[]
        k=0
        for key in listitem:
            for i in range(self.n):
                self.tableWidget.setItem(k,0, QTableWidgetItem(f"{key}{i+1}    "))
                keylist.append(f"{key}{i+1}")
                k+=1
    
    


    def displayPlots(self):
        path = getpath()  
        self.inflist = []
        self.suplist = []
        k=0
        for i in range(5):
            inf = []
            sup = []
            for j in range(self.n):           
                inf.append(float(self.tableWidget.item(k, 1).text()))
                sup.append(float(self.tableWidget.item(k, 2).text()))
                k+=1


            self.inflist.append(inf)
            self.suplist.append(sup)
        #print(self.inflist, self.suplist)
        
        self.mp = ModelPlots(suplist=self.suplist, inflist=self.inflist, path=path)
        self.mp.start()
        self.mp.setter.connect(self.setplot)
        self.mp.thread_msg.connect(self.statusbar.showMessage)
        


    def setplot(self, i, fname):
        program = f"self.modelPlotlabel{i} = QtWidgets.QLabel(\"mlabel_{i}\", self.sa_{i});\npixmap = QtGui.QPixmap(r\"{fname}\");\nself.modelPlotlabel{i}.setPixmap(pixmap);\nself.hl{i}.addWidget(self.modelPlotlabel{i});\nself.modelPlotlabel{i}.show();"
        exec(program)




def plotter():
        pass





