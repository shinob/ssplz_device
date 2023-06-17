#!/usr/bin/env bash

# crontab -e
# 0 0 * * * /root/ssplz_device/client/csv.sh

URL="http://localhost/csv"

x=$(curl -s -X GET $URL)

#echo $x
echo "done."