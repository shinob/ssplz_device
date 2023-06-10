#!/usr/bin/env python3

#@reboot /root/ssplz_device/client/main.py

import flask
from flask import Flask, Response, request, jsonify, render_template, send_file

import OPi.GPIO as GPIO
import pandas as pd
import sys
import os

from datetime import datetime as dt
from datetime import timedelta

import time
import requests
import threading

from glob import glob

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
names = ["in1", "in2", "out1", "out2", "off"]

for s in names:
    cnt[s] = 0
    dat[s] = dt.now()

msg = ""

payload = {}
url = config.url

ssplz_url = "https://ssplz.ittools.biz/api/upload"

def make_dataframe():
    
    df = pd.DataFrame()
    
    df["datetime"] = 0
    df["name"] = 0
    df["value"] = 0
    
    return df
    
df = make_dataframe()

def save_csv_file():
    
    global df
    
    df.to_csv("/root/{}.csv".format(dt.now().strftime('%Y-%m-%d_%H%M%S')), index=False)
    
    #df = make_dataframe()
    
def send_mail(name, value):
    
    url = config.mail_url
    
    payload = {
	    "from": config.mail_from,
	    "subject": config.mail_subject,
	    "name": config.mail_name,
	    "body": "{}\n{} : {}".format(config.mail_body, name, value)
    }

    try:
        res = requests.post(url, data=payload, timeout=1.0)
    except:
        print("ERROR")

def send_ssplz(key, value):
    
    payload = {
        "mailaddress": config.ssplz_mail,
        "sensorkey": key,
        "value": value
    }
    
    res = requests.get(ssplz_url, data=payload, timeout=1.0)
    
    print(res.text)
    
def send_ssplz_wdt():
    
    payload = {
        "mailaddress": config.ssplz_mail,
        "sensorkey": config.ssplz_wdt,
        "value": 1
    }
    
    res = requests.get(ssplz_url, data=payload, timeout=1.0)
    
    print(res.text)
    
def reset_count():

    global cnt
    global dat
    global names
    
    for s in names:
        cnt[s] = 0
        dat[s] = dt.now()
        
    #global payload
    
    #payload = {
    #    "name": "in1",
    #    "value": cnt_in1
    #}
    
    #put_signal()

def set_count(pin, value):

    global cnt
    global dat
    global df
    
    code = {
        8 : "in1",
        10: "in2",
        16: "out1",
        18: "out2",
        22: "off"
    }
    
    name = code[pin]
    print(name)
    
    if config.flg_mail and name in config.mail_target:
        if config.mail_value == value:
            send_mail(name, value)
    
    if name == "in1":
        ssplz_flg = config.ssplz_flg1
        ssplz_key = config.ssplz_key1
        ssplz_type= config.ssplz_type1
        
    if name == "in2":
        ssplz_flg = config.ssplz_flg2
        ssplz_key = config.ssplz_key2
        ssplz_type= config.ssplz_type2
        
    ssplz_value = value
    if ssplz_type == "analog":
        ssplz_value = cnt[name]
    
    print("ssplz")
    print("flg  : {}".format(ssplz_flg))
    print("key  : {}".format(ssplz_key))
    print("type : {}".format(ssplz_type))
    print("value: {}".format(ssplz_value))
    
    if ssplz_type == "analog":
        if dt.now() - dat[name] > timedelta(seconds=10):
            ssplz_flg = False
        
    if ssplz_flg:
        send_ssplz(ssplz_key, ssplz_value)
    
    row = {
        "datetime": [dt.now()],
        "name": [name],
        "value": [value]
    }
    
    df = pd.concat([df, pd.DataFrame(row)]).reset_index(drop=True)
    
    if pin == 22 and value == 1:
        save_csv_file()
    
    cnt[name] += value
    dat[name] = dt.now()
    print(cnt[name], dat[name])

    #row = [
    #    dt.now(),
    #    name,
    #    value
    #]
    #df.at = row
    
    #print(pd.DataFrame(row).head())
    
    print(df.head())
    
def get_count():

    #global cnt
    #global dat
    #global names
    
    txt = {}
    
    for s in names:
        txt["cnt_{}".format(s)] = cnt[s]
        txt["dat_{}".format(s)] = dat[s].strftime('%Y-%m-%d %H:%M:%S')
        
    txt["now"] = dt.now().strftime('%Y-%m-%d %H:%M:%S')
    txt["message"] = msg

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

# not in use
def send_signal_gae(num):

    global cnt
    global dat
    global payload

    name = {
        "8" : "in1",
        "10": "in2",
        "16": "out1",
        "18": "out2",
        "22": "off"
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

    pin = 16 if num == int(1) else 18
    val = GPIO.HIGH if value == int(1) else GPIO.LOW

    GPIO.output(pin, val)
    print("pin :", pin, " / value:", val)
    
    set_count(pin, value)
    
    #cnt["out{}".format(num)] += value
    #dat["out{}".format(num)] = dt.now()
    
    return True

def callback(pin):

    global msg
    
    #print("button pushed %s"%pin, GPIO.input(pin), dt.now())
    msg = "input changed {} {} {}".format(pin, GPIO.input(pin), dt.now().strftime('%Y-%m-%d %H:%M:%S'))

    if pin == 22:
        
        msg += "stop button pushed."
        #rs = subprocess.run(["/usr/sbin/shutdown", "-h", "now"], timeout=3)
        
        #completed_process = subprocess.run(["/root/ssplz_device/client/run.sh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #completed_process = subprocess.run(["/usr/sbin/shutdown", "-h", "now"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #msg += "returncode: {}".format(completed_process.returncode)
        #msg += "stdout: {}".format(completed_process.stdout)
        #msg += "stderr: {}".format(completed_process.stderr)
        
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
    #GPIO.add_event_detect(22, GPIO.FALLING, callback=callback, bouncetime=300)
    GPIO.add_event_detect(22, GPIO.BOTH, callback=callback, bouncetime=300)

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

    name = request.form["name"]
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

@app.route('/csv')
def output_csv():
    
    save_csv_file()
    
    files = glob("/root/*.csv")
    files.sort()
    print(files)

    filepath = files[-1]
    print(filepath)
    filename = os.path.basename(filepath)
    
    return send_file(filepath, as_attachment=True,
                     attachment_filename=filename,
                     mimetype='text/csv')
                     
    #global df
    
    #text = sys.stdin.read()
    #df.to_csv(sys.stdout,index=False)
    
    #return "csv file saved."
    
@app.route('/control')
def control():

    return render_template('control.html', datetime=dt.now().strftime('%Y-%m-%d_%H%M%S'))

@app.route('/mail')
def mail():
    
    send_mail()
    return "mail"
    
@app.route('/wdt')
def wdt():
    
    send_ssplz_wdt()
    return "wdt"
    
@app.route('/shutdown')
def shutdown():

    return str(cnt["off"])
    

if __name__ == "__main__":
    init()

    try:
        app.run(host='::', port=80, debug=True)

    finally:
        print("terminated")

