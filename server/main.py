# need requirements
from flask import Flask, request, jsonify, redirect, render_template

# not requirements
import io
from datetime import datetime as dt
from datetime import timedelta
import json

# initialize

app = Flask(__name__)

types = ["in1", "in2", "out1", "out2"]
signal = {}

signal["status"] = {}

for t in types:
    signal[t] = [
        {
            "datetime": (dt.now() + timedelta(hours=9)).strftime('%Y-%m-%d %H:%M:%S'),
            "value" : 0
        }
    ]
    
    signal["status"][t] = 0

@app.route('/')
def index():
    
    global signal
    
    return jsonify(signal["status"])

@app.route('/update', methods=["POST"])
def update():

    global signal
    
    name = request.form["name"]
    
    if name != "in1":
        dat = (dt.now() + timedelta(hours=9)).strftime('%Y-%m-%d %H:%M:%S')
        value = signal[name][-1]["value"]
        
        data = {
            "datetime": dat,
            "value": value
        }
    
        signal[name].append(data)
    
    dat = (dt.now() + timedelta(hours=9)).strftime('%Y-%m-%d %H:%M:%S')
    value = int(request.form["value"])
    
    data = {
        "datetime": dat,
        "value": value
    }
    
    signal[name].append(data)
    
    if value > 0:
        signal["status"][name] += 1
    
    return now()

@app.route('/datas', methods=["POST"])
def datas():
    
    global signal
    
    name = request.form["name"]
    vals = {
        name: signal[name]
    }
    
    return jsonify(vals)

@app.route('/all')
def all():
    
    global signal
    
    vals = signal
    
    return jsonify(vals)

@app.route('/now')
def now():
    
    global types
    global signal
    
    vals = {}
    
    for t in types:
        vals[t] = signal[t][-1]
    
    return jsonify(vals)

if __name__ == '__main__':

    app.run(host='127.0.0.1', port=8080, debug=True)
