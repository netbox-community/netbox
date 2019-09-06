# Migration

Migration is not required, as supervisord will still continue to function.

## Ubuntu

### Remove supervisord:

```no-highlight
# apt-get remove -y supervisord
```

### systemd configuration:

Copy or link contrib/netbox.service and contrib/netbox-rq.service to /etc/systemd/system/netbox.service and /etc/systemd/system/netbox-rq.service

```no-highlight
# cp contrib/netbox.service /etc/systemd/system/netbox.service
# cp contrib/netbox-rq.service /etc/systemd/system/netbox-rq.service
```

Edit /etc/systemd/system/netbox.service and /etc/systemd/system/netbox-rq.service. Be sure to verify the location of the gunicorn executable on your server (e.g. `which gunicorn`).  If using CentOS/RHEL.  Change the username from `www-data` to `nginx` or `apache`:

```no-highlight
/usr/local/bin/gunicorn --pid ${PidPath} --pythonpath ${WorkingDirectory}/netbox --config ${ConfigPath} netbox.wsgi
```

```no-highlight
User=www-data
Group=www-data
```

Copy contrib/netbox.env to /etc/sysconfig/netbox.env

```no-highlight
# cp contrib/netbox.env /etc/sysconfig/netbox.env
```

Edit /etc/sysconfig/netbox.env and change the settings as required.  Update the `WorkingDirectory` variable if needed.

```no-highlight
# Name is the Process Name
#
Name = 'Netbox'

# ConfigPath is the path to the gunicorn config file.
#
ConfigPath=/opt/netbox/gunicorn.conf

# WorkingDirectory is the Working Directory for Netbox.
#
WorkingDirectory=/opt/netbox/

# PidPath is the path to the pid for the netbox WSGI
#
PidPath=/var/run/netbox.pid
```

Copy contrib/gunicorn.conf to gunicorn.conf

```no-highlight
# cp contrib/gunicorn.conf to gunicorn.conf
```

Edit gunicorn.conf and change the settings as required.

```
# Bind is the ip and port that the Netbox WSGI should bind to
#
bind='127.0.0.1:8001'

# Workers is the number of workers that GUnicorn should spawn.
# Workers should be: cores * 2 + 1.  So if you have 8 cores, it would be 17.
#
workers=3

# Threads
#     The number of threads for handling requests
#
threads=3

# Timeout is the timeout between gunicorn receiving a request and returning a response (or failing with a 500 error)
#
timeout=120

# ErrorLog
#     ErrorLog is the logfile for the ErrorLog
#
errorlog='/opt/netbox/netbox.log'
```

Then, restart the systemd daemon service to detect the netbox service and start the netbox service:

```no-highlight
# systemctl daemon-reload
# systemctl start netbox.service
# systemctl enable netbox.service
```

If using webhooks, also start the Redis worker:

```no-highlight
# systemctl start netbox-rq.service
# systemctl enable netbox-rq.service
```