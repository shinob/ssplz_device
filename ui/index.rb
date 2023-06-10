#!/usr/bin/env ruby

require 'uri'
require 'net/http'
require "json"

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
		<title>カシマ電脳基地</title>
	</head>
	<style>
* {
	margin: 0px;
	padding: 0px;
}
h1 {
	text-align: center;
	border: 0px solid #666;
}
table {
	border: 2px solid #666;
	border-collapse: collapse;
	margin: 10px auto;
}
th, td {
	border: 1px solid #666;
	padding: 5px;
}
td.value {
	text-align: right;
}
	</style>
	<body>
		<h1>カシマ電脳基地</h1>
		<table>
		<tr>
			<th>名称</th>
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
			<td>#{val[0]}</td>
			<td class="value">#{val[1]}</td>
		</tr>
EOF
end

puts <<EOF
		</table>
	</body>
</html>
EOF

#puts res.body if res.is_a?(Net::HTTPSuccess)

