#!/usr/bin/env python3

#@reboot /root/ssplz_device/client/main.py

import flask
from flask import Flask, Response, request, jsonify, render_template

import OPi.GPIO as GPIO
import pandas as pd

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

cnt = {}
dat = {}
names = ["in1", "in2", "out1", "out2"]

for s in names:
    cnt[s] = 0
    dat[s] = dt.now()

df = pd.DataFrame()
df["datetime"] = 0
df["name"] = 0
df["value"] = 0

print(df.head())

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

def set_count(pin, value):

    global cnt
    global dat
    global df
    
    code = {
        8 : "in1",
        10: "in2",
        16: "out1",
        18: "out2"
    }
    
    name = code[pin]

    cnt[name] += value
    dat[name] = dt.now()

    row = {
        "datetime": [dt.now()],
        "name": [name],
        "value": [value]
    }
    
    #print(pd.DataFrame(row).head())
    
    df = pd.concat([df, pd.DataFrame(row)]).reset_index(drop=True)
    print(df.head())
    
def get_count():

    global cnt
    global dat
    global names
    
    txt = {}
    
    for s in names:
        txt["cnt_{}".format(s)] = cnt[s]
        txt["dat_{}".format(s)] = dat[s]
        
    txt["now"] = dt.now()

    return jsonify(txt)

def put_signal():

    global url
    global payload

    try:
        res = requests.post(url, data=payload, timeout=1.0)
        print(res.text)
        
    except:
        print("not working.")

def update(pin):

    global cnt
    global dat

    value = GPIO.input(pin)
    set_count(pin, value)

def send_signal_gae(num):

    global cnt
    global dat
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
        thd.start()

def set_output(num, value):

    global cnt
    global dat

    pin = 16 if num == int(1) else 18
    val = GPIO.HIGH if value == int(1) else GPIO.LOW

    GPIO.output(pin,val)
    print("pin :", pin, " / value:", val)
    
    set_count(pin, value)
    
    #cnt["out{}".format(num)] += value
    #dat["out{}".format(num)] = dt.now()
    
    return True

def callback(pin):

    print("button pushed %s"%pin, GPIO.input(pin), dt.now())

    if pin == 22:
        subprocess.run(["shutdown", "-h", "now"])
    else:
        #send_signal_gae(channel)
        update(pin)
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

    num = 1 if int(request.form["num"]) == 1 else 2
    val = GPIO.HIGH if request.form["val"] == "1" else GPIO.LOW

    set_output(num, val)
    #GPIO.output(num,val)
    #send_signal_gae(num)

    return print_status()

@app.route('/control')
def control():

    return render_template('control.html')

if __name__ == "__main__":
    init()

    try:
        app.run(host='::', port=80, debug=True)

    finally:
        print("terminated")

