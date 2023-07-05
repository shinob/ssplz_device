#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import ssl
import time
import requests

import config

def set_output_api(num, value):

    url = "http://localhost/output"
    
    payload = {
        "num": num,
        "val": value
    }

    try:
        res = requests.post(url, data=payload, timeout=1.0)
        
        if value == 1:
            time.sleep(1)
            set_output_api(num, 0)
        
        #print(res.text)
        
    except:
        print("not working.")

# MQTTブローカーに接続したときに呼ばれるコールバック関数
def on_connect(client, userdata, flags, rc):
	
    print("Connected with result code " + str(rc))
    
    # 接続が確立したら、"test/topic"というトピックにサブスクライブする
    client.subscribe(config.mqtt_topic)
    #client.publish("/test", "Hello, MQTT!")

# メッセージを受信したときに呼ばれるコールバック関数
def on_message(client, userdata, msg):

    #print(msg.topic + " " + str(msg.payload))
    cmd = str(msg.payload)
    print(cmd)
    
    num = 1
    for out in ["out1", "out2"]:
        if out in cmd:
            if "on" in cmd:
                value = 1
            else:
                value = 0
                
            set_output_api(num, value)
        num += 1

# MQTTクライアントの作成
client = mqtt.Client()

# SSL/TLSを使用するための設定
client.tls_set(ca_certs='/etc/ssl/certs/isrgrootx1.pem', certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)

# ユーザー名とパスワードの設定
client.username_pw_set(config.mqtt_user, config.mqtt_passwd)

# 接続時およびメッセージ受信時のコールバック関数を設定
client.on_connect = on_connect
client.on_message = on_message

# MQTTブローカーに接続する
client.connect(config.mqtt_url, 1883, 60)

#print("dksk")

# MQTTのネットワーキングループを開始する
client.loop_start()

#wait to allow publish and logging and exit
#time.sleep(1)

try:
    while True:
        time.sleep(1)
        pass
except KeyboardInterrupt:
    pass

client.loop_stop()
client.disconnect()

print("Finished")
