# generate sound instead of sound.wav?

import pyaudio
import os
import sys
import time
import sys
from queue import Queue

import keyboard
import numpy as np
import sounddevice as sd
import soundfile as sf
#from termcolor import colored

from timeit import default_timer as timer

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import *
from PyQt6 import QtGui
from PyQt6.QtWidgets import QWidget

#         __o
#       _ \<_
#      (_)/(_)
#```````         

class scimiaWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        widget = QWidget()
        
        self.setWindowTitle("GamingListener")

        self.setGeometry(500,120,200,120)

        self.masterGrid = QGridLayout()
        self.inputDevices =  [device for device in sd.query_devices() if (device["max_input_channels"] > 0)]
        self.outputDevices =  [device for device in sd.query_devices() if (device["max_output_channels"] > 0)]
        self.listeningCheck = QCheckBox("enable listening")
        self.triggerCheck = QCheckBox("enable trigger")
        self.thresHold = QLineEdit("100")
        self.inputSelector = QComboBox()
        self.inputSelector.addItems([device["name"] for device in self.inputDevices])
        self.outputSelector = QComboBox()
        self.outputSelector.addItems([device["name"] for device in self.outputDevices])

        self.masterGrid.addWidget(self.listeningCheck)
        self.masterGrid.addWidget(self.triggerCheck)
        self.masterGrid.addWidget(self.thresHold)
        self.masterGrid.addWidget(self.inputSelector)
        self.masterGrid.addWidget(self.outputSelector)

        widget.setLayout(self.masterGrid)
        self.setCentralWidget(widget)
        

    
if __name__ == '__main__':
    

    app = QApplication(sys.argv)
    listenerWindow = scimiaWindow()
    listenerWindow.show()
    app.exec()

