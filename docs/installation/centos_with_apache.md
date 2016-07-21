# Install Netbox on CentOS 7 with Apache as a Web Server and Python Virtualenv



This guide installs NetBox on CentOS 7 system.

This guide assumes that you have configured selinux and firewall to allow apache access to /opt/netbox and webaccess to the server.



# Enable EPEL

```
# yum install epel-release -y
```

# Install required packages for Netbox

```
# yum install -y python-devel git python-pip libxml2-devel libxslt-devel libffi-devel graphviz libpqxx-devel python-psycopg2 gcc openssl-devel libyaml-devel python-lxml git
```

# Install PostreSQL

Install, enable and start PostgreSQL and enable password login with notes from this <a href="https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-centos-7">guide</a>:

```
# install postgresql-server
```

Now that our software is installed, we have to perform a few steps before we can use it.

Create a new PostgreSQL database cluster:

```
# postgresql-setup initdb
```

By default, PostgreSQL does not allow password authentication. We will change that by editing its host-based authentication (HBA) configuration.

Open the HBA configuration with your favorite text editor. We will use vi:

```
# vi /var/lib/pgsql/data/pg_hba.conf
```

Find the lines that looks like this, near the bottom of the file:
pg_hba.conf excerpt (original)

```
 host    all             all             127.0.0.1/32            ident
 host    all             all             ::1/128                 ident
```

Then replace "ident" with "md5", so they look like this:
pg_hba.conf excerpt (updated)

```
 host    all             all             127.0.0.1/32            md5
 host    all             all             ::1/128                 md5
```

Save and exit. PostgreSQL is now configured to allow password authentication.

Now start and enable PostgreSQL:

```
# systemctl start postgresql
# systemctl enable postgresql
```

# Configure Database

At a minimum, we need to create a database for NetBox and assign it a username and password for authentication. This is done with the following commands.

!!! danger
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

You can verify that authentication works issuing the following command and providing the configured password:

```
# psql -U netbox -h localhost -W
```

If successful, you will enter a `postgres` prompt. Type `\q` to exit.


# Use Python's Virtualenv

To use netbox on a Python virtualenv and get latest pip version:

```
# pip install --upgrade pip
# yum install python-virtualenvwrapper
# source /usr/bin/virtualenvwrapper.sh
```

# Add netbox User

To make Apache serve netbox application as netbox user, add netbox user to system:

```
# adduser --home /opt/netbox netbox
# su - netbox
$ pwd
/opt/netbox
$ mkvirtualenv netbox
(netbox)[netbox@netbox-vm-1 ~]$
```

# Install Netbox

For this guide, we'll be using git method:

```
$ git clone -b master https://github.com/digitalocean/netbox.git
```

Then install Python's requirements, make sure you do this inside the virtualenv

```
(netbox)[netbox@netbox-vm-1 netbox]$ pwd
/opt/netbox/netbox
(netbox)[netbox@netbox-vm-1 netbox]$ pip install -r requirements.txt
```

# Configuration

Move into the NetBox configuration directory and make a copy of `configuration.example.py` named `configuration.py`.

```
$ cd netbox/netbox/
$ cp configuration.example.py configuration.py
```

Open `configuration.py` with your preferred editor and set the following variables:
 
* ALLOWED_HOSTS
* DATABASE
* SECRET_KEY

## ALLOWED_HOSTS

This is a list of the valid hostnames by which this server can be reached. You must specify at least one name or IP address.

Example:

```
ALLOWED_HOSTS = ['netbox.example.com', '192.0.2.123']
```

## DATABASE

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

## SECRET_KEY

Generate a random secret key of at least 50 alphanumeric characters. This key must be unique to this installation and must not be shared outside the local system.

You may use the script located at `netbox/generate_secret_key.py` to generate a suitable key.

!!! note
    In the case of a highly available installation with multiple web servers, `SECRET_KEY` must be identical among all servers in order to maintain a persistent user session state.

# Run Database Migrations

Before NetBox can run, we need to install the database schema. This is done by running `./manage.py migrate` from the `netbox` directory (`/opt/netbox/netbox/` in our example):

```
$ cd /opt/netbox/netbox/netbox
$ ./manage.py migrate
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

# Create a Super User

NetBox does not come with any predefined user accounts. You'll need to create a super user to be able to log into NetBox:

```
$ ./manage.py createsuperuser
Username: admin
Email address: admin@example.com
Password: 
Password (again): 
Superuser created successfully.
```

$ Collect Static Files

```
$ ./manage.py collectstatic

You have requested to collect static files at the destination
location as specified in your settings:

    /opt/netbox/netbox/netbox/static

This will overwrite existing files!
Are you sure you want to do this?

Type 'yes' to continue, or 'no' to cancel: yes
```

# Test the Application

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



When you finish, if the test server ran OK, proceed to next step. Otherwise check the steps above.


# Install and Configure Apache to run Netbox

To use Apache to run Netbox, we'll need to install mod_wsgi to connect to wsgi.py script:

```
# yum install httpd mod_wsgi  
```

Add Netbox to virtualhosts

```
# vim /etc/httpd/conf.d/netbox.conf
```

Example netbox.conf contents :

```
# Netbox

<VirtualHost *:80>
    ServerName YOURDOMAIN               # Make sure to add this domain into configuration.py ALLOWED_HOSTS
    ServerAdmin YOUREMAIL


    DocumentRoot /opt/netbox/netbox/
    CustomLog /var/log/wsgi/netbox_log combined
    LogLevel info

    WSGIDaemonProcess netbox user=netbox group=netbox python-path=/opt/netbox/netbox/netbox:/opt/netbox/.virtualenvs/netbox/lib/python2.7/site-packages
    WSGIProcessGroup netbox
    WSGIScriptAlias / /opt/netbox/netbox/netbox/netbox/wsgi.py

    <Directory /opt/netbox/netbox/netbox/netbox/>
        <Files wsgi.py>
            WSGIApplicationGroup %{GLOBAL}
            Require all granted
        </Files>
    </Directory>
    
    Alias /static /opt/netbox/netbox/netbox/static
    <Directory /opt/netbox/netbox/netbox/static/>
            WSGIApplicationGroup %{GLOBAL}
            Require all granted
    </Directory>
</VirtualHost>
```

Make sure you have the log file in the directory above or remove the log line if you want to use httpd's main logging.

# Final step

Last step is to make /opt/netbox executable so Apache can run

```
# chmod +x /opt/netbox
```
Restart apache and you should be good to go. 

```
# systemctl restart httpd
```
