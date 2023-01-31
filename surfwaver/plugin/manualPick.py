# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'manualPick.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 596)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setMaximumSize(QtCore.QSize(16777215, 51))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 780, 49))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.Dright = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.Dright.setGeometry(QtCore.QRect(195, 10, 31, 31))
        self.Dright.setMinimumSize(QtCore.QSize(0, 31))
        self.Dright.setMaximumSize(QtCore.QSize(31, 16777215))
        self.Dright.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/nxt.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Dright.setIcon(icon)
        self.Dright.setIconSize(QtCore.QSize(20, 20))
        self.Dright.setObjectName("Dright")
        self.loca_edt = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
        self.loca_edt.setGeometry(QtCore.QRect(104, 10, 85, 31))
        self.loca_edt.setMinimumSize(QtCore.QSize(0, 31))
        self.loca_edt.setMaximumSize(QtCore.QSize(120, 31))
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setPointSize(12)
        self.loca_edt.setFont(font)
        self.loca_edt.setStyleSheet("background:rgb(255, 255, 255)")
        self.loca_edt.setObjectName("loca_edt")
        self.Dleft = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.Dleft.setGeometry(QtCore.QRect(67, 10, 31, 31))
        self.Dleft.setMinimumSize(QtCore.QSize(0, 31))
        self.Dleft.setMaximumSize(QtCore.QSize(31, 16777215))
        self.Dleft.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("icons/prv.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Dleft.setIcon(icon1)
        self.Dleft.setIconSize(QtCore.QSize(20, 20))
        self.Dleft.setObjectName("Dleft")
        self.label_17 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_17.setGeometry(QtCore.QRect(10, 10, 51, 31))
        self.label_17.setWordWrap(True)
        self.label_17.setObjectName("label_17")
        self.pushButton = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.pushButton.setGeometry(QtCore.QRect(250, 10, 75, 31))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.pushButton_2.setGeometry(QtCore.QRect(330, 10, 75, 31))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.pushButton_3.setGeometry(QtCore.QRect(410, 10, 95, 31))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_4 = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.pushButton_4.setGeometry(QtCore.QRect(510, 10, 75, 31))
        self.pushButton_4.setObjectName("pushButton_4")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setObjectName("graphicsView")
        self.verticalLayout.addWidget(self.graphicsView)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.Dright.setToolTip(_translate("MainWindow", "<html><head/><body><p>Next location</p></body></html>"))
        self.Dleft.setToolTip(_translate("MainWindow", "<html><head/><body><p>Previous location</p></body></html>"))
        self.label_17.setText(_translate("MainWindow", "CMP/Shot location"))
        self.pushButton.setText(_translate("MainWindow", "Save"))
        self.pushButton_2.setText(_translate("MainWindow", "Add Points"))
        self.pushButton_3.setText(_translate("MainWindow", "Remove Points"))
        self.pushButton_4.setText(_translate("MainWindow", "Save All"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())