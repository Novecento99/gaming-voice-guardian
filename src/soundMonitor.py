import sys

import numpy as np
import sounddevice as sd

from PyQt6.QtWidgets import *
from PyQt6.QtCore import QTimer
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


from configparser import ConfigParser


#
#         __o
#       _ \<_
#      (_)/(_)
#```````         

# TODO
# store and retrieve settings
# github workflow setup
# select input/ouput devices DONE
# custom sound
# GUI aestetich improvement
# graphical trigger feedback
# bug when closing application DONE
# max value monitoring
# automatic gain
# possibility to run custom script

class micMonitorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.widget = QWidget()

        
        
        self.setWindowTitle("Microphone Guardian")
        self.setGeometry(500,120,400,200)

        
        self.masterGrid = QGridLayout()
        self.inputDevices =  [device for device in sd.query_devices() if (device["max_input_channels"] > 0)]
        self.outputDevices =  [device for device in sd.query_devices() if (device["max_output_channels"] > 0)]
        self.triggerCheck = QCheckBox("enable trigger")
        self.triggerCheck.setChecked(True)
        self.labelGain = QLabel("set the gain underneath")
        self.gain = QLineEdit("100")
        self.volumeBar = QProgressBar()
        self.feedbackLabel = QLabel()
        self.feedbackLabel.setFixedHeight(10)
        #self.volumeBar.setOrientation(Qt.Orientation.Vertical)
        self.inputSelector = QComboBox()
        self.inputSelector.addItems([(str(device["index"]).format("%02d",7)+" "+device["name"]) for device in self.inputDevices])
        self.inputSelector.setCurrentText(sd.query_devices()[1]["name"])
        self.knob = QDial()
        self.outputSelector = QComboBox()
        self.outputSelector.addItems([(str(device["index"]).format("%02d",7)+" "+device["name"]) for device in self.outputDevices])
        self.outputSelector.setCurrentText(sd.query_devices()[4]["name"])
        self.outputSelector.currentIndexChanged.connect(self.restartOutput)
        self.debugButton = QPushButton("test trigger")
        self.optionsCheck = QCheckBox("minimal mode")
        self.optionsCheck.checkStateChanged.connect(self.toggleOptions)

        self.inputSelector.currentIndexChanged.connect(self.restartInput)

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
        

        self.masterGrid.addWidget(self.triggerCheck)

        
        #self.masterGrid.addWidget(self.volumeBar,0,1,-1,1)
        self.masterGrid.addWidget(self.volumeBar)
        #self.masterGrid.addWidget(self.optionsCheck)
        self.masterGrid.addWidget(self.labelGain)
        self.masterGrid.addWidget(self.gain)
        
        self.masterGrid.addWidget(self.inputSelector)
        self.masterGrid.addWidget(self.outputSelector)
        self.masterGrid.addWidget(self.feedbackLabel)
        self.masterGrid.addWidget(self.debugButton)
        #self.masterGrid.addWidget(self.knob,3,1)
        self.widget.setLayout(self.masterGrid)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.UpdateProgressBar)
        self.timer.start()
        self.timer.setInterval(50)

        self.debugButton.clicked.connect(self.Debug)
        
        self.setCentralWidget(self.widget)

        self.iniPath ='config.ini'
        # Start the audio stream
        self.stream = sd.InputStream(callback=self.ListenToMic)
        self.restartInput()
        self.retrieveConfigs()
        #self.updateConfigs()


    def updateConfigs(self):
        config = ConfigParser()
        config.read(self.iniPath )

        config.set('main','volumeGain',self.gain.text())
        config.set('main','inputDevice',self.inputDevices.())

        with open(self.iniPath , 'w') as f:
            config.write(f)

    def retrieveConfigs(self):
        config = ConfigParser()
        config.read(self.iniPath)

        self.gain.setText(config.get('main','volumeGain'))

    def toggleOptions(self):
        inverted = not(self.optionsCheck.isChecked())
        self.inputSelector.setVisible(inverted)
        self.outputSelector.setVisible(inverted)
        self.gain.setVisible(inverted)
        self.debugButton.setVisible(inverted)
        #self.knob.setVisible(inverted)
        self.feedbackLabel.setVisible(inverted)

    def restartInput(self):
        if self.stream.active:
            self.stream.close()
        try:
            sd.default.device = [int(self.inputSelector.currentText()[0:2]),sd.default.device[1]]
            self.stream = sd.InputStream(callback=self.ListenToMic)
            self.stream.start()
            self.feedbackLabel.setText("Started")
        except Exception as e:
            self.feedbackLabel.setText(e)
            print(e)

    def restartOutput(self):
        try:
            sd.default.device = [sd.default.device[0],int(self.outputSelector.currentText()[0:2])]
            self.PlayTone()
        except Exception as e:
            self.feedbackLabel.setText(e)
            print(e)

    def Debug(self):
        self.PlayTone()

    def ListenToMic(self, indata, frames, time, status):
        # Calculate the volume as the norm of the input data
        self.volume_level = np.linalg.norm(indata) * int(self.gain.text())

    def UpdateProgressBar(self):
        # Update the progress bar with the current volume level
        self.volumeBar.setValue(min(int(self.volume_level), 100))
        if (self.volume_level>100 and self.triggerCheck.isChecked()):
            self.Trigger()

    def Trigger(self):
        self.PlayTone()
        #add here some sort of graphical feedback
    
    def PlayTone(self, freq=2500, duration=0.2, samplerate=44100, amplitude=0.5):
        """
        Play a sine wave tone. (by GPT)

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
    listenerWindow = micMonitorWindow()
    listenerWindow.show()
    app.exec()
    listenerWindow.stream.close()

