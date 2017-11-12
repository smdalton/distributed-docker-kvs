#!/bin/bash
#Shane Dalton CMPS128
#Initializes all servers
#listed in the ports list
cd ..
echo "test"
echo "From server:"
num_servers=$1
echo $num_servers
K=4
VIEW="10.0.0.21:8080,10.0.0.22:8080,10.0.0.23:8080,10.0.0.24:8080"
#starting port range
port=5000
for i in $(seq 1 $num_servers)		#"${ports[@]}"
do
	
	echo "Raising server at localhost:$port"
	python3 server1.py $K $VIEW localhost:$port &
	let "port=port+1"
done 