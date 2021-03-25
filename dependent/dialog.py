from UI.extendPeak import Ui_Dialog
from PyQt5.QtWidgets import *
import sys

class InputDailog(QDialog,Ui_Dialog):
    def __init__(self,*args,**kwargs):
        super(InputDailog, self).__init__(*args,**kwargs)
        self.setupUi(self)
        self.retranslateUi(self)
        self.setMore()
        self.setEvent()

    def setMore(self):
        self.checkOK = False

    def setEvent(self):
        self.pushButton_OK.clicked.connect(self.pushbutton_OK_event)

    def pushbutton_OK_event(self):
        self.checkOK = True
        self.close()

    @staticmethod
    def openDialog():
        dialog = InputDailog()
        dialog.exec_()
        return dialog.checkOK, dialog.doubleSpinBox.value()

if __name__ == '__main__':
    app=QApplication(sys.argv)
    win=InputDailog()
    #win.addPeakInfo("U*",369.3,0.0225)
    win.show()
    sys.exit(app.exec_())