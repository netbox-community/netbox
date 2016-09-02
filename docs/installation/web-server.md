# Web Server Installation

We'll set up a simple WSGI front end using [gunicorn](http://gunicorn.org/) for the purposes of this guide. For web servers, we provide example configurations for both [nginx](https://www.nginx.com/resources/wiki/) and [Apache](http://httpd.apache.org/docs/2.4). (You are of course free to use whichever combination of HTTP and WSGI services you'd like.) We'll also use [supervisord](http://supervisord.org/) to enable service persistence.

Debian/Ubuntu
```
# sudo apt-get install -y gunicorn supervisor
```
Centos/RHEL
```
# sudo yum install -y gunicorn supervisor
```

## Option A: nginx

The following will serve as a minimal nginx configuration. Be sure to modify your server name and installation path appropriately.

Debian/Ubuntu

```
# sudo apt-get install -y nginx
```
Centos/RHEL
```
# sudo yum install -y nginx
```

Once nginx is installed, proceed with the following configuration:

```
server {
    listen 80;

    server_name netbox.example.com;

    access_log off;

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

Save this configuration to `/etc/nginx/sites-available/netbox`. Then, delete `/etc/nginx/sites-enabled/default` and create a symlink in the `sites-enabled` directory to the configuration file you just created.

```
# cd /etc/nginx/sites-enabled/
# rm default
# ln -s /etc/nginx/sites-available/netbox
```

Restart the nginx service to use the new configuration.

```
# service nginx restart
 * Restarting nginx nginx
```

To enable SSL, consider this guide on [securing nginx with Let's Encrypt](https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-14-04).

## Option B: Apache

Debian/Ubuntu

```
# sudo apt-get install -y apache2
```
Centos/RHEL

```
# sudo yum install -y httpd
```

Once Apache is installed, proceed with the following configuration (Be sure to modify the `ServerName` appropriately):

```
<VirtualHost *:80>
    ProxyPreserveHost On

    ServerName netbox.example.com

    Alias /static /opt/netbox/netbox/static

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

```
# a2enmod proxy
# a2enmod proxy_http
# a2ensite netbox
# service apache2 restart
```

To enable SSL, consider this guide on [securing Apache with Let's Encrypt](https://www.digitalocean.com/community/tutorials/how-to-secure-apache-with-let-s-encrypt-on-ubuntu-14-04).

# gunicorn Installation

Save the following configuration file in the root netbox installation path (in this example, `/opt/netbox/`) as `gunicorn_config.py`. Be sure to verify the location of the gunicorn executable (e.g. `which gunicorn`) and to update the `pythonpath` variable if needed.

```
command = '/usr/bin/gunicorn'
pythonpath = '/opt/netbox/netbox'
bind = '127.0.0.1:8001'
workers = 3
user = 'www-data'
```

# supervisord Installation

Save the following as `/etc/supervisor/conf.d/netbox.conf`. Update the `command` and `directory` paths as needed.

```
[program:netbox]
command = gunicorn -c /opt/netbox/gunicorn_config.py netbox.wsgi
directory = /opt/netbox/netbox/
user = www-data
```

Finally, restart the supervisor service to detect and run the gunicorn service:

```
# service supervisor restart
```

At this point, you should be able to connect to the nginx HTTP service at the server name or IP address you provided. If you are unable to connect, check that the nginx service is running and properly configured. If you receive a 502 (bad gateway) error, this indicates that gunicorn is misconfigured or not running.

!!! info
    Please keep in mind that the configurations provided here are bare minimums required to get NetBox up and running. You will almost certainly want to make some changes to better suit your production environment.
