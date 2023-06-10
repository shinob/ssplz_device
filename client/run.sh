#!/usr/bin/env bash

#echo "test"

WDT_URL="http://localhost/wdt"
ALG_URL="http://localhost/analog"
SHD_URL="http://localhost/shutdown"
i=1
j=1

while true
do
	echo $i
	i=$((i+1))
	j=$((j+1))

	# Watch dog timer
	if [ $i -gt 6 ] ; then
		x=$(curl -s -X GET $WDT_URL)
		echo $x
		i=0
	fi

	# Analog data update
	if [ $j -gt 3 ] ; then
		x=$(curl -s -X GET $ALG_URL)
		echo $x
		j=0
	fi
	
	# Watch shutdown counter
	x=$(curl -s -X GET $SHD_URL)
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
