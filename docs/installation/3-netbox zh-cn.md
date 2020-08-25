# NetBox 安装

本章节说明了如何安装和配置NetBox应用程序本身。

## 安装必备软件包

首先安装NetBox及其依赖项所需的所有系统软件包。请注意，从 NetBox v2.8 开始，需要 Python 3.6 或更高版本。


### Ubuntu

```no-highlight
# apt-get install -y python3.6 python3-pip python3-venv python3-dev build-essential libxml2-dev libxslt1-dev libffi-dev libpq-dev libssl-dev zlib1g-dev
```

### CentOS

```no-highlight
# yum install -y gcc python36 python36-devel python36-setuptools libxml2-devel libxslt-devel libffi-devel openssl-devel redhat-rpm-config
# easy_install-3.6 pip
```

## 下载 NetBox

您可以选择从指定版本安装NetBox，也可以通过在GitHub上克隆其存储库的主分支来安装NetBox。

### 选择 A: 下载特定的发布版

从GitHub下载 [最新稳定版本](https://github.com/netbox-community/netbox/releases) 的tarball或ZIP归档文件，并将其解压缩到所需的路径。在本例中，我们将使用 `/opt/netbox`。

```no-highlight
# wget https://github.com/netbox-community/netbox/archive/vX.Y.Z.tar.gz
# tar -xzf vX.Y.Z.tar.gz -C /opt
# cd /opt/
# ln -s netbox-X.Y.Z/ netbox
# cd /opt/netbox/
```

### 选择 B: 从 Git 存储库克隆

为 NetBox 安装创建基础目录. 本指南中, 我们使用 `/opt/netbox`.

```no-highlight
# mkdir -p /opt/netbox/ && cd /opt/netbox/
```

如果未安装 `git` , 使用如下命令进行安装:

#### Ubuntu

```no-highlight
# apt-get install -y git
```

#### CentOS

```no-highlight
# yum install -y git
```

其次, 克隆 Git 存储库的 **master** 分支到当前目录:

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

## 创建 NetBox 用户

创建名为 `netbox` 的系统用户帐户。我们将配置WSGI和HTTP服务在该帐户下运行。我们还将为这个用户分配媒体文件目录的所有权。以确保 NetBox 能够保存本地文件。

#### Ubuntu

```
# adduser --system --group netbox
# chown --recursive netbox /opt/netbox/netbox/media/
```

#### CentOS

```
# groupadd --system netbox
# adduser --system -g netbox netbox
# chown --recursive netbox /opt/netbox/netbox/media/
```

## 设置 Python 环境

我们将使用 Python [虚拟环境](https://docs.python.org/3.6/tutorial/venv.html) 以确保 NetBox 所需的软件包不会与基本系统中的任何内容发生冲突。这将在 NetBox 根目录中创建一个名为 `venv` 的目录。

```no-highlight
# python3 -m venv /opt/netbox/venv
```

接下来，激活虚拟环境并安装所需的 Python 包。您应该会看到控制台提示更改成了相应的活动环境。（激活虚拟环境将更新命令 shell ，以使用我们刚刚为 NetBox 安装的 Python 本地副本，而不是系统的 Python 解释器）


```no-highlight
# source venv/bin/activate
(venv) # pip3 install -r requirements.txt
```

### NAPALM 自动化 (可选)

NetBox支持与 [NAPALM automation](https://napalm-automation.net/) 库的集成。NAPALM 允许 NetBox 从设备获取实时数据，并通过 REST API 将其返回给请求者。安装 NAPALM 是可选的。要启用它，请安装 `napalm` 包：

```no-highlight
(venv) # pip3 install napalm
```

为保证在特性升级时 NAPALM 自动重新安装, 在 NetBox 根目录下创建一个名为 `local_requirements.txt` 的文件 (类似 `requirements.txt`) 并列入 `napalm` 包:

```no-highlight
# echo napalm >> local_requirements.txt
```

### 远程文件存储 (可选)

缺省情况下, NetBox 使用本地文件系统存储上传的文件. 使用远程文件存储时需要, 安装 [`django-storages`](https://django-storages.readthedocs.io/en/stable/) 库并在 `configuration.py` 中配置 [desired backend](../../configuration/optional-settings/#storage_backend) .


```no-highlight
(venv) # pip3 install django-storages
```

不要忘记增加 `django-storages` 包名到 `local_requirements.txt` 文件，以确保在特性升级时也能被自动重新安装:


```no-highlight
# echo django-storages >> local_requirements.txt
```

## 配置

进入 NetBox 配置目录，并基于 `configuration.example.py` 文件复制一份为 `configuration.py`.

```no-highlight
(venv) # cd netbox/netbox/
(venv) # cp configuration.example.py configuration.py
```

以您常用的编辑器打开 `configuration.py` 并配置如下变量:

* `ALLOWED_HOSTS`
* `DATABASE`
* `REDIS`
* `SECRET_KEY`

### ALLOWED_HOSTS

配置服务器能使用的有效的主机名. 必须指定至少一个名称或IP地址. 


例如:

```python
ALLOWED_HOSTS = ['netbox.example.com', '192.0.2.123']
```

### DATABASE

本参数配置数据库连接信息. You must define the username and password used when you configured PostgreSQL. If the service is running on a remote host, replace `localhost` with its address. See the [configuration documentation](../../configuration/required-settings/#database) for more detail on individual parameters.


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
    'tasks': {
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
