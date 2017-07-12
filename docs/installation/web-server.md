# Web Server Installation

We'll set up a simple WSGI front end using [gunicorn](http://gunicorn.org/) for the purposes of this guide. For web servers, we provide example configurations for both [nginx](https://www.nginx.com/resources/wiki/) and [Apache](http://httpd.apache.org/docs/2.4). (You are of course free to use whichever combination of HTTP and WSGI services you'd like.) We'll also use [supervisord](http://supervisord.org/) to enable service persistence.

!!! info
    For the sake of brevity, only Ubuntu 16.04 instructions are provided here, but this sort of web server and WSGI configuration is not unique to NetBox. Please consult your distribution's documentation for assistance if needed.

```no-highlight
# apt-get install -y gunicorn supervisor
```

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

To enable SSL, consider this guide on [securing nginx with Let's Encrypt](https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-14-04).

## Option B: Apache

```no-highlight
# apt-get install -y apache2
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

    ProxyPass / http://127.0.0.1:8001/
    ProxyPassReverse / http://127.0.0.1:8001/
</VirtualHost>
```

Save the contents of the above example in `/etc/apache2/sites-available/netbox.conf`, enable the `proxy` and `proxy_http` modules, and reload Apache:

```no-highlight
# a2enmod proxy
# a2enmod proxy_http
# a2ensite netbox
# service apache2 restart
```

To enable SSL, consider this guide on [securing Apache with Let's Encrypt](https://www.digitalocean.com/community/tutorials/how-to-secure-apache-with-let-s-encrypt-on-ubuntu-14-04).

# gunicorn Installation

Save the following configuration in the root netbox installation path as `gunicorn_config.py` (e.g. `/opt/netbox/gunicorn_config.py` per our example installation). Be sure to verify the location of the gunicorn executable on your server (e.g. `which gunicorn`) and to update the `pythonpath` variable if needed. If using CentOS/RHEL, change the username from `www-data` to `nginx` or `apache`.

```no-highlight
command = '/usr/bin/gunicorn'
pythonpath = '/opt/netbox/netbox'
bind = '127.0.0.1:8001'
workers = 3
user = 'www-data'
```

# supervisord Installation

Save the following as `/etc/supervisor/conf.d/netbox.conf`. Update the `command` and `directory` paths as needed. If using CentOS/RHEL, change the username from `www-data` to `nginx` or `apache`.

```no-highlight
[program:netbox]
command = gunicorn -c /opt/netbox/gunicorn_config.py netbox.wsgi
directory = /opt/netbox/netbox/
user = www-data
```

Then, restart the supervisor service to detect and run the gunicorn service:

```no-highlight
# service supervisor restart
```

At this point, you should be able to connect to the nginx HTTP service at the server name or IP address you provided. If you are unable to connect, check that the nginx service is running and properly configured. If you receive a 502 (bad gateway) error, this indicates that gunicorn is misconfigured or not running.

# nginx + uwsgi installation

uwsgi is an alternative to using gunicorn + supervisord.  It has native proxy support via the WSGI protocol in nginx.

```no-highlight
# apt-get install uwsgi uwsgi-plugin-python3
```

Add a site to uwsgi in `/etc/uwsgi/apps-available/netbox.ini`:

```ini
[uwsgi]
chdir = /var/www/netbox/netbox
stats = 127.0.0.1:9191
wsgi-file = netbox/wsgi.py
master = true
processes = 4
threads = 2
uid = www-data
socket = /run/uwsgi/netbox.sock
chown-socket = www-data:www-data
chmod-socket = 660
vacuum = true
```

Symlink it in `/etc/uwsgi/apps-enabled`:

```no-highlight
# cd /etc/uwsgi/apps-enabled
# ln -s ../apps-available/netbox.ini .
```

For the nginx site setup in `/etc/nginx/sites-available/netbox`, a minimal example is:

```nginx
server {
    listen 443 ssl default_server;
    listen [::]:443 ssl default_server;
    ssl_certificate /etc/ssl/certs/netbox.crt;
    ssl_certificate_key /etc/ssl/private/netbox.key;
    server_name $hostname;
    keepalive_timeout 75;
    root /var/www/netbox;
    access_log /var/log/nginx/netbox.access combined;
    location /static/ {
        alias /var/www/netbox/netbox/static/;
    }
    location / {
        uwsgi_pass unix:///run/uwsgi/netbox.sock;
        include uwsgi_params;
    }
}
```

Finally, test configs & start the nginx and uwsgi services:
```no-highlight
# uwsgi --show-config
# nginx -t
# service uwsgi start
# service nginx start
```

!!! info
    Please keep in mind that the configurations provided here are bare minimums required to get NetBox up and running. You will almost certainly want to make some changes to better suit your production environment.
