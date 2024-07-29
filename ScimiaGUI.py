# generate sound instead of sound.wav?

import sys

import numpy as np
import sounddevice as sd

from PyQt6.QtWidgets import *
from PyQt6.QtCore import QTimer
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

#         __o
#       _ \<_
#      (_)/(_)
#```````         

class monitorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.widget = QWidget()
        
        self.setWindowTitle("voice monitor")
        self.setGeometry(500,120,200,120)

        self.masterGrid = QGridLayout()
        self.inputDevices =  [device for device in sd.query_devices() if (device["max_input_channels"] > 0)]
        self.outputDevices =  [device for device in sd.query_devices() if (device["max_output_channels"] > 0)]
        self.triggerCheck = QCheckBox("enable trigger")
        self.multiplier = QLineEdit("100")
        self.volumeBar = QProgressBar()
        self.volumeBar.setOrientation(Qt.Orientation.Vertical)
        self.inputSelector = QComboBox()
        self.inputSelector.addItems(set([device["name"][0:80] for device in self.inputDevices]))
        self.outputSelector = QComboBox()
        self.outputSelector.addItems(set([device["name"][0:80] for device in self.outputDevices]))
        self.debugButton = QPushButton("debug")
        self.options = QCheckBox("show options")

        self.volumeBar.setStyleSheet("""
            QProgressBar {
                border: 1px solid grey;
                border-radius: 1px;
                text-align: center;
            }

            QProgressBar::chunk {
                background-color: green;
            }
        """)
        print(sd.default.device)

        self.masterGrid.addWidget(self.triggerCheck)
        self.masterGrid.addWidget(self.multiplier)
        self.masterGrid.addWidget(self.inputSelector)
        self.masterGrid.addWidget(self.outputSelector)
        
        self.masterGrid.addWidget(self.debugButton)
        self.masterGrid.addWidget(self.options)
        self.masterGrid.addWidget(self.volumeBar,0,1,-1,1)
        self.widget.setLayout(self.masterGrid)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.UpdateProgressBar)
        self.timer.start()
        self.timer.setInterval(50)

        self.debugButton.clicked.connect(self.Debug)
        
        self.setCentralWidget(self.widget)

        # Start the audio stream
        self.stream = sd.InputStream(callback=self.ListenToMic)
        self.stream.start()

    def Debug(self):
        self.PlayTone()

    def ListenToMic(self, indata, frames, time, status):
        # Calculate the volume as the norm of the input data
        self.volume_level = np.linalg.norm(indata) * int(self.multiplier.text())

    def UpdateProgressBar(self):
        # Update the progress bar with the current volume level
        self.volumeBar.setValue(min(int(self.volume_level), 100))
        if (self.volume_level>100 and self.triggerCheck.isChecked()):
            self.Trigger()

    def Trigger(self):
        self.PlayTone()
    
    def PlayTone(self, freq=2500, duration=0.2, samplerate=44100, amplitude=0.5):
        """
        Play a sine wave tone.

        Parameters:
        - frequency: Frequency of the sine wave in Hz (default: 440 Hz, which is A4 note).
        - duration: Duration of the tone in seconds (default: 1 second).
        - samplerate: Sampling rate in samples per second (default: 44100 Hz).
        - amplitude: Amplitude of the wave (default: 0.5, range: 0.0 to 1.0).
        """
        # Generate time points
        t = np.linspace(0, duration, int(samplerate * duration), endpoint=False)

        # Generate sine wave
        wave = amplitude * np.sin(2 * np.pi * freq * t)

        # Play the sound
        sd.play(wave, samplerate)
        sd.wait()  # Wait until the sound has finished playing



if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont("Aptos", 10)
    app.setFont(font)
    listenerWindow = monitorWindow()
    listenerWindow.show()
    
    app.exec()

