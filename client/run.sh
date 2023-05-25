#!/usr/bin/env bash

#echo "test"

URL="http://localhost/shutdown"

while true
do
	x=$(curl -X GET $URL)
	x=$((x*1))

	if [ $x -gt 0 ] ; then
		echo "off"
		/usr/sbin/shutdown -h now
	else
		echo "on"
	fi
	
	sleep 10
done

#echo $?