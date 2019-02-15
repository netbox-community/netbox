# Migration

## Ubuntu

### Remove supervisord:

```no-highlight
# apt-get remove -y supervisord
```

### systemd configuration:

Copy or link contrib/netbox.service and contrib/netbox-rq.service to /etc/systemd/system/netbox.service and /etc/systemd/system/netbox-rq.service

```no-highlight
# copy contrib/netbox.service to /etc/systemd/system/netbox.service
# copy contrib/netbox-rq.service to /etc/systemd/system/netbox-rq.service
```

Edit /etc/systemd/system/netbox.service and /etc/systemd/system/netbox-rq.service. Be sure to verify the location of the gunicorn executable on your server (e.g. `which gunicorn`).  If using CentOS/RHEL.  Change the username from `www-data` to `nginx` or `apache`:

```no-highlight
/usr/bin/gunicorn --pid ${PidPath} --bind ${Bind} --workers ${Workers} --threads ${Threads} --timeout ${Timeout} --error-log ${ErrorLog} --pythonpath ${WorkingDirectory}/netbox ${ExtraArgs} netbox.wsgi
```

```no-highlight
User=www-data
Group=www-data
```

Copy contrib/netbox.env to /etc/sysconfig/netbox.env

```no-highlight
# mkdir /etc/sysconfig/netbox.env
# copy contrib/netbox.env to /etc/sysconfig/netbox.env
```

Edit /etc/sysconfig/netbox.env and change the settings as required.  Update the `WorkingDirectory` variable if needed.

```no-highlight
# Name is the Process Name
#
Name = 'Netbox'

# GUExec is the gunicorn executable path
#
GUExec=/bin/gunicorn

# WorkingDirectory is the Working Directory for Netbox.
#
WorkingDirectory=/usr/local/netbox/

# PidPath is the path to the pid for the netbox WSGI
#
PidPath=/var/run/netbox.pid

# Bind is the ip and port that the Netbox WSGI should bind to
#
Bind='127.0.0.1:8001'

# Workers is the number of workers that GUnicorn should spawn.
# Workers should be: cores * 2 + 1.  So if you have 8 cores, it would be 17.
#
Workers=3

# Threads
#     The number of threads for handling requests
#
Threads=3

# Timeout is the timeout
#
Timeout=120

# ErrorLog
#     ErrorLog is the logfile for the ErrorLog
#
ErrorLog='/usr/local/netbox/netbox.log'

# ExtraArgs
#    ExtraArgs is a string of extra arguments for Gunicorn
#
ExtraArgs='--capture-output'
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