#!/bin/sh
# Author: Cristian Gonzales
# CMPS 128

# Port number
PORT=8081

curl -X GET http://localhost:$PORT/kv-store/get_node_details
echo "\n"

curl -X GET http://localhost:$PORT/kv-store/get_all_replicas
echo "\n"
