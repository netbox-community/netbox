# Gunicorn

Like most Django applications, NetBox runs as a [WSGI application](https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface) behind an HTTP server. This documentation shows how to install and configure [gunicorn](http://gunicorn.org/) (which is automatically installed with NetBox) for this role, however other WSGI servers are available and should work similarly well. [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/) is a popular alternative.

## Configuration

NetBox ships with a default configuration file for gunicorn. To use it, copy `/opt/netbox/contrib/gunicorn.py` to `/opt/netbox/gunicorn.py`. (We make a copy of this file rather than pointing to it directly to ensure that any local changes to it do not get overwritten by a future upgrade.)

```no-highlight
sudo cp /opt/netbox/contrib/gunicorn.py /opt/netbox/gunicorn.py
```

While the provided configuration should suffice for most initial installations, you may wish to edit this file to change the bound IP address and/or port number, or to make performance-related adjustments. See [the Gunicorn documentation](https://docs.gunicorn.org/en/stable/configure.html) for the available configuration parameters.

## systemd Setup

We'll use systemd to control both gunicorn and NetBox's background worker process. First, copy `contrib/netbox.service` and `contrib/netbox-rq.service` to the `/etc/systemd/system/` directory and reload the systemd dameon:

```no-highlight
sudo cp -v /opt/netbox/contrib/*.service /etc/systemd/system/
sudo systemctl daemon-reload
```

Then, start the `netbox` and `netbox-rq` services and enable them to initiate at boot time:

```no-highlight
sudo systemctl start netbox netbox-rq
sudo systemctl enable netbox netbox-rq
```

You can use the command `systemctl status netbox` to verify that the WSGI service is running:

```no-highlight
# systemctl status netbox.service
● netbox.service - NetBox WSGI Service
     Loaded: loaded (/etc/systemd/system/netbox.service; enabled; vendor preset: enabled)
     Active: active (running) since Tue 2020-11-17 16:18:23 UTC; 3min 35s ago
       Docs: https://netbox.readthedocs.io/en/stable/
   Main PID: 22836 (gunicorn)
      Tasks: 6 (limit: 2345)
     Memory: 339.3M
     CGroup: /system.slice/netbox.service
             ├─22836 /opt/netbox/venv/bin/python3 /opt/netbox/venv/bin/gunicorn --pid>
             ├─22854 /opt/netbox/venv/bin/python3 /opt/netbox/venv/bin/gunicorn --pid>
             ├─22855 /opt/netbox/venv/bin/python3 /opt/netbox/venv/bin/gunicorn --pid>
...
```

!!! note
    If the NetBox service fails to start, issue the command `journalctl -eu netbox` to check for log messages that may indicate the problem.

Once you've verified that the WSGI workers are up and running, move on to HTTP server setup.
