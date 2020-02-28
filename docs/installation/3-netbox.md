This section of the documentation discusses installing and configuring the NetBox application. Begin by installing all system packages required by NetBox and its dependencies:

## Install System Packages

#### Ubuntu

```no-highlight
# apt-get install -y python3 python3-pip python3-venv python3-dev build-essential libxml2-dev libxslt1-dev libffi-dev libpq-dev libssl-dev zlib1g-dev
```

#### CentOS

```no-highlight
# yum install -y epel-release
# yum install -y gcc python36 python36-devel python36-setuptools libxml2-devel libxslt-devel libffi-devel openssl-devel redhat-rpm-config
# easy_install-3.6 pip
# ln -s /usr/bin/python3.6 /usr/bin/python3
```

## Download NetBox

You may opt to install NetBox either from a numbered release or by cloning the master branch of its repository on GitHub.

### Option A: Download a Release

Download the [latest stable release](https://github.com/netbox-community/netbox/releases) from GitHub as a tarball or ZIP archive and extract it to your desired path. In this example, we'll use `/opt/netbox`.

```no-highlight
# wget https://github.com/netbox-community/netbox/archive/vX.Y.Z.tar.gz
# tar -xzf vX.Y.Z.tar.gz -C /opt
# cd /opt/
# ln -s netbox-X.Y.Z/ netbox
# cd /opt/netbox/
```

### Option B: Clone the Git Repository

Create the base directory for the NetBox installation. For this guide, we'll use `/opt/netbox`.

```no-highlight
# mkdir -p /opt/netbox/ && cd /opt/netbox/
```

If `git` is not already installed, install it:

#### Ubuntu

```no-highlight
# apt-get install -y git
```

#### CentOS

```no-highlight
# yum install -y git
```

Next, clone the **master** branch of the NetBox GitHub repository into the current directory:

```no-highlight
# git clone -b master https://github.com/netbox-community/netbox.git .
Cloning into '.'...
remote: Counting objects: 1994, done.
remote: Compressing objects: 100% (150/150), done.
remote: Total 1994 (delta 80), reused 0 (delta 0), pack-reused 1842
Receiving objects: 100% (1994/1994), 472.36 KiB | 0 bytes/s, done.
Resolving deltas: 100% (1495/1495), done.
Checking connectivity... done.
```

## Create the NetBox User

Create a system user account named `netbox`. We'll configure the WSGI and HTTP services to run under this account. We'll also assign this user ownership of the media directory. This ensures that NetBox will be able to save local files.

```
# adduser --system --group netbox
# chown --recursive netbox /opt/netbox/netbox/media/`
```

## Set Up Python Environment

We'll use a Python [virtual environment](https://docs.python.org/3.6/tutorial/venv.html) to ensure NetBox's required packages don't conflict with anything in the base system. This will create a directory named `venv` in our NetBox root.

```no-highlight
# python3 -m venv /opt/netbox/venv
```

Next, activate the virtual environment and install the required Python packages. You should see your console prompt change to indicate the active environment. (Activating the virtual environment updates your command shell to use the local copy of Python that we just installed for NetBox instead of the system's Python interpreter.)

```no-highlight
# source venv/bin/activate
(venv) # pip3 install -r requirements.txt
```

#### NAPALM Automation (Optional)

NetBox supports integration with the [NAPALM automation](https://napalm-automation.net/) library. NAPALM allows NetBox to fetch live data from devices and return it to a requester via its REST API. Installation of NAPALM is optional. To enable it, install the `napalm` package:

```no-highlight
(venv) # pip3 install napalm
```

#### Remote File Storage (Optional)

By default, NetBox will use the local filesystem to storage uploaded files. To use a remote filesystem, install the [`django-storages`](https://django-storages.readthedocs.io/en/stable/) library and configure your [desired backend](../../configuration/optional-settings/#storage_backend) in `configuration.py`.

```no-highlight
(venv) # pip3 install django-storages
```

## Configuration

Move into the NetBox configuration directory and make a copy of `configuration.example.py` named `configuration.py`.

```no-highlight
(venv) # cd netbox/netbox/
(venv) # cp configuration.example.py configuration.py
```

Open `configuration.py` with your preferred editor and set the following variables:

* `ALLOWED_HOSTS`
* `DATABASE`
* `REDIS`
* `SECRET_KEY`

### ALLOWED_HOSTS

This is a list of the valid hostnames by which this server can be reached. You must specify at least one name or IP address.

Example:

```python
ALLOWED_HOSTS = ['netbox.example.com', '192.0.2.123']
```

### DATABASE

This parameter holds the database configuration details. You must define the username and password used when you configured PostgreSQL. If the service is running on a remote host, replace `localhost` with its address. See the [configuration documentation](../../configuration/required-settings/#database) for more detail on individual parameters.

Example:

```python
DATABASE = {
    'NAME': 'netbox',               # Database name
    'USER': 'netbox',               # PostgreSQL username
    'PASSWORD': 'J5brHrAXFLQSif0K', # PostgreSQL password
    'HOST': 'localhost',            # Database server
    'PORT': '',                     # Database port (leave blank for default)
    'CONN_MAX_AGE': 300,            # Max database connection age
}
```

### REDIS

Redis is a in-memory key-value store required as part of the NetBox installation. It is used for features such as webhooks and caching. Redis typically requires minimal configuration; the values below should suffice for most installations. See the [configuration documentation](../../configuration/required-settings/#redis) for more detail on individual parameters.

```python
REDIS = {
    'webhooks': {
        'HOST': 'redis.example.com',
        'PORT': 1234,
        'PASSWORD': 'foobar',
        'DATABASE': 0,
        'DEFAULT_TIMEOUT': 300,
        'SSL': False,
    },
    'caching': {
        'HOST': 'localhost',
        'PORT': 6379,
        'PASSWORD': '',
        'DATABASE': 1,
        'DEFAULT_TIMEOUT': 300,
        'SSL': False,
    }
}
```

### SECRET_KEY

Generate a random secret key of at least 50 alphanumeric characters. This key must be unique to this installation and must not be shared outside the local system.

You may use the script located at `netbox/generate_secret_key.py` to generate a suitable key.

!!! note
    In the case of a highly available installation with multiple web servers, `SECRET_KEY` must be identical among all servers in order to maintain a persistent user session state.

## Run Database Migrations

Before NetBox can run, we need to install the database schema. This is done by running `python3 manage.py migrate` from the `netbox` directory (`/opt/netbox/netbox/` in our example):

```no-highlight
(venv) # cd /opt/netbox/netbox/
(venv) # python3 manage.py migrate
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

```no-highlight
(venv) # python3 manage.py createsuperuser
Username: admin
Email address: admin@example.com
Password:
Password (again):
Superuser created successfully.
```

## Collect Static Files

```no-highlight
(venv) # python3 manage.py collectstatic --no-input

959 static files copied to '/opt/netbox/netbox/static'.
```

## Test the Application

At this point, NetBox should be able to run. We can verify this by starting a development instance:

```no-highlight
(venv) # python3 manage.py runserver 0.0.0.0:8000 --insecure
Performing system checks...

System check identified no issues (0 silenced).
November 28, 2018 - 09:33:45
Django version 2.0.9, using settings 'netbox.settings'
Starting development server at http://0.0.0.0:8000/
Quit the server with CONTROL-C.
```

Next, connect to the name or IP of the server (as defined in `ALLOWED_HOSTS`) on port 8000; for example, <http://127.0.0.1:8000/>. You should be greeted with the NetBox home page. Note that this built-in web service is for development and testing purposes only. **It is not suited for production use.**

!!! warning
    If the test service does not run, or you cannot reach the NetBox home page, something has gone wrong. Do not proceed with the rest of this guide until the installation has been corrected.

Note that the initial UI will be locked down for non-authenticated users.

![NetBox UI as seen by a non-authenticated user](../media/installation/netbox_ui_guest.png)

After logging in as the superuser you created earlier, all areas of the UI will be available.

![NetBox UI as seen by an administrator](../media/installation/netbox_ui_admin.png)
