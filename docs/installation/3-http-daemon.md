We'll set up a simple WSGI front end using [gunicorn](http://gunicorn.org/) for the purposes of this guide. For web servers, we provide example configurations for both [nginx](https://www.nginx.com/resources/wiki/) and [Apache](http://httpd.apache.org/docs/2.4). (You are of course free to use whichever combination of HTTP and WSGI services you'd like.) We'll use systemd to enable service persistence.

!!! info
    For the sake of brevity, only Ubuntu 18.04 instructions are provided here, but this sort of web server and WSGI configuration is not unique to NetBox. Please consult your distribution's documentation for assistance if needed.

# Web Server Installation

## Option A: nginx

The following will serve as a minimal nginx configuration. Be sure to modify your server name and installation path appropriately.

```no-highlight
# apt-get install -y nginx
```

Once nginx is installed, save the following configuration to `/etc/nginx/sites-available/netbox`. Be sure to replace `netbox.example.com` with the domain name or IP address of your installation. (This should match the value configured for `ALLOWED_HOSTS` in `configuration.py`.)

```nginx
server {
    listen 80;

    server_name netbox.example.com;

    client_max_body_size 25m;

    location /static/ {
        alias /opt/netbox/netbox/static/;
    }

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header X-Forwarded-Host $server_name;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        add_header P3P 'CP="ALL DSP COR PSAa PSDa OUR NOR ONL UNI COM NAV"';
    }
}
```

Then, delete `/etc/nginx/sites-enabled/default` and create a symlink in the `sites-enabled` directory to the configuration file you just created.

```no-highlight
# cd /etc/nginx/sites-enabled/
# rm default
# ln -s /etc/nginx/sites-available/netbox
```

Restart the nginx service to use the new configuration.

```no-highlight
# service nginx restart
```

To enable SSL, consider this guide on [securing nginx with Let's Encrypt](https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-16-04).

## Option B: Apache

```no-highlight
# apt-get install -y apache2 libapache2-mod-wsgi-py3
```

Once Apache is installed, proceed with the following configuration (Be sure to modify the `ServerName` appropriately):

```apache
<VirtualHost *:80>
    ProxyPreserveHost On

    ServerName netbox.example.com

    Alias /static /opt/netbox/netbox/static

    # Needed to allow token-based API authentication
    WSGIPassAuthorization on

    <Directory /opt/netbox/netbox/static>
        Options Indexes FollowSymLinks MultiViews
        AllowOverride None
        Require all granted
    </Directory>

    <Location /static>
        ProxyPass !
    </Location>

    RequestHeader set "X-Forwarded-Proto" expr=%{REQUEST_SCHEME}
    ProxyPass / http://127.0.0.1:8001/
    ProxyPassReverse / http://127.0.0.1:8001/
</VirtualHost>
```

Save the contents of the above example in `/etc/apache2/sites-available/netbox.conf`, enable the `proxy` and `proxy_http` modules, and reload Apache:

```no-highlight
# a2enmod proxy
# a2enmod proxy_http
# a2enmod headers
# a2ensite netbox
# service apache2 restart
```

To enable SSL, consider this guide on [securing Apache with Let's Encrypt](https://www.digitalocean.com/community/tutorials/how-to-secure-apache-with-let-s-encrypt-on-ubuntu-16-04).

# gunicorn Installation

Install gunicorn:

```no-highlight
# pip3 install gunicorn
```

# systemd configuration

Copy or link contrib/netbox.service and contrib/netbox-rq.service to /etc/systemd/system/netbox.service and /etc/systemd/system/netbox-rq.service

```no-highlight
# cp contrib/netbox.service to /etc/systemd/system/netbox.service
# cp contrib/netbox-rq.service to /etc/systemd/system/netbox-rq.service
```

Edit /etc/systemd/system/netbox.service and /etc/systemd/system/netbox-rq.service. Be sure to verify the location of the gunicorn executable on your server (e.g. `which gunicorn`).  If using CentOS/RHEL, change the username from `www-data` to `nginx` or `apache`:

```no-highlight
/usr/local/bin/gunicorn --pid ${PidPath} --pythonpath ${WorkingDirectory}/netbox --config ${ConfigPath} netbox.wsgi
```

```no-highlight
User=www-data
Group=www-data
```

Copy contrib/netbox.env to /etc/sysconfig/netbox.env

```no-highlight
# cp contrib/netbox.env to /etc/sysconfig/netbox.env
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
#     Threads should be: cores * 2 + 1.  So if you have 4 cores, it would be 9.
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

At this point, you should be able to connect to the nginx HTTP service at the server name or IP address you provided. If you are unable to connect, check that the nginx service is running and properly configured. If you receive a 502 (bad gateway) error, this indicates that gunicorn is misconfigured or not running.

!!! info
    Please keep in mind that the configurations provided here are bare minimums required to get NetBox up and running. You will almost certainly want to make some changes to better suit your production environment.
