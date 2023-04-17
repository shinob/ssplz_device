#!/usr/bin/env python3

import flask
from flask import Flask, Response, request, jsonify

import OPi.GPIO as GPIO

from datetime import datetime as dt
from datetime import timedelta

import time
import requests
import threading

import config

GPIO.BOARD = {
    7:    203,
    8:    198,
    10:   199,
    11:   0,
    12:   6,
    13:   2,
    15:   3,
    16:   200,
    18:   201,
    19:   20,
    21:   65,
    22:    1,
    23:   66,
    24:   67
}

app = Flask(__name__)

cnt_in1 = 0
dat_in1 = dt.now()

payload = {}
url = config.url

def reset_count():

    global cnt_in1
    global dat_in1
    
    global payload
    
    payload = {
        "name": "in1",
        "value": cnt_in1
    }
    
    put_signal()

    cnt_in1 = 0
    dat_in1 = dt.now()
    
    payload = {
        "name": "in1",
        "value": cnt_in1
    }
    
    put_signal()

def set_count(value):

    global cnt_in1
    global dat_in1
    
    cnt_in1 = value
    dat_in1 = dt.now()

def get_count():

    global cnt_in1
    global dat_in1
    
    txt = {
        "cnt_in1" : cnt_in1,
        "dat_in1" : dat_in1
    }

    return jsonify(txt)

def put_signal():

    global url
    global payload

    res = requests.post(url, data=payload, timeout=1.0)
    
    print(res.text)

def send_signal_gae(num):

    global cnt_in1
    global dat_in1
    global payload

    name = {
        "8" : "in1",
        "10": "in2",
        "16": "out1",
        "18": "out2"
    }

    value = GPIO.input(num)

    payload = {
        "name": name[str(num)],
        "value": GPIO.input(num)
    }

    if num == int(8):

        set_output(1, value)

        cnt_in1 += value
        print(cnt_in1)
        
        flg = False
        
        if cnt_in1 % 10 == 0:
            flg = True
        if value == 1:
            flg = True
        if dat_in1 < dt.now() - timedelta(minutes=1):
            flg = True
            
        print(flg)

        if flg:
            
            payload["value"] = cnt_in1
            dat_in1 = dt.now()
            
            thd = threading.Thread(target=put_signal)
            thd.start()

    else:
        
        thd = threading.Thread(target=put_signal)
        thd.join()

def set_output(num, value):

    pin = 16 if num == int(1) else 18
    val = GPIO.HIGH if value == int(1) else GPIO.LOW

    GPIO.output(pin,val)
    print("pin :", pin, " / value:", val)

    return True

def callback(channel):

    print("button pushed %s"%channel, GPIO.input(channel), dt.now())

    if channel == 22:
        subprocess.run(["shutdown", "-h", "now"])
    else:
        send_signal_gae(channel)
        time.sleep(0.5)

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

def print_status():

    txt = {
        "in1" : GPIO.input(8),
        "in2" : GPIO.input(10),
        "out1": GPIO.input(16),
        "out2": GPIO.input(18),
        "stop": GPIO.input(22)
    }

    return jsonify(txt)

@app.route('/')
def index():

    return print_status()

@app.route('/reset')
def reset():

    reset_count()
    
    return print_status()

@app.route('/setcnt', methods=["POST"])
def setcnt():

    num = request.form["num"]
    val = request.form["val"]
    set_count(int(val))
    
    return get_count()

@app.route('/getcnt')
def getcnt():

    return get_count()

@app.route('/output', methods=["POST"])
def output():

    num = 16 if int(request.form["num"]) == 1 else 18
    val = GPIO.HIGH if request.form["val"] == "1" else GPIO.LOW

    GPIO.output(num,val)
    send_signal_gae(num)

    return print_status()

if __name__ == "__main__":
    init()

    try:
        app.run(host='::', port=80, debug=True)

    finally:
        print("terminated")

