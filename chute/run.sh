#!/bin/bash

# Create the image cache directory
mkdir -p /var/www/html/CPs
chmod a+rw /var/www/html/CPs

# Execute the file, one pic every 10 ms
python /usr/local/bin/ar_nav_2.py -m_sec 10 > seccam.log 2> seccam.err &

# Add the symlink
ln -s --relative /var/www/html/CPs /var/www/html/app-dist/

# Allow client traffic for development
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

# Enable mod rewrite
/usr/sbin/a2enmod rewrite

while true; do
    sleep 300
done

# If execution reaches this point, the chute will stop running.
exit 0
