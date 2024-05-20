# uWSGI

!!! tip
    This page provides instructions for setting up the [uWSGI](https://uwsgi-docs.readthedocs.io/) WSGI server. If you plan to use [gunicorn](http://gunicorn.org/) instead, go [here](./4a-gunicorn.md).

NetBox runs as a [WSGI application](https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface) behind an HTTP server. This documentation shows how to install and configure [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/) for this role, however other WSGI servers are available and should work similarly well.

## Installation

Activate the Python virtual environment and install the `pyuwsgi` package using pip:

```no-highlight
source /opt/netbox/venv/bin/activate
pip3 install pyuwsgi
```

Once installed, add the package to `local_requirements.txt` to ensure it is re-installed during future rebuilds of the virtual environment:

```no-highlight
sudo sh -c "echo 'pyuwsgi' >> /opt/netbox/local_requirements.txt"
```

## Configuration

NetBox ships with a default configuration file for uWSGI. To use it, copy `/opt/netbox/contrib/uwsgi.ini` to `/opt/netbox/uwsgi.ini`. (We make a copy of this file rather than pointing to it directly to ensure that any local changes to it do not get overwritten during a future NetBox upgrade.)

```no-highlight
sudo cp /opt/netbox/contrib/uwsgi.ini /opt/netbox/uwsgi.ini
```

While the provided configuration should suffice for most initial installations, you may wish to edit this file to change the bound IP address and/or port number, or to make performance-related adjustments. See [the uWSGI documentation](https://uwsgi-docs-additions.readthedocs.io/en/latest/Options.html) for the available configuration parameters and take a minute to review the [Things to know](https://uwsgi-docs.readthedocs.io/en/latest/ThingsToKnow.html) page. Django also provides [additional documentation](https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/uwsgi/) on configuring uWSGI with a Django app.

## systemd Setup

We'll use systemd to control both uWSGI and NetBox's background worker process. First, copy `contrib/netbox.service` and `contrib/netbox-rq.service` to the `/etc/systemd/system/` directory.

```no-highlight
sudo cp -v /opt/netbox/contrib/*.service /etc/systemd/system/
sudo systemctl daemon-reload
```

The reference configuration assumes that gunicorn is in use, so we need to update it. Edit the `netbox.service` file to remove the line beginning with `ExecStart=/opt/netbox/venv/bin/gunicorn` and uncomment the line below it.

!!! warning "Check user & group assignment"
    The stock service configuration files packaged with NetBox assume that the service will run with the `netbox` user and group names. If these differ on your installation, be sure to update the service files accordingly.

Once the configuration file has been saved, reload the service:

```no-highlight
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
     Loaded: loaded (/etc/systemd/system/netbox.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2021-08-30 04:02:36 UTC; 14h ago
       Docs: https://docs.netbox.dev/
   Main PID: 1140492 (uwsgi)
      Tasks: 19 (limit: 4683)
     Memory: 666.2M
     CGroup: /system.slice/netbox.service
             ├─1061 /opt/netbox/venv/bin/python3 /opt/netbox/venv/bin/uwsgi --ini /opt/netbox/uwsgi.ini
             ├─1976 /opt/netbox/venv/bin/python3 /opt/netbox/venv/bin/uwsgi --ini /opt/netbox/uwsgi.ini
...
```

!!! note
    If the NetBox service fails to start, issue the command `journalctl -eu netbox` to check for log messages that may indicate the problem.

Once you've verified that the WSGI workers are up and running, move on to HTTP server setup.

## HTTP Server Installation

For server installation, you will want to follow the NetBox [HTTP Server Setup](5-http-server.md) guide, however after copying the configuration file, you will need to edit the file and change the `location` section to uncomment the uWSGI parameters:

```no-highlight
    location / {
        # proxy_pass http://127.0.0.1:8001;
        # proxy_set_header X-Forwarded-Host $http_host;
        # proxy_set_header X-Real-IP $remote_addr;
        # proxy_set_header X-Forwarded-Proto $scheme;
        # comment the lines above and uncomment the lines below if using uWSGI
        include uwsgi_params;
        uwsgi_pass  127.0.0.1:8001;
        uwsgi_param Host $host;
        uwsgi_param X-Real-IP $remote_addr;
        uwsgi_param X-Forwarded-For $proxy_add_x_forwarded_for;
        uwsgi_param X-Forwarded-Proto $http_x_forwarded_proto;
    }
```
