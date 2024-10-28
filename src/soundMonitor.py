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
# ```````

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
        self.isChangedByUser = False
        self.setWindowTitle("Microphone Guardian")
        self.setGeometry(500, 120, 400, 200)

        self.inputDevices = [
            device
            for device in sd.query_devices()
            if (device["max_input_channels"] > 0)
        ]
        self.outputDevices = [
            device
            for device in sd.query_devices()
            if (device["max_output_channels"] > 0)
        ]

        self.triggerCheck = QCheckBox("Enable Trigger")
        self.triggerCheck.setChecked(True)

        configBoxSize = 50

        self.thresholdSlider = QSlider()
        self.thresholdSlider.setValue(configBoxSize)
        self.thresholdSlider.setOrientation(Qt.Orientation.Horizontal)
        self.thresholdSlider.setBaseSize(0, 0)

        self.thresholdLabel = QLabel("- Trigger Threshold")
        self.thresholdBox = QLineEdit("50")
        self.thresholdBox.setMaximumWidth(50)

        self.gainLabel = QLabel("- Mic Sensitivity (Gain)")
        self.gainBox = QLineEdit("100")
        self.gainBox.setMaximumWidth(configBoxSize)

        # Options
        self.frequencyLabel = QLabel("- Frequency (440 Hz is A4)")
        self.frequencyBox = QLineEdit("500")
        self.frequencyBox.setMaximumWidth(configBoxSize)

        self.durationLabel = QLabel("- Duration in seconds")
        self.durationBox = QLineEdit("1")
        self.durationBox.setMaximumWidth(configBoxSize)

        self.sampleRateLabel = QLabel("- Sample Rate (44100 Hz)")
        self.sampleRateBox = QLineEdit("44100")
        self.sampleRateBox.setMaximumWidth(configBoxSize)

        self.amplitudeLabel = QLabel("- Amplitude (0.0 to 1.0)")
        self.amplitudeBox = QLineEdit("0.75")
        self.amplitudeBox.setMaximumWidth(configBoxSize)

        self.volumeBar = QProgressBar()
        self.volumeBar.setTextVisible(False)
        self.feedbackLabel = QLabel()
        self.feedbackLabel.setFixedHeight(10)
        # self.volumeBar.setOrientation(Qt.Orientation.Vertical)
        self.inputSelector = QComboBox()
        self.inputSelector.addItems(
            [
                (str(device["index"]).format("%02d", 7) + " " + device["name"])
                for device in self.inputDevices
            ]
        )
        self.inputSelector.setCurrentText(sd.query_devices()[1]["name"])
        self.volumeKnob = QDial()
        self.volumeKnob.setValue(100)
        self.outputSelector = QComboBox()
        self.outputSelector.addItems(
            [
                (str(device["index"]).format("%02d", 7) + " " + device["name"])
                for device in self.outputDevices
            ]
        )
        self.outputSelector.setCurrentText(sd.query_devices()[4]["name"])
        self.outputSelector.currentIndexChanged.connect(self.restartOutput)
        self.saveMainButton = QPushButton("Save Settings")
        self.cancelMainButton = QPushButton("Cancel Changes")
        self.saveOptionsButton = QPushButton("Save Settings")
        self.cancelOptionsButton = QPushButton("Cancel Changes")
        # self.optionsCheck = QCheckBox("minimal mode")
        # self.optionsCheck.checkStateChanged.connect(self.toggleOptions)

        self.inputSelector.currentIndexChanged.connect(self.restartInput)

        self.volumeBar.setStyleSheet(
            """
            QProgressBar {
                border: 1px solid grey;
                border-radius: 1px;
                text-align: center;
            }

            QProgressBar::chunk {
                background-color: green;
            }
        """
        )

        self.thresholdSlider.setStyleSheet(
            """
            QSlider::groove:horizontal {
                height: 0px;
            }
            QSlider::handle:horizontal {
                background-color: blue; 
                border: 1px solid black;
                width: 10px;
                margin: -5px 0;
            }
        """
        )

        self.parentGrid = QGridLayout()
        gainLayout = QHBoxLayout()
        thresholdLayout = QHBoxLayout()
        self.configLayout = QGridLayout()

        gainLayout.addWidget(self.gainBox, 0, Qt.AlignmentFlag.AlignLeft)
        gainLayout.addWidget(self.gainLabel, 0, Qt.AlignmentFlag.AlignLeft)

        thresholdLayout.addWidget(self.thresholdBox, 0, Qt.AlignmentFlag.AlignLeft)
        thresholdLayout.addWidget(self.thresholdLabel, 0, Qt.AlignmentFlag.AlignLeft)

        # (arg__1,row,column,rowSpan,columnSpan,alignment)
        self.parentGrid.addWidget(
            self.volumeBar, 0, 0, 1, -1, Qt.AlignmentFlag.AlignBaseline
        )
        self.parentGrid.addWidget(
            self.thresholdSlider, 0, 0, 1, -1, Qt.AlignmentFlag.AlignBaseline
        )
        self.parentGrid.addWidget(
            self.volumeKnob, 1, 0, 2, 1, Qt.AlignmentFlag.AlignBaseline
        )

        self.parentGrid.addLayout(
            thresholdLayout, 1, 1, 1, 1, Qt.AlignmentFlag.AlignLeft
        )
        self.parentGrid.addLayout(gainLayout, 2, 1, 1, 1, Qt.AlignmentFlag.AlignLeft)

        # self.parentGrid.addWidget(self.feedbackLabel,4,0,1,-1,Qt.AlignmentFlag.AlignJustify)
        self.parentGrid.addWidget(
            self.triggerCheck, 1, 2, 1, -1, Qt.AlignmentFlag.AlignRight
        )
        self.parentGrid.addWidget(
            self.saveMainButton, 3, 0, 1, -1, Qt.AlignmentFlag.AlignLeft
        )
        self.parentGrid.addWidget(
            self.cancelMainButton, 3, 2, 1, -1, Qt.AlignmentFlag.AlignRight
        )

        self.configLayout.addWidget(self.frequencyBox, 0, 0)
        self.configLayout.addWidget(self.frequencyLabel, 0, 1)

        self.configLayout.addWidget(self.durationBox, 1, 0)
        self.configLayout.addWidget(self.durationLabel, 1, 1)

        self.configLayout.addWidget(self.sampleRateBox, 0, 2)
        self.configLayout.addWidget(self.sampleRateLabel, 0, 3)

        self.configLayout.addWidget(self.amplitudeBox, 1, 2)
        self.configLayout.addWidget(self.amplitudeLabel, 1, 3)

        self.configLayout.addWidget(
            self.inputSelector, 2, 0, 1, -1, Qt.AlignmentFlag.AlignBaseline
        )
        self.configLayout.addWidget(
            self.outputSelector, 3, 0, 1, -1, Qt.AlignmentFlag.AlignBaseline
        )
        self.configLayout.addWidget(
            self.saveOptionsButton, 4, 0, 1, -1, Qt.AlignmentFlag.AlignLeft
        )
        self.configLayout.addWidget(
            self.cancelOptionsButton, 4, 2, 1, -1, Qt.AlignmentFlag.AlignRight
        )

        # self.freq, self.duration, self.samplerate,self.amplitude

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.UpdateProgressBar)
        self.timer.start()
        self.timer.setInterval(50)

        self.frequencyBox.textEdited.connect(self.UpdateOptions)
        self.durationBox.textEdited.connect(self.UpdateOptions)
        self.sampleRateBox.textEdited.connect(self.UpdateOptions)
        self.amplitudeBox.textEdited.connect(self.UpdateOptions)

        self.volumeKnob.valueChanged.connect(self.setGainBox)
        self.gainBox.textEdited.connect(self.setVolumeKnob)
        self.thresholdSlider.valueChanged.connect(self.setThresholdBox)
        self.thresholdBox.textEdited.connect(self.setThresholdSlider)

        self.saveMainButton.clicked.connect(self.updateConfigs)
        self.saveOptionsButton.clicked.connect(self.updateConfigs)

        self.cancelMainButton.clicked.connect(self.retrieveConfigs)
        self.cancelOptionsButton.clicked.connect(self.retrieveConfigs)
        self.setChanged(False)

        self.tab_widget = QTabWidget()

        self.mainTab = QWidget()
        self.optionsTab = QWidget()

        self.tab_widget.addTab(self.mainTab, "Main")
        self.tab_widget.addTab(self.optionsTab, "Options")
        self.mainTab.setLayout(self.parentGrid)
        self.optionsTab.setLayout(self.configLayout)

        self.setCentralWidget(self.tab_widget)

        self.iniPath = "config.ini"
        # Start the audio stream
        self.stream = sd.InputStream(callback=self.ListenToMic)
        self.restartInput()
        self.retrieveConfigs()

        self.isChangedByUser = False
        self.UpdateOptions()
        self.isChangedByUser = (
            True  # any future changes triggered will be from a user action
        )

    def setChanged(self, isChanged):
        self.saveMainButton.setDisabled(not isChanged)
        self.saveOptionsButton.setDisabled(not isChanged)
        self.cancelMainButton.setDisabled(not isChanged)
        self.cancelOptionsButton.setDisabled(not isChanged)

    def setThresholdSlider(self):
        self.thresholdSlider.setValue(int(self.thresholdBox.text()))
        self.setChanged(True)

    def setThresholdBox(self):
        self.thresholdBox.setText(str(self.thresholdSlider.value()))
        self.setChanged(True)

    def setVolumeKnob(self):
        self.volumeKnob.setValue(int(self.gainBox.text()))
        self.setChanged(True)

    def setGainBox(self):
        self.gainBox.setText(str(self.volumeKnob.value()))
        self.setChanged(True)

    def updateConfigs(self):
        config = ConfigParser()
        config.read(self.iniPath)
        if not config.has_section("main"):
            config.add_section("main")
        if not config.has_section("options"):
            config.add_section("options")
        if not config.has_section("devices"):
            config.add_section("devices")

        config.set("main", "gainBox", self.gainBox.text())
        config.set("main", "thresholdBox", self.thresholdBox.text())
        config.set("main", "triggerCheck", str(self.triggerCheck.isChecked()))

        config.set("options", "frequencyBox", self.frequencyBox.text())
        config.set("options", "durationBox", self.durationBox.text())
        config.set("options", "sampleRateBox", self.sampleRateBox.text())
        config.set("options", "amplitudeBox", self.amplitudeBox.text())

        config.set("devices", "inputSelector", self.inputSelector.currentText())
        config.set("devices", "outputSelector", self.outputSelector.currentText())

        with open(self.iniPath, "w") as f:
            config.write(f)

        self.setChanged(False)

    def retrieveConfigs(self):
        config = ConfigParser()
        config.read(self.iniPath)

        self.isChangedByUser = False

        self.volumeKnob.setValue(int(config.get("main", "gainBox", fallback="100")))
        self.thresholdSlider.setValue(
            int(config.get("main", "thresholdBox", fallback="50"))
        )
        self.gainBox.setText(config.get("main", "gainBox", fallback="100"))
        self.thresholdBox.setText(config.get("main", "thresholdBox", fallback="50"))
        self.triggerCheck.setChecked(
            bool(config.get("main", "triggerCheck", fallback="True"))
        )

        self.frequencyBox.setText(config.get("options", "frequencyBox", fallback="440"))
        self.durationBox.setText(config.get("options", "durationBox", fallback="1"))
        self.sampleRateBox.setText(
            config.get("options", "sampleRateBox", fallback="44100")
        )
        self.amplitudeBox.setText(
            config.get("options", "amplitudeBox", fallback="0.75")
        )

        self.inputSelector.setCurrentText(
            config.get("devices", "inputSelector", fallback="")
        )
        self.outputSelector.setCurrentText(
            config.get("devices", "outputSelector", fallback="")
        )

        self.setChanged(False)
        self.isChangedByUser = True  # Next change would be triggered by a user

    def toggleOptions(self):
        inverted = not (self.optionsCheck.isChecked())
        self.inputSelector.setVisible(inverted)
        self.outputSelector.setVisible(inverted)
        self.gainBox.setVisible(inverted)
        # self.debugButton.setVisible(inverted)
        # self.knob.setVisible(inverted)
        self.feedbackLabel.setVisible(inverted)

    def restartInput(self):
        if self.stream.active:
            self.stream.close()
        try:
            sd.default.device = [
                int(self.inputSelector.currentText()[0:2]),
                sd.default.device[1],
            ]
            self.stream = sd.InputStream(callback=self.ListenToMic)
            self.stream.start()
            self.feedbackLabel.setText("Started")
        except Exception as e:
            self.feedbackLabel.setText(e)
            print(e)

    def restartOutput(self):
        try:
            sd.default.device = [
                sd.default.device[0],
                int(self.outputSelector.currentText()[0:2]),
            ]
            # self.PlayTone()
            if self.isChangedByUser:
                self.setChanged(True)
            else:
                self.setChanged(False)

        except Exception as e:
            self.feedbackLabel.setText(e)
            print(e)

    def ListenToMic(self, indata, frames, time, status):
        # Calculate the volume as the norm of the input data
        self.volume_level = np.linalg.norm(indata) * int(self.gainBox.text())

    def UpdateProgressBar(self):
        # Update the progress bar with the current volume level
        self.volumeBar.setValue(min(int(self.volume_level), 100))

        if (
            self.volume_level > self.thresholdSlider.value()
            and self.triggerCheck.isChecked()
        ):
            self.Trigger()

    def UpdateOptions(self):
        # check to see if action was by a user or loading
        if self.isChangedByUser:
            self.setChanged(True)
        else:
            self.setChanged(False)

        try:
            self.freq = int(self.frequencyBox.text())
            self.frequencyBox.setStyleSheet("color: blue;")
        except ValueError:
            self.frequencyBox.setStyleSheet("color: red;")

        try:
            self.duration = float(self.durationBox.text())
            self.durationBox.setStyleSheet("color: blue;")
        except ValueError:
            self.durationBox.setStyleSheet("color: red;")

        try:
            self.samplerate = int(self.sampleRateBox.text())
            self.sampleRateBox.setStyleSheet("color: blue;")
        except ValueError:
            self.sampleRateBox.setStyleSheet("color: red;")

        try:
            self.amplitude = float(self.amplitudeBox.text())
            self.amplitudeBox.setStyleSheet("color: blue;")
        except ValueError:
            self.amplitudeBox.setStyleSheet("color: red;")

    def Trigger(self):
        self.PlayTone(self.freq, self.duration, self.samplerate, self.amplitude)

    def PlayTone(self, freq=500, duration=1, samplerate=44100, amplitude=0.75):
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Aptos", 10)
    app.setFont(font)
    listenerWindow = micMonitorWindow()
    listenerWindow.show()
    app.exec()
    listenerWindow.stream.close()
