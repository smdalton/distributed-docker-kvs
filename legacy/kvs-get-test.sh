#!/bin/sh

PORT=8080

#put a value and then get it back
curl -X PUT 127.0.0.1:$PORT/kv-store/test -d val=cheese
echo "\n"

curl -X GET 127.0.0.1:$PORT/kv-store/test
echo "\n"

#put the value again and check to see if the clock increments
echo "Clock should increment here \n"
curl -X PUT 127.0.0.1:$PORT/kv-store/test -d val=cheese1 -d causal_payload="0"

curl -X PUT 127.0.0.1:$PORT/kv-store/test -d val=cheese1 -d causal_payload="1"

