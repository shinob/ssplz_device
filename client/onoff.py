#!/usr/bin/env python3

#@reboot /root/ssplz_device/client/onoff.py

import asyncio

from datetime import datetime as dt
from datetime import timedelta
import time

import requests

def set_output_api(num, value):

    url = "http://localhost/output"
    
    payload = {
        "num": num,
        "val": value
    }

    try:
        res = requests.post(url, data=payload, timeout=1.0)
        #print(res.text)
        
    except:
        print("not working.")
    
async def main():

    i = 0
    d = dt.now()

    while (dt.now() - d) < timedelta(days=1) :
    #while (dt.now() - d) < timedelta(minutes=1) :

        i += 1
        #print("{} : {}".format(i, dt.now() - d))

        time.sleep(5)
        set_output_api(1,1)
        print("{} ON : {}".format(i, dt.now() - d))

        #time.sleep(60 * 3)
        time.sleep(10)
        set_output_api(1,0)
        print("{} OFF: {}".format(i, dt.now() - d))

        #output_by_hour(20, 1)
        #time.sleep(10)

    
#loop = asyncio.get_event_loop()
#loop.run_until_complete(make_request())

asyncio.run(main())
