#!/bin/sh

# 1. Install Nginx Unit from https://unit.nginx.org/installation/ before running this.
# 2. Check the other files to replace the "netbox" user, if using "www-data" or something else.
# 3. chmod u+rx nunit-redis-install.sh && sudo ./nunit-redis-install.sh

# Remove supervisord & gunicorn, if only used for NetBox
# apt remove supervisor gunicorn -y && apt autoremove -y

# Load Redis Worker service
cp -f netbox-rqworker.service /etc/systemd/system/
systemctl enable netbox-rqworker && systemctl restart netbox-rqworker

# Load NUnit config
systemctl enable unit && systemctl restart unit
sudo apt install curl -y
sudo curl -X PUT -d @netbox-unit.json --unix-socket /var/control.unit.sock http://localhost/config/
