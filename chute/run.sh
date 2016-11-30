#!/bin/bash

# Create the image cache directory
mkdir -p /var/www/html/CPs
chmod a+rw /var/www/html/CPs

# Execute the file, one pic every 10 ms
python /usr/local/bin/TestServer_v2.py &

# Allow client traffic for development
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

while true; do
    sleep 300
done

# If execution reaches this point, the chute will stop running.
exit 0
