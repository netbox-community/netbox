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

## Crear un super usuario

NetBox no viene con ninguna cuentas basica.Vas a necesitar crear un super usuario para poder entrar a NetBox:

```
# ./manage.py createsuperuser
Username: admin
Email address: admin@example.com
Password:
Password (again):
Superuser created successfully.
```

## Colecionar archivos estaticos

```
# ./manage.py collectstatic

You have requested to collect static files at the destination
location as specified in your settings:

    /opt/netbox/netbox/static

This will overwrite existing files!
Are you sure you want to do this?

Type 'yes' to continue, or 'no' to cancel: yes
```

## Testiar la aplicación

En este punto ya NetBox puede correr. Podemos verificar empesando la aplicación:

```
# ./manage.py runserver 0.0.0.0:8000 --insecure
Performing system checks...

System check identified no issues (0 silenced).
June 17, 2016 - 16:17:36
Django version 1.9.7, using settings 'netbox.settings'
Starting development server at http://0.0.0.0:8000/
Quit the server with CONTROL-C.
```

Ahora si vamos a el nombre de el aparato o IP de el servidor (como definido en `ALLOWED_HOSTS`) Nos encontramos con la página de NetBox. Nota que este servicio de web es para testiar o desarrollo namas y no se deveria ser usada para nada en producción.

Si el servicio no corre or no te sale la página de NetBox entonces algo paso. No sigas con el resto de esta guía hasta que el problema a sido resuelto.

# nginx and gunicorn

## Instalación

Vamos a setiar un simple HTTP front end suando [nginx](https://www.nginx.com/resources/wiki/) y [gunicorn](http://gunicorn.org/) como ejemplos en esta guía . (Tu puedes usar cualquier combinación que quieras de  HTTP and WSGI .) Tambien vamos a usar [supervisord](http://supervisord.org/).

```
# apt-get install nginx gunicorn supervisor
```

## nginx Configuración

Esto servira para correr lo minimo de nginx. Acuerdate cambiar el nombre de el servidor y el directorio de la instalación.

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

Graba esta configuración a `/etc/nginx/sites-available/netbox`. entonces borra `/etc/nginx/sites-enabled/default` y crea un  symlink en `sites-enabled` directorio para la configuración  de el archivo que creaste.

```
# cd /etc/nginx/sites-enabled/
# rm default
# ln -s /etc/nginx/sites-available/netbox
```

Vuelve a empezar el servicio de nginx para usar la nueva configuración.

```
# service nginx restart
 * Restarting nginx nginx
```

## gunicorn Configuración

Save the following configuración file in the root netbox installation path (in this example, `/opt/netbox/`.) as `gunicorn_config.py`. Be sure to verify the location of the gunicorn executable (e.g. `which gunicorn`) and to update the `pythonpath` variable if needed.

```
command = '/usr/bin/gunicorn'
pythonpath = '/opt/netbox/netbox'
bind = '127.0.0.1:8001'
workers = 3
user = 'www-data'
```

## supervisord Configuración

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

A este punto deverias poder conectarte a  nginx con el nombre de el servidor o el que pusistes. Si no te pudes conectar chequea que el servicio de nginx esta corriendo y tiene la configuración correcta. Si recibes un 502 (bad gateway) error esto indica que gunicorn no tiene la configuración correcta o no esta prendido.

Please keep in mind that the configurations provided here are a bare minimum to get NetBox up and running. You will almost certainly want to make some changes to better suit your production environment.
