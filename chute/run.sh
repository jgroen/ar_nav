#!/bin/bash

# Execute the file, one pic every 10 ms
python /usr/local/bin/TestServer_v10.py > TestServer_v10.log 2> TestServer_v10.err &

# Allow client traffic for development
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

while true; do
    sleep 300
done

# If execution reaches this point, the chute will stop running.
exit 0
