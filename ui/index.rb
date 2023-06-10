#!/usr/bin/env ruby

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
}
h1 {
	text-align: center;
	border: 0px solid #666;
	line-height: 250%;
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
.err {
	background-color: #F66;
}
	</style>
	<body>
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
	</body>
</html>
EOF

#puts res.body if res.is_a?(Net::HTTPSuccess)

