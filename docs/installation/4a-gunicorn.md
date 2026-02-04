# Gunicorn

!!! tip
    This page provides instructions for setting up the [gunicorn](http://gunicorn.org/) WSGI server. If you plan to use [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/) instead, go [here](./4b-uwsgi.md).

NetBox runs as a [WSGI application](https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface) behind an HTTP server. This documentation shows how to install and configure [gunicorn](http://gunicorn.org/) (which is automatically installed with NetBox) for this role, however other WSGI servers are available and should work similarly well.

## Configuration

NetBox ships with a default configuration file for gunicorn. To use it, copy `/opt/netbox/contrib/gunicorn.py` to `/opt/netbox/gunicorn.py`. (We make a copy of this file rather than pointing to it directly to ensure that any local changes to it do not get overwritten during a future NetBox upgrade.)

```no-highlight
sudo cp /opt/netbox/contrib/gunicorn.py /opt/netbox/gunicorn.py
```

While the provided configuration should suffice for most initial installations, you may wish to edit this file to change the bound IP address and/or port number, or to make performance-related adjustments. See [the Gunicorn documentation](https://docs.gunicorn.org/en/stable/configure.html) for the available configuration parameters.

## systemd Setup

We'll use systemd to control both gunicorn and NetBox's background worker process. First, copy `contrib/netbox.service` and `contrib/netbox-rq.service` to the `/etc/systemd/system/` directory and reload the systemd daemon.

!!! warning "Check user & group assignment"
    The stock service configuration files packaged with NetBox assume that the service will run with the `netbox` user and group names. If these differ on your installation, be sure to update the service files accordingly.

```no-highlight
sudo cp -v /opt/netbox/contrib/*.service /etc/systemd/system/
sudo systemctl daemon-reload
```

Then, start the `netbox` and `netbox-rq` services and enable them to initiate at boot time:

```no-highlight
sudo systemctl enable --now netbox netbox-rq
```

You can use the command `systemctl status netbox` to verify that the WSGI service is running:

```no-highlight
systemctl status netbox.service
```

You should see output similar to the following:

```no-highlight
● netbox.service - NetBox WSGI Service
     Loaded: loaded (/etc/systemd/system/netbox.service; enabled; preset: enabled)
     Active: active (running) since Mon 2026-01-26 11:00:00 CST; 7s ago
       Docs: https://docs.netbox.dev/
   Main PID: 7283 (gunicorn)
      Tasks: 6 (limit: 4545)
     Memory: 556.1M (peak: 556.3M)
        CPU: 3.387s
     CGroup: /system.slice/netbox.service
             ├─7283 /opt/netbox/venv/bin/python3 /opt/netbox/venv/bin/gunicorn --pid /var/tmp/netbox.pid --pythonpath /opt/netbox/netbox>
             ├─7285 /opt/netbox/venv/bin/python3 /opt/netbox/venv/bin/gunicorn --pid /var/tmp/netbox.pid --pythonpath /opt/netbox/netbox>
             ├─7286 /opt/netbox/venv/bin/python3 /opt/netbox/venv/bin/gunicorn --pid /var/tmp/netbox.pid --pythonpath /opt/netbox/netbox>
             ├─7287 /opt/netbox/venv/bin/python3 /opt/netbox/venv/bin/gunicorn --pid /var/tmp/netbox.pid --pythonpath /opt/netbox/netbox>
             ├─7288 /opt/netbox/venv/bin/python3 /opt/netbox/venv/bin/gunicorn --pid /var/tmp/netbox.pid --pythonpath /opt/netbox/netbox>
             └─7289 /opt/netbox/venv/bin/python3 /opt/netbox/venv/bin/gunicorn --pid /var/tmp/netbox.pid --pythonpath /opt/netbox/netbox>

Jan 26 11:00:00 netbox systemd[1]: Started netbox.service - NetBox WSGI Service.
...
```

!!! note
    If the NetBox service fails to start, issue the command `journalctl -eu netbox` to check for log messages that may indicate the problem.

Once you've verified that the WSGI workers are up and running, move on to HTTP server setup.
