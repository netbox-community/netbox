# PostgreSQL 数据库安装

本节说明了如何安装和配置本地PostgreSQL数据库。如果您已经有了PostgreSQL数据库服务，请跳到 [下一节](2-redis.md).


!!! 警告
    NetBox 需要 PostgreSQL 9.6 或更高。 请注意 **不** 支持 MySQL 及其它关系数据库.

这里提供的安装说明已经在 Ubuntu 18.04 及 CentOS 7.5 上进行了测试。在其他发行版上安装依赖项所需的相应命令可能会有很大不同。不幸的是，这超出了 NetBox 维护人员的能力范围。请参考发行版的文档以获得相应错误的帮助。

## 安装 

#### Ubuntu

如果您的发行版的包管理器中没有 PostgreSQL 的最新版本，则需要从官方的 [PostgreSQL repository](https://wiki.postgresql.org/wiki/Apt) 安装它.

```no-highlight
# apt-get update
# apt-get install -y postgresql libpq-dev
```

#### CentOS

CentOS 7.5 没有提供 PostgreSQL 的最新版本，因此需要从外部存储库安装它。下面的说明显示了 PostgreSQL 9.6 的安装，但是您可以选择安装更新的版本。

```no-highlight
# yum install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm
# yum install -y postgresql96 postgresql96-server postgresql96-devel
# /usr/pgsql-9.6/bin/postgresql96-setup initdb
```

CentOS 用户需要修改 PostgreSQL 的 `/var/lib/pgsql/9.6/data/pg_hba.conf` 配置文件，即将所有 host 项的 `ident` 使用 `md5` 进行替代，以支持基于密码的认证 . 如:

```no-highlight
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
```

然后启动服务，并允许其开机启动:

```no-highlight
# systemctl start postgresql-9.6
# systemctl enable postgresql-9.6
```

## 创建数据库

我们至少需要为 NetBox 创建一个数据库，并创建单独的用户（指定用户名和密码），以进行用户认证。

!!! 危险
    请不要在真实环境里使用示例中的密码.

```no-highlight
# sudo -u postgres psql
psql (10.10)
Type "help" for help.

postgres=# CREATE DATABASE netbox;
CREATE DATABASE
postgres=# CREATE USER netbox WITH PASSWORD 'J5brHrAXFLQSif0K';
CREATE ROLE
postgres=# GRANT ALL PRIVILEGES ON DATABASE netbox TO netbox;
GRANT
postgres=# \q
```

## 确认服务状态

您可以使用以下命令并提供相应的密码来验证创建的用户是否有效。（如果使用远程数据库，请将 `localhost` 替换为数据库服务器地址。）


```no-highlight
# psql -U netbox -W -h localhost netbox
```

正确的情况下, 您将进入 `netbox` 提示符. 输入 `\q` 以退出.
