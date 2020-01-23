# Migration

Migration is not required, as supervisord will still continue to function.

## Ubuntu

### Remove supervisord:

```no-highlight
# apt-get remove -y supervisord
```

### systemd configuration:

Copy or link `contrib/netbox.service` and `contrib/netbox-rq.service` to the `/etc/systemd/system/` directory:

```no-highlight
# cp contrib/*.service /etc/systemd/system/
```

!!! note
    These service files assume that gunicorn is installed at `/usr/local/bin/gunicorn`. If the output of `which gunicorn` indicates a different path, you'll need to correct the `ExecStart` path in both files.

Copy `contrib/gunicorn.py` to `/opt/netbox/gunicorn.py`. We make a copy of this file to ensure that any changes to it do not get overwritten by a future upgrade.

```no-highlight
# cp contrib/gunicorn.py /opt/netbox/gunicorn.py
```

You may wish to edit this file to change the bound IP address or port number, or to make performance-related adjustments.

Finally, start the `netbox` and `netbox-rq` services and enable them to initiate at boot time:

```no-highlight
# systemctl daemon-reload
# systemctl start netbox.service
# systemctl start netbox-rq.service
# systemctl enable netbox.service
# systemctl enable netbox-rq.service
```

You can use the command `systemctl status netbox` to verify that the WSGI service is running:

```
# systemctl status netbox.service
● netbox.service - NetBox WSGI Service
   Loaded: loaded (/etc/systemd/system/netbox.service; enabled; vendor preset: enabled)
   Active: active (running) since Thu 2019-12-12 19:23:40 UTC; 25s ago
     Docs: https://netbox.readthedocs.io/en/stable/
 Main PID: 11993 (gunicorn)
    Tasks: 6 (limit: 2362)
   CGroup: /system.slice/netbox.service
           ├─11993 /usr/bin/python3 /usr/local/bin/gunicorn --pid /var/tmp/netbox.pid --pythonpath /opt/netbox/...
           ├─12015 /usr/bin/python3 /usr/local/bin/gunicorn --pid /var/tmp/netbox.pid --pythonpath /opt/netbox/...
           ├─12016 /usr/bin/python3 /usr/local/bin/gunicorn --pid /var/tmp/netbox.pid --pythonpath /opt/netbox/...
...
```
