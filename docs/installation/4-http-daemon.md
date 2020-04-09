# HTTP Server Setup

We'll set up a simple WSGI front end using [gunicorn](http://gunicorn.org/) for the purposes of this guide. For web servers, we provide example configurations for both [nginx](https://www.nginx.com/resources/wiki/) and [Apache](http://httpd.apache.org/docs/2.4). (You are of course free to use whichever combination of HTTP and WSGI services you'd like.) We'll use systemd to enable service persistence.

!!! info
    For the sake of brevity, only Ubuntu 18.04 instructions are provided here, but this sort of web server and WSGI configuration is not unique to NetBox. Please consult your distribution's documentation for assistance if needed.

## Obtain an SSL Certificate

To enable HTTPS access to NetBox, you'll need a valid SSL certificate. You can purchase one from a trusted commercial provider, obtain one for free from [Let's Encrypt](https://letsencrypt.org/getting-started/), or generate your own (although self-signed certificates are generally untrusted). Both the public certificate and private key files need to be installed on your NetBox server in a location that is readable by the `netbox` user.

The command below can be used to generate a self-signed certificate for testing purposes, however it is strongly recommended to use a certificate from a trusted authority in production. Two files will be created: the public certificate (`netbox.crt`) and the private key (`netbox.key`). The certificate is published to the world, whereas the private key must be kept secret at all times.

```no-highlight
# openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
-keyout /etc/ssl/private/netbox.key \
-out /etc/ssl/certs/netbox.crt
```

## HTTP Daemon Installation

### Option A: nginx

The following will serve as a minimal nginx configuration. Be sure to modify your server name and installation path appropriately.

```no-highlight
# apt-get install -y nginx
```

Once nginx is installed, copy the default nginx configuration file to `/etc/nginx/sites-available/netbox`. Be sure to replace `netbox.example.com` with the domain name or IP address of your installation. (This should match the value configured for `ALLOWED_HOSTS` in `configuration.py`.)

```no-highlight
# cp /opt/netbox/contrib/nginx.conf /etc/nginx/sites-available/netbox
```

Then, delete `/etc/nginx/sites-enabled/default` and create a symlink in the `sites-enabled` directory to the configuration file you just created.

```no-highlight
# cd /etc/nginx/sites-enabled/
# rm default
# ln -s /etc/nginx/sites-available/netbox
```

Finally, restart the `nginx` service to use the new configuration.

```no-highlight
# service nginx restart
```

### Option B: Apache

Begin by installing Apache:

```no-highlight
# apt-get install -y apache2
```

Next, copy the default configuration file to `/etc/apache2/sites-available/`. Be sure to modify the `ServerName` parameter appropriately.

```no-highlight
# cp /opt/netbox/contrib/apache.conf /etc/apache2/sites-available/netbox.conf
```

Finally, ensure that the required Apache modules are enabled, enable the `netbox` site, and reload Apache:

```no-highlight
# a2enmod ssl proxy proxy_http headers
# a2ensite netbox
# service apache2 restart
```

!!! note
    Certain components of NetBox (such as the display of rack elevation diagrams) rely on the use of embedded objects. Ensure that your HTTP server configuration does not override the `X-Frame-Options` response header set by NetBox.

## Gunicorn Configuration

Copy `/opt/netbox/contrib/gunicorn.py` to `/opt/netbox/gunicorn.py`. (We make a copy of this file to ensure that any changes to it do not get overwritten by a future upgrade.)

```no-highlight
# cd /opt/netbox
# cp contrib/gunicorn.py /opt/netbox/gunicorn.py
```

You may wish to edit this file to change the bound IP address or port number, or to make performance-related adjustments. See [the Gunicorn documentation](https://docs.gunicorn.org/en/stable/configure.html) for the available configuration parameters.

## systemd Configuration

We'll use systemd to control the daemonization of NetBox services. First, copy `contrib/netbox.service` and `contrib/netbox-rq.service` to the `/etc/systemd/system/` directory:

```no-highlight
# cp contrib/*.service /etc/systemd/system/
```

Then, start the `netbox` and `netbox-rq` services and enable them to initiate at boot time:

```no-highlight
# systemctl daemon-reload
# systemctl start netbox netbox-rq
# systemctl enable netbox netbox-rq
```

You can use the command `systemctl status netbox` to verify that the WSGI service is running:

```no-highlight
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

At this point, you should be able to connect to the HTTP service at the server name or IP address you provided.

!!! info
    Please keep in mind that the configurations provided here are bare minimums required to get NetBox up and running. You may want to make adjustments to better suit your production environment.

## Troubleshooting

If you are unable to connect to the HTTP server, check that:

* Nginx/Apache is running and configured to listen on the correct port.
* Access is not being blocked by a firewall. (Try connecting locally from the server itself.)

If you are able to connect but receive a 502 (bad gateway) error, check the following:

* The NetBox system process (gunicorn) is running: `systemctl status netbox`
* nginx/Apache is configured to connect to the port on which gunicorn is listening (default is 8001).
* SELinux is not preventing the reverse proxy connection. You may need to allow HTTP network connections with the command `setsebool -P httpd_can_network_connect 1`
