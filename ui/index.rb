#!/usr/bin/env ruby

require 'mqtt'

require 'uri'
require 'net/http'
require "json"
require 'time'
require 'date'

load "config.rb"

def get_data(key)
  
  uri = URI('https://ssplz.ittools.biz/api/download')
  params = {
    :mailaddress => $ssplz_mail,
    :sensorkey => key,
  }
  
  uri.query = URI.encode_www_form(params)
  #puts uri
  
  res = Net::HTTP.get_response(uri)
  #puts res.body

  hash = JSON.parse(res.body)
  #p hash

  #p hash["datetime"]
  #p hash["data"][$ssplz_key]
  return [hash["datetime"], hash["data"][key]]

end

host = $ssplz_mqtt[:host]
port = $ssplz_mqtt[:port]
username = $ssplz_mqtt[:username]
password = $ssplz_mqtt[:password]
pem_file = $ssplz_mqtt[:pem_file]
topic = $ssplz_mqtt[:topic]

# Connect to the MQTT server
client = MQTT::Client.new(host: host, port: port, username: username, password: password, ssl: true, cert_file: pem_file)
client.connect

message = 'out1 on'
client.publish(topic, message)

sleep(1)

message = "out1 off"
client.publish(topic, message)

# Disconnect from the MQTT server
client.disconnect

puts "Content-type: text/html; charset=UTF-8\n\n"

puts <<EOF
<html>
	<head>
		<meta name="viewport" content="width=device-width, initial-scale=1.0">
		<title>古民家DX</title>
	</head>
	<style>
* {
	margin: 0px;
	padding: 0px;
	font-size: 10pt;
}
h1 {
	text-align: center;
	border: 0px solid #666;
	line-height: 250%;
	font-size: 24pt;
}
div.img_box {
	width: 90%;
	border: 0px solid #F00;
	margin: 0px auto;	
}
img {
	width: 100%;
}
table.data {
	border: 3px solid #666;
	border-collapse: collapse;
	margin: 0px auto 10px;
	width: 90%;
}
table.data th {
	border: 1px solid #666;
	padding: 5px;
	background-color: #DDD;
}
table.data td {
	border: 1px solid #666;
	padding: 5px;
}
td.datetime {
	text-align: center;
	width: 150px;
}
td.value {
	text-align: right;
	width: 50px;
}
td.status {
	text-align: center;
	width: 50px;
}
#page {
	width: 800px;
	margin: 0px auto;
}
@media (max-width: 800px) {
  #page {
    width: 100%;
  }
}
.err {
	background-color: #F66;
}
	</style>
	<body>
		<div id="page">
		<h1>古民家DX</h1>
		<div class="img_box">
			<img src="imgs/layout.gif" />
		</div>
		<table class="data">
		<tr>
			<th>センサー</th>
			<th>最終更新日時</th>
			<th>値</th>
		</tr>
EOF


$ssplz_key.each do |snc|
  #puts snc
  
  name = snc[:name]
  key = snc[:key]
  #puts name, key

  val = get_data(key)

  puts <<EOF
		<tr>
			<td>#{name}</td>
			<td class="datetime">#{val[0]}</td>
			<td class="value">#{val[1]}</td>
		</tr>
EOF
end

puts <<EOF
		</table>
		<table class="data">
		<tr>
			<th>WDT</th>
			<th>最終更新日時</th>
			<th>状態</th>
		</tr>
EOF

$ssplz_wdt.each do |snc|
  #puts snc
  
  name = snc[:name]
  key = snc[:key]
  #puts name, key

  val = get_data(key)
  
  status = "正常"
  css = ""
  #puts val[0]
  
  val[0] = Time.strptime(val[0], "%Y-%m-%d %H:%M:%S")
  
  if Time.now - val[0] >= 90 then
    status = "異常"
    css = "class='err'"
  end
  
  puts <<EOF
		<tr #{css}>
			<td>#{name}</td>
			<td class="datetime">#{val[0].strftime('%Y-%m-%d %H:%M:%S')}</td>
			<td class="status">#{status}</td>
		</tr>
EOF
end

puts <<EOF
		</table>
		</div>
<!--
		<iframe width="100%" height="315" src="https://www.youtube.com/embed/stQzZ9hpl-Q?controls=0" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
-->
	</body>
</html>
EOF

#puts res.body if res.is_a?(Net::HTTPSuccess)

