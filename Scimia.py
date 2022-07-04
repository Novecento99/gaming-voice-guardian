"""
Scimia by Novecento

This script is meant to be run directly.
"""

import os
import time
import sys
from queue import Queue

import keyboard
import numpy as np
import sounddevice as sd
import soundfile as sf
from termcolor import colored

scimia_enabled = True
BAR_LENGTH = 60

os.system('color')
os.system('mode con: cols=65 lines=32')
data, fs = sf.read('sound.wav')
print(r"""               _           _                __      __         
    __________(_)___ ___  (_)___ _   ____ _/ /___  / /_  ____ _
   / ___/ ___/ / __ `__ \/ / __ `/  / __ `/ / __ \/ __ \/ __ `/
  (__  ) /__/ / / / / / / / /_/ /  / /_/ / / /_/ / / / / /_/ / 
 /____/\___/_/_/ /_/ /_/_/\__,_/   \__,_/_/ .___/_/ /_/\__,_/  
                                       /_/       by Novecento                                                                                                                           
""")

if len(sys.argv)>1:
    print('Volume threshold set to ' + sys.argv[1])
    val = sys.argv[1]
else:
    val = input(" Set microphone treshold: ")

print(" Scimia is alarmed... ")
print(r"""
                                   __
                                 / _,\
                                 \_\
                      ,,,,    _,_)  #      /)
                     (= =)D__/    __/     //
                    C/^__)/     _(    ___//
                      \_,/  -.   '-._/,--'
                _\\_,  /           -//.
                 \_ \_/  -,._ _     ) )
                   \/    /    )    / /
                   \-__,/    (    ( (
                              \.__,-)\_
                               )\_ / -(
              b'ger           / -(////
                             ////
                             

""")

max_audio_value = int(val)
print(" p to pause, give a banana to Scimia at paypal.me/Novecento99" + "\033[F" + "\033[F" + "\033[F")

# Create the queue that will hold the audio chunks
audio_queue = Queue()


# noinspection PyUnusedLocal
def callback(indata: np.ndarray, outdata: np.ndarray, frames: int,
             time_, status: sd.CallbackFlags) -> None:
    """
    This is called (from a separate thread) for each audio block.

    Taken from the sounddevice docs:
    https://python-sounddevice.readthedocs.io/en/0.3.14/examples.html#recording-with-arbitrary-duration

    According to the docs, our function must have this signature:
    def callback(indata: ndarray, outdata: ndarray, frames: int,
                             time: CData, status: CallbackFlags) -> None
    """
    # Add the data to the queue
    audio_queue.put(indata.copy())


with sd.Stream(callback=callback):
    try:
        while True:
            # Pull a chunk of audio from the queue
            # This call is blocking, so if the queue is empty, we will wait until chunk has been added
            loudness = np.linalg.norm(audio_queue.get()) * 10
            bar = int(loudness * (BAR_LENGTH / max_audio_value))

            # Check if we need to pause
            if keyboard.is_pressed('p'):
                # Flip the boolean
                scimia_enabled = not scimia_enabled
                print(f"\n\n p to {'pause' if scimia_enabled else 'resume'} " + "\033[F" * 3)
                time.sleep(0.3)

            # If we are quiet, then print the audio bar
            if loudness < max_audio_value:
                print(' [' + '|' * bar + ' ' * (BAR_LENGTH - bar) + ']', end='\r')
            else:
                # Add the color red if we have passed the audio threshold
                print(colored(' [' + '!' * BAR_LENGTH + ']', 'red'), end='\r')
                # Play a sound to the user to let them know that they are loud
                if scimia_enabled:
                    sd.play(data, fs)
                    sd.wait()
    except KeyboardInterrupt:
        print("\n\n\nStopping...")
