import sounddevice as sd
import numpy as np
import soundfile as sf
import sys
import os
import time
from termcolor import colored, cprint
import keyboard

check = True
BarLenght = 60

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

ValMax = int(val)
print(" p to pause, give a banana to Scimia at paypal.me/Novecento99" + "\033[F" + "\033[F" + "\033[F")


def main(indata, outdata, frames, timeM, status):
    global check
    Loudness = np.linalg.norm(indata) * 10
    Bar = int(Loudness * (BarLenght / ValMax))
    if keyboard.is_pressed('p'):
        check = not check
        if (check):
            print("\n\n p to pause " + "\033[F" + "\033[F" + "\033[F")
            time.sleep(0.1)
        else:
            print("\n\n p to resume" + "\033[F" + "\033[F" + "\033[F")
            time.sleep(0.1)

    if Loudness < ValMax:
        print(' [' + '|' * Bar + ' ' * (BarLenght - Bar) + ']', end='\r')
    else:
        print(colored(' [' + '!' * BarLenght + ']', 'red'), end='\r')
        if check:
            sd.play(data, fs)
            sd.wait()


with sd.Stream(callback=main):
    sd.sleep(24 * 60 * 60000)
