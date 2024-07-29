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
from PyQt6.QtCore import QTimer

import winsound
frequency = 2500  # Set Frequency To 2500 Hertz
duration = 100 # Set Duration To 1000 ms == 1 second


#         __o
#       _ \<_
#      (_)/(_)
#```````         

class scimiaWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.widget = QWidget()
        
        self.setWindowTitle("GamingListener")
        self.setGeometry(500,120,200,120)

        self.masterGrid = QGridLayout()
        self.inputDevices =  [device for device in sd.query_devices() if (device["max_input_channels"] > 0)]
        self.outputDevices =  [device for device in sd.query_devices() if (device["max_output_channels"] > 0)]
        self.listeningCheck = QCheckBox("enable listening")
        self.triggerCheck = QCheckBox("enable trigger")
        self.threshold = QLineEdit("100")
        self.volumeBar = QProgressBar()
        self.inputSelector = QComboBox()
        self.inputSelector.addItems([device["name"] for device in self.inputDevices])
        self.outputSelector = QComboBox()
        self.outputSelector.addItems([device["name"] for device in self.outputDevices])
        self.debugButton = QPushButton("debug")
        self.options = QCheckBox("show options")

        self.masterGrid.addWidget(self.listeningCheck)
        self.masterGrid.addWidget(self.triggerCheck)
        self.masterGrid.addWidget(self.threshold)
        self.masterGrid.addWidget(self.inputSelector)
        self.masterGrid.addWidget(self.outputSelector)
        self.masterGrid.addWidget(self.volumeBar)
        self.masterGrid.addWidget(self.debugButton)
        self.widget.setLayout(self.masterGrid)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateProgressBar)
        self.timer.start()
        self.timer.setInterval(10)

        self.debugButton.clicked.connect(self.playsound)
        
        self.setCentralWidget(self.widget)

        # Start the audio stream
        self.stream = sd.InputStream(callback=self.audio_callback)
        self.stream.start()

    def audio_callback(self, indata, frames, time, status):
        # Calculate the volume as the norm of the input data
        self.volume_level = np.linalg.norm(indata) * 40

    def updateProgressBar(self):
        print("hello")
        # Update the progress bar with the current volume level
        self.volumeBar.setValue(min(int(self.volume_level), 100))
        if (self.volume_level>100):
            self.playsound()


    def playsound(self):
        winsound.Beep(frequency, duration)
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    listenerWindow = scimiaWindow()
    listenerWindow.show()
    app.exec()

