#!/usr/bin/env python3

#@reboot /root/ssplz_device/client/shutdown.py

import asyncio
import subprocess

import OPi.GPIO as GPIO
from datetime import datetime as dt
import time

import requests

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

    GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.add_event_detect(8, GPIO.BOTH, callback=callback, bouncetime=300)
    GPIO.add_event_detect(10, GPIO.BOTH, callback=callback, bouncetime=300)

    GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(22, GPIO.FALLING, callback=callback, bouncetime=300)

    GPIO.setup(16,GPIO.OUT)
    GPIO.setup(18,GPIO.OUT)

def callback(channel):
    print("button pushed %s"%channel)
    subprocess.run("/usr/sbin/shutdown -h now", shell=True)

def set_output(num, value):

    pin = 16 if num == int(1) else 18
    val = GPIO.HIGH if value == int(1) else GPIO.LOW

    GPIO.output(pin,val)
    print("pin :", pin, " / value:", val)

    return True
    
def set_output_api(num, value):

    url = "http://localhost/output"
    
    payload = {
        "num": num,
        "val": value
    }

    try:
        res = requests.post(url, data=payload, timeout=1.0)
        print(res.text)
        
    except:
        print("not working.")
    
def output_by_hour(hour, num):

    h = dt.now().hour
    print(hour)

    #num = 1
    value = 1

    if h < hour:
        value = 0

    #set_output(num, value)
    set_output_api(num, value)
        
async def main():

    init()
    
    while True:
        
        output_by_hour(20, 1):
        time.sleep(10)

#loop = asyncio.get_event_loop()
#loop.run_until_complete(make_request())

asyncio.run(main())