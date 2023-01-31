from PyQt5.QtWidgets import QMainWindow 
from plugin.manualPick import Ui_MainWindow as Ui_manpk


class ManPick(QMainWindow, Ui_manpk):
    def __init__(self, parent=None):
        super(ManPick, self).__init__(parent)
        self.setupUi(self)