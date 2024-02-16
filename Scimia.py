# generate sound instead of sound.wav?


import os
import sys
import time
import sys
from queue import Queue

import keyboard
import numpy as np
import sounddevice as sd
import soundfile as sf
from termcolor import colored

from timeit import default_timer as timer

scimia_enabled = True
BAR_LENGTH = 60
start=-100

os.system('color')
os.system('mode con: cols=65 lines=32')

# If this file is compiled, we will use the _MEIPASS path (the temporary path/folder used by PyInstaller),
# otherwise use the CWD (current working directory).
data, samplerate = sf.read(getattr(sys, "_MEIPASS", os.getcwd()) + '/sound.wav')

# If this file is compiled, we will use the _MEIPASS path (the temporary path/folder used by PyInstaller),
# otherwise use the CWD (current working directory).
with open(getattr(sys, "_MEIPASS", os.getcwd()) +"/settings.txt", "r") as f:
    max_audio_value=int(f.read())


print(r"""                               
                __________(_)___ ___  (_)___ _  
               / ___/ ___/ / __ `__ \/ / __ `/  
              (__  ) /__/ / / / / / / / /_/ /  
             /____/\___/_/_/ /_/ /_/_/\__,_/   
                                by Novecento
      """)

if len(sys.argv)>1:
    print('Volume threshold set to ' + sys.argv[1])
    val = sys.argv[1]
else:
    print(" Microphone treshold from settings is: "+str(max_audio_value))
    val = input("\n Set microphone treshold: (or enter to keep "+str(max_audio_value)+")")
    try:

        max_audio_value=int(val)
        with open(getattr(sys, "_MEIPASS", os.getcwd()) +"/settings.txt", "w") as f:
            f.write(str(val))
    except ValueError:
        print(" Last threshold kept\n")
        

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


print(f" p to {colored('pause','red')}! give a banana to Scimia at  " + "\033[F" + "\033[F" + "\033[F")

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
                print(f"\n\n p to {colored('pause','red') if scimia_enabled else colored('resume','red')}!" + "\033[F" * 3)
                time.sleep(0.3)

            # If we are quiet, then print the audio bar
            if loudness < max_audio_value:
                print(' [' + '|' * bar + ' ' * (BAR_LENGTH - bar) + ']', end='\r')
            else:
                # Add the color red if we have passed the audio threshold
                print(colored(' [' + '!' * BAR_LENGTH + ']', 'red'), end='\r')
                # Play a sound to the user to let them know that they are loud
                if scimia_enabled and (timer()-start)>4:
                    start = timer()
                    sd.play(data, samplerate)
                    sd.wait()
    except KeyboardInterrupt:
        print("\n\n\nStopping...")
