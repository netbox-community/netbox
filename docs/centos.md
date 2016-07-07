<h1>Getting started on RHEL/Centos OS</h1>

This guide documents the process of installing NetBox on RHEL/Centos 7 with [nginx](https://www.nginx.com/) and [gunicorn](http://gunicorn.org/).

CENTOS 7 - Centos 6 is similar, but slightly different

[TOC]

# PostgreSQL

 Install postgresql repository

# yum localinstall https://download.postgresql.org/pub/repos/yum/9.5/redhat/rhel-7-x86_64/pgdg-centos95-9.5-2.noarch.rpm

This packages are necessary to Install postgresql
```
yum install postgresql95-server postgresql95-devel python-psycopg2 -y
```

Enable the service
```
systemctl enable postgresql-9.5
```

Initialize the database
```
/usr/pgsql-9.5/bin/postgresql95-setup initdb
```
Allow password login for users
```
sed -i -e 's/ident/md5/' /var/lib/pgsql/9.5/data/pg_hba.conf
```

Start the service
```
service postgresql-9.5 start
```

Create our user/database
```
sudo -u postgres psql <<EOL
CREATE DATABASE netbox;
CREATE USER netbox WITH PASSWORD 'J5brHrAXFLQSif0K';
GRANT ALL PRIVILEGES ON DATABASE netbox TO netbox;
\q
EOL
```
Install required RPM's
```
yum install epel-release
yum install -y gcc openssl-devel python python-dev git python-pip libxml2-devel libxslt-devel libffi-devel graphviz
```

# Git clone the repo
```
mkdir -p /opt/netbox
cd /opt/netbox
git clone -b master https://github.com/digitalocean/netbox.git .
pip install -r requirements.txt
sed -i -e "s/'USER': ''/'USER': 'netbox'/" /opt/netbox/netbox/netbox/configuration.py
sed -i -e "s/'PASSWORD': ''/'PASSWORD': 'J5brHrAXFLQSif0K'/" /opt/netbox/netbox/netbox/configuration.py
sed -i -e "s/ALLOWED_HOSTS = \[\]/ALLOWED_HOSTS = \['\*'\]/" /opt/netbox/netbox/netbox/configuration.py
key=`python2.7 /opt/netbox/netbox/generate_secret_key.py`
sed -i -e "s/SECRET_KEY = ''/SECRET_KEY = '$key'/" /opt/netbox/netbox/netbox/configuration.py
python2.7 /opt/netbox/netbox/manage.py migrate
python2.7 /opt/netbox/netbox/manage.py collectstatic
```
Test the application to make sure it starts
```
 python2.7 manage.py runserver 0.0.0.0:8080
```

Use the latest NGINX
```
echo "[nginx]
name=nginx repo
baseurl=http://nginx.org/packages/centos/7/$basearch/
gpgcheck=0
enabled=1" > /etc/yum.repos.d/nginx.repo
```

Install nginx gunicorn and supervisor
```
yum install -y nginx python-gunicorn supervisor
```

Use this Nginx configuration:
 ```
echo 'server {
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
       add_header P3P \'CP="ALL DSP COR PSAa PSDa OUR NOR ONL UNI COM NAV"\';
   }
}' > /etc/nginx/conf.d/netbox.conf
rm /etc/nginx/conf.d/default
```
Creater a user to run netbox services
```
useradd -M netbox
```
```
Gunicorn configuration
echo "command = '/usr/bin/gunicorn'
pythonpath = '/opt/netbox/netbox'
bind = '0.0.0.0:8001'
workers = 3
user = 'netbox'" > /opt/netbox/gunicorn_config.py
```
Supervisor configuration
```
echo "[program:netbox]
command = gunicorn -c /opt/netbox/gunicorn_config.py netbox.wsgi
directory = /opt/netbox/netbox/
user = netbox" >> /etc/supervisord.conf
```
Restart the services to it takes the changes
```
service nginx restart
```
service supervisord restart
```
