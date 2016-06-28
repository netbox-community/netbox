<h1>Como Empesar</h1>

Esta guía document el proceso de instalar NetBox en servidor con Ubuntu 14.04 usando  [nginx](https://www.nginx.com/) y [gunicorn](http://gunicorn.org/).

[TOC]

# PostgreSQL

## Instalación

Estos paquetes son necesarios para poder instalar PostgreSQL:

* postgresql
* libpq-dev
* python-psycopg2

```
# apt-get install postgresql libpq-dev python-psycopg2
```

## Configuración

a el mínimo necesitamos crear una base de datos y asignar un nombre para el usuario y una contraseña para autenticación. Esto es echo con estos comandos.

No uses la contraseña de este ejemplo.

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

Puedes verificar que la autenticación funciono haciendo estos comandos:

```
# psql -U netbox -h localhost -W
```

---

# NetBox

## Dependencias

* python2.7
* python-dev
* git
* python-pip
* libxml2-dev
* libxslt1-dev
* libffi-dev
* graphviz*

```
# apt-get install python2.7 python-dev git python-pip libxml2-dev libxslt1-dev libffi-dev graphviz
```

*graphviz es necesario para poder representar los mapas con topología. Si no necesita este requisito entonces graphviz no es necesario.

## Copiar el deposito de git.

Crear la base y el directorio donde NetBox va ser instalado. Para esta guía vamos a usar  `/opt/netbox`.

```
# mkdir -p /opt/netbox/
# cd /opt/netbox/
```

Entonces  copie el deposito de git en esta misma directorio:

```
# git clone https://github.com/digitalocean/netbox.git .
Cloning into '.'...
remote: Counting objects: 1994, done.
remote: Compressing objects: 100% (150/150), done.
remote: Total 1994 (delta 80), reused 0 (delta 0), pack-reused 1842
Receiving objects: 100% (1994/1994), 472.36 KiB | 0 bytes/s, done.
Resolving deltas: 100% (1495/1495), done.
Checking connectivity... done.
```

Instala los paquetes necesario de Python usand pip.( Si encuentas algun error compilando en este paso, asegurate que tienes todas las dependencias necesarias.)

```
# pip install -r requirements.txt
```

## Configuración

Mueve en el directorio de la configuración y alte una copia de el `configuration.example.py` llamado `configuration.py`.

```
# cd netbox/netbox/
# cp configuration.example.py configuration.py
```

Abre `configuration.py` con tu preferido editor y pon entos valores:
* ALLOWED_HOSTS
* DATABASE
* SECRET_KEY

### ALLOWED_HOSTS

Esta es una lista de los aparatos que el servidor puede comunicarse. Tienes que especificar el nombre de el aparato o el IP address.

Ejemplo:

```
ALLOWED_HOSTS = ['netbox.example.com', '192.0.2.123']
```

### Base de Datos

Este parámetro tiene los detalles y la configuración de la base de datos. Tienes que definir un nombre para el usuario y una contraseña cuando configuras PostgreSQL. Si el servicio
esta en un servidor remoto cambia `localhost` con su dirección.

Ejemplo:

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

Genera una llave secreta algarete con polo menos 50 letras alfanuméricas. Esta llave tiene que ser la unica en esta instalación y no puede ser compartida fuera de este sistema.

Puedes usar este script en`netbox/generate_secret_key.py` para generar una llave.

## Hacer migraciónes de el sistema

Antes que NetBox pueda correr necesitamos instalar la schema para la base de datos. Esto es echo corriendo `./manage.py migrate` de el `netbox` directorio (`/opt/netbox/netbox/` en nuestro ejemplo):

```
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

Si en este paso resulta con errores de autenticación en PostgreSQL , asegura que el nombre de el usuario y la contraseña creada en la base de datos es igual a lo que fue especificado en `configuration.py`

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

# nginx and gunicorn

## Installation

We'll set up a simple HTTP front end using [nginx](https://www.nginx.com/resources/wiki/) and [gunicorn](http://gunicorn.org/) for the purposes of this guide. (You are of course free to use whichever combination of HTTP and WSGI services you'd like.) We'll also use [supervisord](http://supervisord.org/) for service persistence.

```
# apt-get install nginx gunicorn supervisor
```

## nginx Configuration

The following will serve as a minimal nginx configuration. Be sure to modify your server name and installation path appropriately.

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

## gunicorn Configuration

Save the following configuration file in the root netbox installation path (in this example, `/opt/netbox/`.) as `gunicorn_config.py`. Be sure to verify the location of the gunicorn executable (e.g. `which gunicorn`) and to update the `pythonpath` variable if needed.

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

Please keep in mind that the configurations provided here are a bare minimum to get NetBox up and running. You will almost certainly want to make some changes to better suit your production environment.
