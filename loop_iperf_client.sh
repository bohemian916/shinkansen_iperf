#!/bin/bash
if [ $# -ne 1 ];
then
        echo "few arguments: $#"
        echo "example: ./start_iperf_server.sh 127.0.0.1"
       
fi

ip=$1
while true
do
     iperf3 -c $ip -u -t 15000 -b 10M 
    sleep 1
done
