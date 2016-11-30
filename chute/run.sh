#!/bin/bash

# Execute the file, one pic every 10 ms
python /usr/local/bin/TestServer_v2.py &

# Allow client traffic for development
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

# Enable mod rewrite
/usr/sbin/a2enmod rewrite

while true; do
    sleep 300
done

# If execution reaches this point, the chute will stop running.
exit 0
