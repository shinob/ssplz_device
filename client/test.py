#!/usr/bin/env python3

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

def callback(channel):
    print("button pushed %s"%channel)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.add_event_detect(8, GPIO.FALLING, callback=callback, bouncetime=300)
GPIO.add_event_detect(10, GPIO.FALLING, callback=callback, bouncetime=300)

GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(22, GPIO.FALLING, callback=callback, bouncetime=300)

GPIO.setup(16,GPIO.OUT)
GPIO.setup(18,GPIO.OUT)

for p in [16, 18]:

    time.sleep(2)
    GPIO.output(p,GPIO.HIGH)
    
    time.sleep(5)
    GPIO.output(p,GPIO.LOW)
    
    #time.sleep(5)

