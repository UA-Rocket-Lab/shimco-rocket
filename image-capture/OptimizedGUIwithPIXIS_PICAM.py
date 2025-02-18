# -*- coding: utf-8 -*-
"""
Created on Wed Jan  1 19:28:32 2025

@author: hayde
"""

from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
import threading
import time
import matplotlib
import datetime
import os

# Eliminate Extra Figure
matplotlib.use('Qt5Agg')
plt.ioff() 

# Initialize Camera
from PIXIS_PICAM_Initialization import *



class CaptureSeriesThread(QThread):
    update_image = pyqtSignal(np.ndarray)

    def __init__(self, series, parent=None):
        super().__init__(parent)
        self.series = series

    def run(self):
        for command in self.series:
            if len(command) == 1:
                time.sleep(command[0])
            else:
                num_exposures, exposure_time, target_name = command
                for exposure in range(num_exposures):
                    cam1.set_attribute_value('Exposure Time', int(exposure_time))
                    image = cam1.grab(1)
                    self.update_image.emit(image)
                    
                    # File Saving
                    target = target_name.strip().replace(" ", "_")
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    filename = f"{target}_{current_time}"    
                    file_path = os.path.join("C:\\Users\\Owner\\PICAM\\images", filename)
                    image.tofile(file_path + '.bin')
                    

class Ui_Form(object):
    def setupUi(self, Form):
        self.Form = Form
        Form.setObjectName("Form")
        Form.resize(1100, 1000)
        
        # Parameters Label
        self.Pt = QtWidgets.QLabel(Form)
        self.Pt.setGeometry(QtCore.QRect(35, 10, 130, 30))
        self.Pt.setObjectName("Pt")
        self.Pt.setText("Parameters")
        self.Pt.setStyleSheet("font-size: 24px;")
        
        # Image Capture Label
        self.IC = QtWidgets.QLabel(Form)
        self.IC.setGeometry(QtCore.QRect(35, 310, 170, 30))
        self.IC.setText("Image Capture")
        self.IC.setStyleSheet("font-size: 24px;")
        
        # Pause Button
        self.pauseButton = QtWidgets.QPushButton(Form)
        self.pauseButton.setGeometry(QtCore.QRect(35, 430, 170, 50))
        self.pauseButton.setObjectName("pause")
        self.pauseButton.setText("Pause")
        self.pauseButton.setStyleSheet("font-size: 16px;")
        self.pauseButton.clicked.connect(self.pauseCapture)
        self.pauseButton.setEnabled(False)
        
        # Resume Button
        self.resumeButton = QtWidgets.QPushButton(Form)
        self.resumeButton.setGeometry(QtCore.QRect(35, 360, 170, 50))
        self.resumeButton.setObjectName("resume")
        self.resumeButton.setText("Start")
        self.resumeButton.clicked.connect(self.resumeCapture)
        self.resumeButton.setStyleSheet("font-size: 16px;")
        
        # Stop Button
        self.stopButton = QtWidgets.QPushButton(Form)
        self.stopButton.setGeometry(QtCore.QRect(35, 500, 170, 50))
        self.stopButton.setObjectName("stopButton")
        self.stopButton.setText("Close")
        self.stopButton.setStyleSheet("font-size: 16px;")
        
        # Set Value Button
        self.setValues = QtWidgets.QPushButton(Form)
        self.setValues.setGeometry(QtCore.QRect(850, 160, 150, 65))
        self.setValues.setObjectName("setvalues")
        self.setValues.setText("Set Values")
        self.setValues.setStyleSheet("font-size: 16px;")
        
        # Target Textbox
        self.Target = QtWidgets.QLineEdit(Form)
        self.Target.setGeometry(QtCore.QRect(85, 190, 100, 30))
        self.Target.setObjectName("Target_Name")
        self.Target.setText("None")
        self.Target.setStyleSheet("font-size: 14px;")
        
        # Capture Loop Parameters Textbox
        self.Param = QtWidgets.QTextEdit(Form)
        self.Param.setGeometry(QtCore.QRect(35, 585, 300, 200))
        self.Param.setObjectName("Capture Parameters")
        self.Param.setText("add delay 3\n5 120 HeNe_darks_120s")
        self.Param.setStyleSheet("font-size: 14px;")
        
        # Example Series
        self.Cap1 = QtWidgets.QPushButton(Form)
        self.Cap1.setGeometry(QtCore.QRect(35, 810, 140, 60))
        self.Cap1.setObjectName("cap1")
        self.Cap1.setText("Example Series")
        self.Cap1.setStyleSheet("font-size: 14px;")
        # self.Cap1.clicked.connect(self.Capture Function)
        
        # Capture Button
        self.Cap2 = QtWidgets.QPushButton(Form)
        self.Cap2.setGeometry(QtCore.QRect(195, 810, 140, 60))
        self.Cap2.setObjectName("cap1")
        self.Cap2.setText("Execute Series")
        self.Cap2.setStyleSheet("font-size: 14px;")
        self.Cap2.clicked.connect(self.ExecuteSeries)
        
        # Exposure Spinbox
        self.Exposure = QtWidgets.QSpinBox(Form)
        self.Exposure.setGeometry(QtCore.QRect(355, 190, 60, 30))
        self.Exposure.setObjectName("Exposure Time")
        self.Exposure.setMaximum(10000)
        self.Exposure.setValue(10)
        self.Exposure.setStyleSheet("font-size: 14px;")
        
        # Temperature Spinbox
        self.Temperature = QtWidgets.QSpinBox(Form)
        self.Temperature.setGeometry(QtCore.QRect(650, 190, 60, 30))
        self.Temperature.setObjectName("Temperature")
        self.Temperature.setMaximum(10000) 
        self.Temperature.setMinimum(-100)
        self.Temperature.setValue(-70)  
        self.Temperature.setStyleSheet("font-size: 14px;")

        # Current Target Label
        self.Tg = QtWidgets.QLabel(Form)
        self.Tg.setGeometry(QtCore.QRect(80, 70, 130, 20))
        self.Tg.setObjectName("CTg")
        self.Tg.setText("Current Target:")
        self.Tg.setStyleSheet("font-size: 16px;")        

        # Target Label
        self.Tg = QtWidgets.QLabel(Form)
        self.Tg.setGeometry(QtCore.QRect(85, 160, 130, 20))
        self.Tg.setObjectName("Tg")
        self.Tg.setText("Target Name:")
        self.Tg.setStyleSheet("font-size: 16px;")  
        
        # Current Exposure Time Label
        self.exp = QtWidgets.QLabel(Form)
        self.exp.setGeometry(QtCore.QRect(275, 70, 210, 20))
        self.exp.setObjectName("CExp")
        self.exp.setText("Current Exposure Time (ms):")
        self.exp.setStyleSheet("font-size: 16px;")
        
        # Exposure Time Label
        self.exp = QtWidgets.QLabel(Form)
        self.exp.setGeometry(QtCore.QRect(310, 160, 170, 20))
        self.exp.setObjectName("Exp")
        self.exp.setText("Exposure Time (ms):")
        self.exp.setStyleSheet("font-size: 16px;")  

        # Current Temperature Label
        self.Temp = QtWidgets.QLabel(Form)
        self.Temp.setGeometry(QtCore.QRect(580, 70, 200, 20))
        self.Temp.setObjectName("CTemp")
        self.Temp.setText("Current Temperature (°C):")
        self.Temp.setStyleSheet("font-size: 16px;")
        
        # Temperature Label
        self.Temp = QtWidgets.QLabel(Form)
        self.Temp.setGeometry(QtCore.QRect(615, 160, 150, 20))
        self.Temp.setObjectName("Temp")
        self.Temp.setText("Temperature (°C):")
        self.Temp.setStyleSheet("font-size: 16px;")  
        
        # Target Status
        self.TGS = QtWidgets.QLabel(Form)
        self.TGS.setGeometry(QtCore.QRect(115, 100, 120, 16))
        self.TGS.setObjectName("TGS")
        self.TGS.setText('None')
        self.TGS.setStyleSheet("font-size: 16px;")
        
        # Exp Status
        self.ExpS = QtWidgets.QLabel(Form)
        self.ExpS.setGeometry(QtCore.QRect(370, 100, 165, 16))
        self.ExpS.setObjectName("ExpS")
        self.ExpS.setText('10')
        self.ExpS.setStyleSheet("font-size: 16px;")
        
        # Temp Status
        self.TmpS = QtWidgets.QLabel(Form)
        self.TmpS.setGeometry(QtCore.QRect(660, 100, 155, 16))
        self.TmpS.setObjectName("TmpS")
        self.TempStatus()
        self.TmpS.setStyleSheet("font-size: 16px;")
        
        # Camera Status Label
        self.CG = QtWidgets.QLabel(Form)
        self.CG.setGeometry(QtCore.QRect(840, 10, 300, 25))
        self.CG.setObjectName("CG")
        self.updateCameraStatus()
        
        # Timer for live Updates
        self.timer = QtCore.QTimer(Form)
        self.timer.timeout.connect(self.updateCameraStatus)
        self.timer.timeout.connect(self.TempStatus)
        self.timer.start(500)
        
        # Graph
        self.graphWidget = QtWidgets.QWidget(Form)
        self.graphWidget.setGeometry(QtCore.QRect(350, 270, 700, 700))
        self.graphLayout = QtWidgets.QVBoxLayout(self.graphWidget)  
        
        # Image Display Label
        self.ID = QtWidgets.QLabel(Form)
        self.ID.setGeometry(QtCore.QRect(630, 310, 170, 30))
        self.ID.setText("Image Display")
        self.ID.setStyleSheet("font-size: 24px;")

        self.figure = plt.figure()
        self.ax = self.figure.add_subplot(111) 
        self.canvas = FigureCanvas(self.figure)
        self.graphLayout.addWidget(self.canvas)        
        self.figure.set_facecolor('#F0F0F0')  # Match PyQt GUI background
        
        # Plot appearance
        self.ax.set_xlabel("X-axis")
        self.ax.set_ylabel("Y-axis")
        self.stopButton.clicked.connect(self.stopFunction)
        self.setValues.clicked.connect(self.setFunction)
        
        self.stop = False
        self.cam_open = True
        self.paused = True
        self.TargetName = ""

        # Start the image capture thread
        self.capture_thread = threading.Thread(target=self.capture_images)
        self.capture_thread.start()
        
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def stopFunction(self):
        self.stop = True
        self.cam_open = False
        self.Form.close()
        
    def updateCameraStatus(self):
        self.CG.clear()
        if self.stop == False:
            if -72 < cam1.get_attribute_value('Sensor Temperature Reading') < -68:
                self.CG.setText("Camera is ready for Image Capture")
                self.CG.setStyleSheet("color: green; font-size: 14px;")
            else:
                self.CG.setText("Camera is not ready for Image Capture")
                self.CG.setStyleSheet("color: red; font-size: 14px;")

    
    def TempStatus(self):
        self.TmpS.setText(str(cam1.get_attribute_value('Sensor Temperature Reading')))
        
    def setFunction(self):
        self.TGS.setText(str(self.Target.text()))
        self.ExpS.setText(str(self.Exposure.value()))
        
        cam1.set_attribute_value('Exposure Time', self.Exposure.value())
        cam1.set_attribute_value('Sensor Temperature Set Point', self.Temperature.value())

    
    def capture_images(self):
        if not hasattr(self, 'image_handle'):
            initial_image = np.zeros((50, 50))
            self.image_handle = self.ax.imshow(initial_image, 
                                               interpolation='nearest', 
                                               cmap='Blues',
                                               vmin=0, vmax=1)
            self.canvas.draw_idle()
            
        while self.cam_open:
            if self.paused:
                time.sleep(1)
                continue
    
            if not self.stop:
                exposure_time = int(self.ExpS.value()) 
                cam1.set_attribute_value('Exposure Time', exposure_time)
                with PrincetonInstruments.PicamCamera('0809080002') as cam1:
                    cam1.start_acquisition()
                    while True:
                        cam1.wait_for_frame()  
                        image = cam1.read_oldest_image()
                        self.image_handle.set_data(image)
                        self.canvas.draw_idle()
                        
                        # File Saving
                        target = self.Target.text().strip().replace(" ", "_")
                        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                        filename = f"{target}_{current_time}"    
                        file_path = os.path.join("C:\\Users\\Owner\\PICAM\\images", filename)
                        image.tofile(file_path + '.bin')
                
            else:
                break
    
            time.sleep(0.2)


    def pauseCapture(self):
        self.paused = True
        self.pauseButton.setEnabled(False)
        self.resumeButton.setEnabled(True)
        
    def ExecuteSeries(self):
        input_string = self.Param.toPlainText()
        series = []
    
        rows = input_string.splitlines()
        for row in rows:
            parts = row.split()
            if not parts:
                continue
    
            if parts[0] == 'add' and parts[1] == 'delay':
                series.append([float(parts[2])])
            else:
                num_exposures = int(parts[0])
                exposure_time = float(parts[1])
                file_name = parts[2]
                series.append([num_exposures, exposure_time, file_name])
    
        # Create and start the thread
        self.capture_thread = CaptureSeriesThread(series)
        self.capture_thread.update_image.connect(self.display_image)
        self.capture_thread.start()
    
    def display_image(self, image):
        if not hasattr(self, 'image_handle'):
            self.image_handle = self.ax.imshow(image, interpolation='nearest')
        else:
            self.image_handle.set_data(image)
    
        self.canvas.draw_idle()
    

    def resumeCapture(self):
        self.paused = False
        self.resumeButton.setEnabled(False)
        self.pauseButton.setEnabled(True)
        
    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Camera Operation"))

        
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
