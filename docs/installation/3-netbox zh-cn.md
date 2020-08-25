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

本参数配置数据库连接信息. 配置 PostgreSQL 时必须指定用户名和密码. 如果服务运行在远程主机, 用相应地址替换 `localhost` . 各参数详细说明查看 [配置文档](../../configuration/required-settings/#database) .


例如:

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

Redis 是基于内存的 key-value 存储，是 NetBox 安装的必需部分. 主要用于 webhooks 和缓存. Redis 通常需要最小化配置; 如下参数满足大多数据应用场景. 各参数详细说明查看 [配置文档](../../configuration/required-settings/#redis) .

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

创建一个至少50个字符的包括数字、字符的随机密钥。此密钥必须对此安装唯一，且不应在本系统外使用。 

必须使用 `netbox/generate_secret_key.py` 创建一个相应的密钥.

!!! note

在具有多个web服务器的高可用性安装的情况下，所有服务器之间的, `SECRET_KEY` 必须相同，才能保存持久化的用户会话状态。

## 运行数据库迁移

在 NetBox 运行前, 必须安装数据库脚本. 在我们的示例里，通过在 `netbox` 目录 (`/opt/netbox/netbox/` )运行 `python3 manage.py migrate` :

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

如果本步骤报 PostgreSQL 验证错, 请确认在数据库安装时创建的用户名和密码与配置文件 `configuration.py` 中指定的相匹配。

## 创建超级用户

NetBox 未指定任何预置账户. 您首先必须创建一个超级用户以登录 NetBox:

```no-highlight
(venv) # python3 manage.py createsuperuser
Username: admin
Email address: admin@example.com
Password:
Password (again):
Superuser created successfully.
```

## 采集静态文件

```no-highlight
(venv) # python3 manage.py collectstatic --no-input

959 static files copied to '/opt/netbox/netbox/static'.
```

## 测试应用程序

当前, NetBox 应该可以运行了. 我们能够通过启动一个开发实例以进行确认：

```no-highlight
(venv) # python3 manage.py runserver 0.0.0.0:8000 --insecure
Performing system checks...

System check identified no issues (0 silenced).
November 28, 2018 - 09:33:45
Django version 2.0.9, using settings 'netbox.settings'
Starting development server at http://0.0.0.0:8000/
Quit the server with CONTROL-C.
```

然后, 使用在 (`ALLOWED_HOSTS` 中指定的地址)连接到服务器的 8000 端口; 例如, <http://127.0.0.1:8000/>. 然后就应该能够看到 NetBox 首页. 需要注意的是，内建的 Web 服务器只用于开发和测试目的. **不适合生产环境使用.**

!!! warning
    如果测试服务没有运行，或者您无法访问 NetBox 主页，则说明出现了问题。在纠正安装之前，不要继续执行本指南的其余部分。 

 请注意，对于未经身份验证的用户，初始UI将被锁定.

![未经身份验证的 NetBox 用户界面](../media/installation/netbox_ui_guest.png)

以先前创建的超级用户身份登录后，UI的所有区域都将可用。 

![NetBox 的管理员界面](../media/installation/netbox_ui_admin.png)
