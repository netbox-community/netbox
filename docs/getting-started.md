<h1>Getting Started</h1>

This guide documents the process of installing NetBox on an Ubuntu 14.04 server with [nginx](https://www.nginx.com/) and [gunicorn](http://gunicorn.org/).

[TOC]

# PostgreSQL

## Installation

The following packages are needed to install PostgreSQL:

* postgresql
* libpq-dev
* python-psycopg2

```
# sudo apt-get install -y postgresql libpq-dev python-psycopg2
```

## Configuration

At a minimum, we need to create a database for NetBox and assign it a username and password for authentication. This is done with the following commands.

DO NOT USE THE PASSWORD FROM THE EXAMPLE.

```
# sudo -u postgres psql
psql (9.3.13)
Type "help" for help.

postgres=# CREATE DATABASE netbox;
CREATE DATABASE
postgres=# CREATE USER netbox WITH PASSWORD 'J5brHrAXFLQSif0K';
CREATE ROLE
postgres=# GRANT ALL PRIVILEGES ON DATABASE netbox TO netbox;
GRANT
postgres=# \q
```

You can verify that authentication works using the following command:

```
# psql -U netbox -h localhost -W
```

---

# NetBox

## Installation

NetBox requires following dependencies:

* python2.7
* python-dev
* python-pip
* libxml2-dev
* libxslt1-dev
* libffi-dev
* graphviz

```
# sudo apt-get install -y python2.7 python-dev git python-pip libxml2-dev libxslt1-dev libffi-dev graphviz
```

You may opt to install NetBox either from a numbered release or by cloning the master branch of its repository on GitHub.

### Option A: Download a Release

Download the [latest stable release](https://github.com/digitalocean/netbox/releases) from GitHub as a tarball or ZIP archive. Extract it to your desired path. In this example, we'll use `/opt/netbox`.

```
# wget https://github.com/digitalocean/netbox/archive/vX.Y.Z.tar.gz
# tar -xzf vX.Y.Z.tar.gz -C /opt
# cd /opt/
# ln -s netbox-1.0.4/ netbox
# cd /opt/netbox/
```

### Option B: Clone the Git Repository

Create the base directory for the NetBox installation. For this guide, we'll use `/opt/netbox`.

```
# mkdir -p /opt/netbox/
# cd /opt/netbox/
```

If `git` is not already installed, install it:

```
# sudo apt-get install -y git
```

Next, clone the **master** branch of the NetBox GitHub repository into the current directory:

```
# git clone -b master https://github.com/digitalocean/netbox.git .
Cloning into '.'...
remote: Counting objects: 1994, done.
remote: Compressing objects: 100% (150/150), done.
remote: Total 1994 (delta 80), reused 0 (delta 0), pack-reused 1842
Receiving objects: 100% (1994/1994), 472.36 KiB | 0 bytes/s, done.
Resolving deltas: 100% (1495/1495), done.
Checking connectivity... done.
```

### Install Python Packages

Install the necessary Python packages using pip. (If you encounter any compilation errors during this step, ensure that you've installed all of the required dependencies.)

```
# sudo pip install -r requirements.txt
```

## Configuration

Move into the NetBox configuration directory and make a copy of `configuration.example.py` named `configuration.py`.

```
# cd netbox/netbox/
# cp configuration.example.py configuration.py
```

Open `configuration.py` with your preferred editor and set the following variables:
 
* ALLOWED_HOSTS
* DATABASE
* SECRET_KEY

### ALLOWED_HOSTS

This is a list of the valid hostnames by which this server can be reached. You must specify at least one name or IP address.

Example:

```
ALLOWED_HOSTS = ['netbox.example.com', '192.0.2.123']
```

### DATABASE

This parameter holds the database configuration details. You must define the username and password used when you configured PostgreSQL. If the service is running on a remote host, replace `localhost` with its address.

Example:

```
DATABASE = {
    'NAME': 'netbox',               # Database name
    'USER': 'netbox',               # PostgreSQL username
    'PASSWORD': 'J5brHrAXFLQSif0K', # PostgreSQL password
    'HOST': 'localhost',            # Database server
    'PORT': '',                     # Database port (leave blank for default)
}
```

### SECRET_KEY

Generate a random secret key of at least 50 alphanumeric characters. This key must be unique to this installation and must not be shared outside the local system.

You may use the script located at `netbox/generate_secret_key.py` to generate a suitable key.

## Run Migrations

Before NetBox can run, we need to install the database schema. This is done by running `./manage.py migrate` from the `netbox` directory (`/opt/netbox/netbox/` in our example):

```
# cd /opt/netbox/netbox/
# ./manage.py migrate
Operations to perform:
  Apply all migrations: dcim, sessions, admin, ipam, utilities, auth, circuits, contenttypes, extras, secrets, users
Running migrations:
  Rendering model states... DONE
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  ...
```

If this step results in a PostgreSQL authentication error, ensure that the username and password created in the database match what has been specified in `configuration.py`

## Create a Super User

NetBox does not come with any predefined user accounts. You'll need to create a super user to be able to log into NetBox:

```
# ./manage.py createsuperuser
Username: admin
Email address: admin@example.com
Password: 
Password (again): 
Superuser created successfully.
```

## Collect Static Files

```
# ./manage.py collectstatic

You have requested to collect static files at the destination
location as specified in your settings:

    /opt/netbox/netbox/static

This will overwrite existing files!
Are you sure you want to do this?

Type 'yes' to continue, or 'no' to cancel: yes
```

## Test the Application

At this point, NetBox should be able to run. We can verify this by starting a development instance:

```
# ./manage.py runserver 0.0.0.0:8000 --insecure
Performing system checks...

System check identified no issues (0 silenced).
June 17, 2016 - 16:17:36
Django version 1.9.7, using settings 'netbox.settings'
Starting development server at http://0.0.0.0:8000/
Quit the server with CONTROL-C.
```

Now if we navigate to the name or IP of the server (as defined in `ALLOWED_HOSTS`) we should be greeted with the NetBox home page. Note that this built-in web service is for development and testing purposes only. It is not suited for production use.

If the test service does not run, or you cannot reach the NetBox home page, something has gone wrong. Do not proceed with the rest of this guide until the installation has been corrected.

# Web Server and gunicorn

## Installation

We'll set up a simple HTTP front end using [gunicorn](http://gunicorn.org/) for the purposes of this guide. For web servers, we provide example configurations for both [nginx](https://www.nginx.com/resources/wiki/) and [Apache](http://httpd.apache.org/docs/2.4). (You are of course free to use whichever combination of HTTP and WSGI services you'd like.) We'll also use [supervisord](http://supervisord.org/) for service persistence. 

```
# sudo apt-get install -y gunicorn supervisor
```

## nginx Configuration

The following will serve as a minimal nginx configuration. Be sure to modify your server name and installation path appropriately.

```
# sudo apt-get install -y nginx
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
## Apache Configuration

```
# sudo apt-get install -y apache2
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

## gunicorn Configuration

Save the following configuration file in the root netbox installation path (in this example, `/opt/netbox/`) as `gunicorn_config.py`. Be sure to verify the location of the gunicorn executable (e.g. `which gunicorn`) and to update the `pythonpath` variable if needed.

```
command = '/usr/bin/gunicorn'
pythonpath = '/opt/netbox/netbox'
bind = '127.0.0.1:8001'
workers = 3
user = 'www-data'
```

## supervisord Configuration

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

Please keep in mind that the configurations provided here are bare minimums required to get NetBox up and running. You will almost certainly want to make some changes to better suit your production environment.

## Let's Encrypt SSL + nginx

To add SSL support to the installation we'll start by installing the arbitrary precision calculator language.

```
# sudo apt-get install -y bc
```

Next we'll clone Let's Encrypt into /opt/:

```
# sudo git clone https://github.com/letsencrypt/letsencrypt /opt/letsencrypt
```

To ensure Let's Encrypt can publicly access the directory it needs for certificate validation you'll need to edit `/etc/nginx/sites-available/netbox` and add:

```
    location /.well-known/ {
        alias /opt/netbox/netbox/.well-known/;
        allow all;
    }
```

Then restart nginix:

```
# sudo services nginx restart
```

To create the certificate use the following commands ensuring to change `netbox.example.com` to the domain name of the server:

```
# cd /opt/letsencrypt
# ./letsencrypt-auto certonly -a webroot --webroot-path=/opt/netbox/netbox/ -d netbox.example.com
```

If you wish to add support for the `www` prefix you'd use:

```
# cd /opt/letsencrypt
# ./letsencrypt-auto certonly -a webroot --webroot-path=/opt/netbox/netbox/ -d netbox.example.com -d www.netbox.example.com
```

Make sure you have DNS records setup for the hostnames you use and that they resolve back the netbox server.

You will be prompted for your email address to receive notifications about your SSL and then asked to accept the subscriber agreement.

If successful you'll now have four files in `/etc/letsencrypt/live/netbox.example.com` (remember, your hostname is different)

```
cert.pem
chain.pem
fullchain.pem
privkey.pem
```

Now edit your nginx configuration `/etc/nginx/sites-available/netbox` and at the top edit to the following:

```
    #listen 80;
    #listen [::]80;
    listen 443;
    listen [::]443;

    ssl on;
    ssl_certificate /etc/letsencrypt/live/netbox.example.com/cert.pem;
    ssl_certificate_key /etc/letsencrypt/live/netbox.example.com/privkey.pem;
```

If you are not using IPv6 then you do not need `listen [::]443;` The two commented lines are for non-SSL for both IPv4 and IPv6.

Lastly, restart nginx:

```
# sudo services nginx restart
```

You should now have netbox running on a SSL protected connection.

# Upgrading

## Installation of Upgrade

As with the initial installation, you can upgrade NetBox by either downloading the latest release package or by cloning the `master` branch of the git repository. 

### Option A: Download a Release

Download the [latest stable release](https://github.com/digitalocean/netbox/releases) from GitHub as a tarball or ZIP archive. Extract it to your desired path. In this example, we'll use `/opt/netbox`.  For this guide we are using 1.0.4 as the old version and 1.0.7 as the new version.

Download & extract latest version:
```
# wget https://github.com/digitalocean/netbox/archive/vX.Y.Z.tar.gz
# tar -xzf vX.Y.Z.tar.gz -C /opt
# cd /opt/
# ln -sf netbox-1.0.7/ netbox
```

Copy the 'configuration.py' you created when first installing to the new version:
```
# cp /opt/netbox-1.0.4/configuration.py /opt/netbox/configuration.py
```

### Option B: Clone the Git Repository (latest master release)

For this guide, we'll use `/opt/netbox`.

Check that your git branch is up to date & is set to master:
```
# cd /opt/netbox
# git status
```

If not on branch master, set it and verify status:
```
# git checkout master
# git status
```

Pull down the set branch from git status above:
```
# git pull
```


## Upgrade Script & Netbox Restart

Once the new code is in place, run the upgrade script (which may need to be run as root depending on how your environment is configured).

```
# ./upgrade.sh
```

This script:

* Installs or upgrades any new required Python packages
* Applies any database migrations that were included in the release
* Collects all static files to be served by the HTTP service

Finally, restart the WSGI service to run the new code. If you followed this guide for the initial installation, this is done using `supervisorctl`:

```
# sudo supervisorctl restart netbox
```
