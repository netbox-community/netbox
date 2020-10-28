# Migrating to systemd

This document contains instructions for migrating from a legacy NetBox deployment using [supervisor](http://supervisord.org/) to a systemd-based approach.

## Ubuntu

### Uninstall supervisord

```no-highlight
# apt-get remove -y supervisor
```

### Configure systemd

!!! note
    These instructions assume the presence of a Python virtual environment at `/opt/netbox/venv`. If you have not created this environment, please refer to the [installation instructions](3-netbox.md#set-up-python-environment) for direction.

We'll use systemd to control the daemonization of NetBox services. First, copy `contrib/netbox.service` and `contrib/netbox-rq.service` to the `/etc/systemd/system/` directory:

```no-highlight
# cp contrib/*.service /etc/systemd/system/
```

!!! note
    You may need to modify the user that the systemd service runs as.  Please verify the user for httpd on your specific release and edit both files to match your httpd service under user and group.  The username could be "nobody", "nginx", "apache", "www-data", or something else.

Then, start the `netbox` and `netbox-rq` services and enable them to initiate at boot time:

```no-highlight
# systemctl daemon-reload
# systemctl start netbox netbox-rq
# systemctl enable netbox netbox-rq
```

You can use the command `systemctl status netbox` to verify that the WSGI service is running:

```
# systemctl status netbox.service
● netbox.service - NetBox WSGI Service
   Loaded: loaded (/etc/systemd/system/netbox.service; enabled; vendor preset: enabled)
   Active: active (running) since Sat 2020-10-24 19:23:40 UTC; 25s ago
     Docs: https://netbox.readthedocs.io/en/stable/
 Main PID: 11993 (gunicorn)
    Tasks: 6 (limit: 2362)
   CGroup: /system.slice/netbox.service
           ├─11993 /opt/netbox/venv/bin/python3 /opt/netbox/venv/bin/gunicorn --pid /var/tmp/netbox.pid --pythonpath /opt/netbox/...
           ├─12015 /opt/netbox/venv/bin/python3 /opt/netbox/venv/bin/gunicorn --pid /var/tmp/netbox.pid --pythonpath /opt/netbox/...
           ├─12016 /opt/netbox/venv/bin/python3 /opt/netbox/venv/bin/gunicorn --pid /var/tmp/netbox.pid --pythonpath /opt/netbox/...
...
```

At this point, you should be able to connect to the HTTP service at the server name or IP address you provided. If you are unable to connect, check that the nginx service is running and properly configured. If you receive a 502 (bad gateway) error, this indicates that gunicorn is misconfigured or not running. Issue the command `journalctl -xe` to see why the services were unable to start.

!!! info
    Please keep in mind that the configurations provided here are bare minimums required to get NetBox up and running. You may want to make adjustments to better suit your production environment.
