#!/usr/bin/env python3
import time
import sys
import pandas as pd
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import *
from dependent.avaspec import *
from dependent import globals
from dependent.Analyse import *
import os
from UI import mainWindow


class onlineWindow(QMainWindow, mainWindow.Ui_MainWindow):
    newdata = pyqtSignal()

    def __init__(self,*args):
        super(onlineWindow, self).__init__(*args)
        self.setupUi(self)
        self.IntTimeEdt.setText("{:3.1f}".format(5.0))
        self.NumAvgEdt.setText("{0:d}".format(1))
        self.NumMeasEdt.setText("{0:d}".format(1))
        self.StartMeasBtn.setEnabled(False)
        self.VersionBtn.setEnabled(False)
        #       self.OpenCommBtn.clicked.connect(self.on_OpenCommBtn_clicked)
        #       do not use explicit connect together with the on_ notation, or you will get
        #       two signals instead of one!
        self.newdata.connect(self.handle_newdata)

    @pyqtSlot()
    #   if you leave out the @pyqtSlot() line, you will also get an extra signal!
    #   so you might even get three!
    def on_OpenCommBtn_clicked(self):
        ret = AVS_Init(0)
        # QMessageBox.information(self,"Info","AVS_Init returned:  {0:d}".format(ret))
        ret = AVS_GetNrOfDevices()
        # QMessageBox.information(self,"Info","AVS_GetNrOfDevices returned:  {0:d}".format(ret))
        req = 0
        mylist = AvsIdentityType * 1
        ret = AVS_GetList(75, req, mylist)
        serienummer = str(ret[1].SerialNumber.decode("utf-8"))
        QMessageBox.information(self, "Info", "Found Serialnumber: " + serienummer)
        globals.dev_handle = AVS_Activate(ret[1])
        # QMessageBox.information(self,"Info","AVS_Activate returned:  {0:d}".format(globals.dev_handle))
        devcon = DeviceConfigType
        reqsize = 0
        ret = AVS_GetParameter(globals.dev_handle, 63484, reqsize, devcon)
        globals.pixels = ret[1].m_Detector_m_NrPixels
        ret = AVS_GetLambda(globals.dev_handle, globals.wavelength)
        x = 0
        while (x < globals.pixels):  # 0 through 2047
            globals.wavelength[x] = ret[x]
            x += 1
        self.StartMeasBtn.setEnabled(True)
        self.VersionBtn.setEnabled(True)
        return

    @pyqtSlot()
    def on_CloseCommBtn_clicked(self):
        callbackclass.callback(self, 0, 0)
        return

    @pyqtSlot()
    def on_VersionBtn_clicked(self):
        FPGAver = bytes(VERSION_LEN)
        FWver = bytes(VERSION_LEN)
        DLLver = bytes(VERSION_LEN)
        ret = AVS_GetVersionInfo(globals.dev_handle, FPGAver, FWver, DLLver)
        FPGAver = ret[0]
        FWver = ret[1]
        DLLver = ret[2]
        QMessageBox.information(self, "Info", "FPGA version: {FPGA} \nFirmware version: {FW} \nDLL version: {DLL}" \
                                .format(FPGA=FPGAver.value.decode('utf-8'),
                                        FW=FWver.value.decode('utf-8'),
                                        DLL=DLLver.value.decode('utf-8')))
        return

    @pyqtSlot()
    def on_StartMeasBtn_clicked(self):
        ret = AVS_UseHighResAdc(globals.dev_handle, True)
        measconfig = MeasConfigType
        measconfig.m_StartPixel = 0
        measconfig.m_StopPixel = globals.pixels - 1
        measconfig.m_IntegrationTime = float(self.IntTimeEdt.text())
        measconfig.m_IntegrationDelay = 0
        measconfig.m_NrAverages = int(self.NumAvgEdt.text())
        measconfig.m_CorDynDark_m_Enable = 0  # nesting of types does NOT work!!
        measconfig.m_CorDynDark_m_ForgetPercentage = 0
        measconfig.m_Smoothing_m_SmoothPix = 0
        measconfig.m_Smoothing_m_SmoothModel = 0
        measconfig.m_SaturationDetection = 0
        measconfig.m_Trigger_m_Mode = 0
        measconfig.m_Trigger_m_Source = 0
        measconfig.m_Trigger_m_SourceType = 0
        measconfig.m_Control_m_StrobeControl = 0
        measconfig.m_Control_m_LaserDelay = 0
        measconfig.m_Control_m_LaserWidth = 0
        measconfig.m_Control_m_LaserWaveLength = 0.0
        measconfig.m_Control_m_StoreToRam = 0
        ret = AVS_PrepareMeasure(globals.dev_handle, measconfig)
        nummeas = int(self.NumMeasEdt.text())

        # to use Windows messages, supply a window handle to send the messages to
        # ret = AVS_Measure(globals.dev_handle, int(self.winId()), nummeas)
        # single message sent from DLL, confirmed with Spy++

        # when using polling, just pass a 0 for the windows handle
        scans = 0
        while (scans < nummeas):
            ret = AVS_Measure(globals.dev_handle, 0, 1)
            dataready = False
            while (dataready == False):
                dataready = (AVS_PollScan(globals.dev_handle) == True)
                time.sleep(0.001)
            if dataready == True:
                scans = scans + 1
                self.newdata.emit()
        return

    @pyqtSlot()
    def on_StopMeasBtn_clicked(self):
        ret = AVS_StopMeasure(globals.dev_handle)
        return

    # def nativeEvent(self, eventType, message):
    #    msg = ctypes.wintypes.MSG.from_address(message.__int__())
    #    if eventType == "windows_generic_MSG":
    #        if msg.message == WM_MEAS_READY:
    #            # print("Message Received!")
    #            self.newdata.emit()
    #    return False, 0

    @pyqtSlot()
    def handle_newdata(self):
        timestamp = 0
        ret = AVS_GetScopeData(globals.dev_handle, timestamp, globals.spectraldata)
        timestamp = ret[0]
        x = 0
        while (x < globals.pixels):  # 0 through 2047
            globals.spectraldata[x] = ret[1][x]
            x += 1
            # QMessageBox.information(self,"Info","Received data")
        self.plot.update()
        return

class MainWindow(onlineWindow):
    def __init__(self,*args):
        super(MainWindow, self).__init__(*args)
        self.setMore()
        self.setEvent()

    #=============处理在线部分的按钮事件报错=============
    @pyqtSlot()
    def on_OpenCommBtn_clicked(self):
        try:
            super(MainWindow, self).on_OpenCommBtn_clicked()
        except:
            from traceback import print_exc
            print_exc()
            QMessageBox.information(self,"information","The device doesn't seem to be properly connected.")

    @pyqtSlot()
    def on_CloseCommBtn_clicked(self):
        try:
            super(MainWindow, self).on_CloseCommBtn_clicked()
        except:
            QMessageBox.information(self,"information","The device doesn't seem to be properly connected.")

    @pyqtSlot()
    def on_StopMeasBtn_clicked(self):
        try:
            super(MainWindow, self).on_StopMeasBtn_clicked()
        except:
            QMessageBox.information(self,"information","The device doesn't seem to be properly connected.")

    #=============离线模式部分=============
    def setMore(self):
        self.pushButton_asdColor.setColor(pg.mkColor("r"))
        self.pushButton_mearsureColor.setColor(pg.mkColor("b"))
        self.asdData = pd.DataFrame()
        self.measureData = pd.DataFrame()
        self.initializePlot()
        self.initializePeakItem()

    def setEvent(self):
        # ----asd----
        self.pushButton_asdInput.clicked.connect(self.on_pushButton_asdInput_Clicked)
        self.pushButton_asdColor.sigColorChanged.connect(self.on_pushButton_asdColor_Clicked)
        self.doubleSpinBox_asdThreshold.valueChanged.connect(self.asdPlotDataUpdate)
        self.doubleSpinBox_asdTranslate.valueChanged.connect(self.on_doubleSpinBox_asdTranslate_ValueChange)
        self.horizontalSlider_asdTranslate.valueChanged.connect(self.on_horizontalSlider_asdTranslate_ValueChange)
        self.checkBox_asdShow.clicked.connect(self.on_checkBox_asdShow_Checked)
        self.doubleSpinBox_asdDamping.valueChanged.connect(self.asdPlotDataUpdate)
        # ----实测----
        self.pushButton_measureInput.clicked.connect(self.on_pushButton_meaarsuredInput_Clicked)
        self.pushButton_mearsureColor.sigColorChanged.connect(self.on_pushButton_measureColor_Clicked)
        self.doubleSpinBox_measureTranslate.valueChanged.connect(self.on_doubleSpinBox_measureTranslate_ValueChange)
        self.horizontalSlider_measureTranslate.valueChanged.connect(self.on_horizontalSlider_measureTranslate_ValueChange)
        self.checkBox_mearsureShow.clicked.connect(self.on_checkBox_mearsureShow_Checked)
        self.doubleSpinBox_measureSmothingFactor.valueChanged.connect(self.on_doubleSpinBox_measureSmothingFactor_ValueChange)
        # ----zoomBar----
        self.doubleSpinBox_measureThreshold.valueChanged.connect(self.measuredPlotDataUpdate)
        self.doubleSpinBox_zoomDown.valueChanged.connect(self.spinBoxRengeChange_event)
        self.partPlot.sigXRangeChanged.connect(self.partPlotRegionChange_event)
        self.zoomBar.sigRegionChanged.connect(self.zoomBarChange_event)
        # -----peakItem----
        self.checkBox_showCharacteristicPeak.clicked.connect(self.showPeackItem)
        self.doubleSpinBox_peakThreshold.valueChanged.connect(self.on_doubleSpinBox_peakThreshold_ValueChange)

    #--------------asd数据---------------
    @pyqtSlot()
    # 工具栏事件：导入asd数据
    def on_pushButton_asdInput_Clicked(self):
        path,fileType = QFileDialog.getOpenFileName(parent=self,caption="open ASD data",
                                                    directory=os.path.expanduser("~"),filter="ASDdata (*.txt *.csv)")
        if path != '':
            self.asdData_raw = pd.read_csv(path,header=0,sep="\s+")
            # 预处理-将低于0的值置零，然后归一化
            data = replaceZeroFromThreshold(self.asdData_raw, 0.)
            self.asdData = countTranslateTontensityI(data)
            self.asdPlotDataUpdate()
            self.resetZoomBarSet()

    @pyqtSlot()
    # 工具栏事件：切换asd曲线的颜色
    def on_pushButton_asdColor_Clicked(self):
        self.measureItem_main.setPen(pg.mkPen(self.pushButton_asdColor.color()))
        self.measureItem_part.setPen(pg.mkPen(self.pushButton_asdColor.color()))

    @pyqtSlot(int)
    # 工具栏事件：asd曲线平移-滑动条
    def on_horizontalSlider_asdTranslate_ValueChange(self,a0: int):
        # 滑动条只有整数，所以范围设置为-300~300，对应-3.00~3.00
        self.doubleSpinBox_asdTranslate.setValue(a0/100)
        self.asdPlotDataUpdate()

    @pyqtSlot(float)
    # 工具栏事件：asd曲线平移-数字框
    def on_doubleSpinBox_asdTranslate_ValueChange(self,a0: float):
        # 滑动条只有整数，所以范围设置为-300~300，对应-3.00~3.00
        self.horizontalSlider_asdTranslate.setValue(int(a0*100))
        self.asdPlotDataUpdate()

    @pyqtSlot(bool)
    # 工具栏事件：显示/隐藏asd曲线
    def on_checkBox_asdShow_Checked(self, a0: bool):
        if a0:
            self.mainPlot.addItem(self.asdItem_main)
            self.partPlot.addItem(self.asdItem_part)
        else:
            self.mainPlot.removeItem(self.asdItem_main)
            self.partPlot.removeItem(self.asdItem_part)

    #------------实测数据----------------
    @pyqtSlot()
    # 工具栏事件：导入实测数据
    def on_pushButton_meaarsuredInput_Clicked(self):
        path,fileType = QFileDialog.getOpenFileName(parent=self,caption="open measured data",
                                                    directory="./",filter="MeasuredData (*.txt *.csv)")
        if path != '':
            self.measureData_raw = pd.read_csv(path,header=0,sep="\s+")
            self.pretreatment() # 数据预处理
            self.measuredPlotDataUpdate()
            self.resetZoomBarSet()

    @pyqtSlot()
    # 工具栏事件：切换实测曲线的颜色
    def on_pushButton_measureColor_Clicked(self):
        self.measureItem_main.setPen(pg.mkPen(self.pushButton_mearsureColor.color()))
        self.measureItem_part.setPen(pg.mkPen(self.pushButton_mearsureColor.color()))

    @pyqtSlot(int)
    # 工具栏事件：实测曲线平移-滑动条
    def on_horizontalSlider_measureTranslate_ValueChange(self,a0: int):
        # 滑动条只有整数，所以范围设置为-300~300，对应-3.00~3.00
        self.doubleSpinBox_measureTranslate.setValue(a0/100)
        self.measuredPlotDataUpdate()

    @pyqtSlot(float)
    # 工具栏事件：实测曲线平移-数字框
    def on_doubleSpinBox_measureTranslate_ValueChange(self,a0: float):
        # 滑动条只有整数，所以范围设置为-300~300，对应-3.00~3.00
        self.horizontalSlider_measureTranslate.setValue(int(a0*100))
        self.measuredPlotDataUpdate()

    @pyqtSlot(bool)
    # 工具栏事件：显示/隐藏实测曲线
    def on_checkBox_mearsureShow_Checked(self,a0: bool):
        if a0:
            self.mainPlot.addItem(self.measureItem_main)
            self.partPlot.addItem(self.measureItem_part)
        else:
            self.mainPlot.removeItem(self.measureItem_main)
            self.partPlot.removeItem(self.measureItem_part)

    @pyqtSlot()
    # 工具栏事件：平滑系数更改
    def on_doubleSpinBox_measureSmothingFactor_ValueChange(self):
        self.pretreatment()
        self.measuredPlotDataUpdate()

    #--------------图像更新------------
    @pyqtSlot()
    #更新实测图像数据
    def measuredPlotDataUpdate(self):
        # 数据平移
        data = moveWaveLength(self.measureData,self.doubleSpinBox_measureTranslate.value())
        # 4.寻峰
        self.peakPointUpdate(data)
        # 将小于阈值的置零
        underThreshold = replaceZeroFromThreshold(data,self.doubleSpinBox_measureThreshold.value())
        xData = underThreshold[Index[0]].values
        yData = underThreshold[Index[1]].values
        # 导入图像
        self.measureItem_main.setData(x=xData,y=yData,pen=pg.mkPen(self.pushButton_mearsureColor.color()))
        self.measureItem_part.setData(x=xData,y=yData,pen=pg.mkPen(self.pushButton_mearsureColor.color()))
        # 绘制峰标签
        if self.checkBox_showCharacteristicPeak.isChecked():
            self.showPeackItem()

    @pyqtSlot()
    # 更新ASD图像数据
    def asdPlotDataUpdate(self):
        # 数据平移
        data = moveWaveLength(self.asdData,self.doubleSpinBox_asdTranslate.value())
        # 将小于阈值的置零
        underThreshold = replaceZeroFromThreshold(data,self.doubleSpinBox_asdThreshold.value()/self.doubleSpinBox_asdDamping.value())
        # asd数据强度作10倍衰减
        xData = underThreshold[Index[0]].values + self.doubleSpinBox_asdTranslate.value()
        yData = underThreshold[Index[1]].values * self.doubleSpinBox_asdDamping.value()
        # 导入图像
        self.asdItem_main.setData(x=xData, y=yData, pen=pg.mkPen(self.pushButton_asdColor.color()))
        self.asdItem_part.setData(x=xData, y=yData, pen=pg.mkPen(self.pushButton_asdColor.color()))

    #---------绘图小部件事件----------
    @pyqtSlot()
    # zoomBar:当zoomBar改变时
    def zoomBarChange_event(self):
        range = self.zoomBar.getRegion()
        self.partPlot.setXRange(*range,padding=0)
        self.doubleSpinBox_zoomUp.setValue(range[0])
        self.doubleSpinBox_zoomDown.setValue(range[1])

    @pyqtSlot()
    # zoomBar:当partPlot范围改变时
    def partPlotRegionChange_event(self):
        range = self.partPlot.getViewBox().viewRange()[0]
        self.zoomBar.setRegion(range)
        self.doubleSpinBox_zoomUp.setValue(range[0])
        self.doubleSpinBox_zoomDown.setValue(range[1])

    @pyqtSlot()
    # zoomBar:当工具栏中的范围框改变时
    def spinBoxRengeChange_event(self):
        range = [self.doubleSpinBox_zoomUp.value(),self.doubleSpinBox_zoomDown.value()]
        if range[1] - range[0] < 0.1:
            range[1] = range[0] + 0.1
        self.doubleSpinBox_zoomDown.setValue(range[1])
        self.partPlot.setXRange(*range,padding=0)
        self.zoomBar.setRegion(range)

    @pyqtSlot(bool)
    # peakItem:隐藏/显示特征峰部件（从plot中删除)
    def showPeackItem(self,show:bool = True):
        if show:
            for text in self.peakItems_main:
                self.mainPlot.addItem(text)
            for text in self.peakItems_part:
                self.partPlot.addItem(text)
        else:
            for text in self.peakItems_main:
                self.mainPlot.removeItem(text)
            for text in self.peakItems_part:
                self.partPlot.removeItem(text)

    @pyqtSlot()
    # peakItem:调整寻峰阈值
    def on_doubleSpinBox_peakThreshold_ValueChange(self):
        self.peakPointUpdate()
        if self.checkBox_showCharacteristicPeak.isChecked():
            self.showPeackItem()

    # --------------------------------
    # 辅助函数：初始化图像控件
    def initializePlot(self):
        # 初始化上下两个图像
        self.plot_offline.setBackground("w")
        self.mainPlot: pg.PlotItem = self.plot_offline.addPlot(title="Libs spectrum",bottom="wave length(nm)",left="intensity")
        self.mainPlot.showGrid(x=True,y=True)
        self.plot_offline.nextRow()
        self.partPlot: pg.PlotItem = self.plot_offline.addPlot(bottom="wave length(nm)",left="intensity")
        self.partPlot.showGrid(x=True,y=True)
        # 初始化测量数据和asd数据元素
        self.measureItem_main = pg.PlotDataItem()
        self.asdItem_main = pg.PlotDataItem()
        self.mainPlot.addDataItem(self.measureItem_main)
        self.mainPlot.addDataItem(self.asdItem_main)
        self.measureItem_part = pg.PlotDataItem()
        self.asdItem_part = pg.PlotDataItem()
        self.partPlot.addItem(self.measureItem_part)
        self.partPlot.addItem(self.asdItem_part)
        # 初始化ZoomBar
        self.zoomBar = pg.LinearRegionItem([0,100])
        self.zoomBar.setZValue(-10)
        self.mainPlot.addItem(self.zoomBar)

    # 辅助函数：初始化特征峰部件
    def initializePeakItem(self):
        self.peakItems_main = []     #由元组(textItem)组成
        self.peakItems_part = []     #由元组(textItem)组成

    # 辅助函数：计算获取特征峰位置
    def peakPointUpdate(self,data:pd.DataFrame = None):
        if data is None:
            data = moveWaveLength(self.measureData, self.doubleSpinBox_measureTranslate.value())
        self.showPeackItem(False)
        self.peakItems_main.clear()
        self.peakItems_part.clear()
        self.tableWidget_peak.clear()
        # 对于重点特征峰
        for peakKey in Peak.keys():
            for peakWave in Peak.get(peakKey,[]):
                peakPoint = findPeak(peakWave,data,threshold=self.doubleSpinBox_peakThreshold.value())
                if peakPoint is not None:
                    text_main = pg.TextItem("{}".format(peakKey),angle=0,color=pg.mkColor("k"))
                    text_main.setPos(*peakPoint)
                    self.peakItems_main.append(text_main)
                    text_part = pg.TextItem("{}({:.2f}nm,{:.2%})".format(peakKey,*peakPoint),angle=90,color=pg.mkColor("k"))
                    text_part.setPos(*peakPoint)
                    self.peakItems_part.append(text_part)
                    if peakKey == "U*":
                        peakRange = findPeakRange(self.measureData,peakPoint[0])
                        peakArea = calculateArea(self.measureData.loc[peakRange[0]:peakRange[1]])
                        self.tableWidget_peak.addPeakInfo(peakKey,peakPoint[0],peakArea/self.allArea)

    # 辅助函数：重新设置zoomBar位置
    def resetZoomBarSet(self):
        # 设置新的ZoomBar范围
        length = self.mainPlot.getViewBox().viewRange()[0][1] - self.mainPlot.getViewBox().viewRange()[0][0]
        region = [self.mainPlot.getViewBox().viewRange()[0][0] + length / 3,
                  self.mainPlot.getViewBox().viewRange()[0][1] - length / 3]
        self.zoomBar.setRegion(region)

    # 辅助函数：实测数据预处理
    def pretreatment(self):
        # 1.降噪
        data = reduceNoise(self.measureData_raw,self.doubleSpinBox_measureSmothingFactor.value())
        print(self.doubleSpinBox_measureSmothingFactor.value())
        # 2.去除本底
        data = backgroundSubraction(data)
        # 3.小于零的值置零
        data = replaceZeroFromThreshold(data, 0.)
        # 4.归一化
        self.measureData = countTranslateTontensityI(data)
        # 5.计算谱面积
        self.allArea = calculateArea(self.measureData)




def main():
    app = QApplication(sys.argv)
    app.lastWindowClosed.connect(app.quit)
    app.setApplicationName("PyQt5 simple demo")
    form = MainWindow()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
