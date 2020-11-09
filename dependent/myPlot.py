import pyqtgraph as pg
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore

class mainPlot(pg.PlotItem):
    def __init__(self,*args):
        super(mainPlot, self).__init__(*args)
        self.setMore()

    def setMore(self):
        self.showGrid()

