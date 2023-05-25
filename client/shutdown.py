#!/usr/bin/env python3

#@reboot /root/ssplz_device/client/shutdown.py

import asyncio
import subprocess
import OPi.GPIO as GPIO

import time

GPIO.BOARD = {
    7:    203,   # PG11
    8:    198,   # PG6
    10:   199,   # PG7
    11:   0,     # PA0
    12:   6,     # PA6
    13:   2,     # PA2
    15:   3,     # PA3
    16:   200,   # PG8
    18:   201,   # PG9
    19:   20,    # PC0
    21:   65,    # PC1
    22:    1,    # PA1
    23:   66,    # PC2
    24:   67     # PC3
}

def init():

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(22, GPIO.BOTH, callback=callback, bouncetime=300)

def callback(channel):
	
    subprocess.run("/usr/sbin/shutdown -h now", shell=True)

async def main():

    init()
    
    while True:

        time.sleep(5)
    
asyncio.run(main())
