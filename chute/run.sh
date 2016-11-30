#!/bin/bash

# Create the image cache directory
mkdir -p /var/www/html/motionLog
chmod a+rw /var/www/html/motionLog

# Execute the file, one pic every 10 ms
python /usr/local/bin/TestServer_v2.py &

# Allow client traffic for development
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

# Add the symlink
ln -s --relative /var/www/html/motionLog /var/www/html/app-dist/

# Allow client traffic for development
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

# Enable mod rewrite
/usr/sbin/a2enmod rewrite

# Make sure apache2 is running and rewrite is enabled
/etc/init.d/apache2 restart

# Run photo server
/usr/bin/nodejs photo-server.js > photo-server.log 2> photo-server.err &

while true; do
    sleep 300
done

# If execution reaches this point, the chute will stop running.
exit 0
