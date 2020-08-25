# Redis 安装

## 安装 Redis

[Redis](https://redis.io/) 是一个基于内存的 key-value 存储，NetBox 基于其进行缓存和队列. 本节说明了如何安装和配置本地Redis实例。如果您已经有了Redis服务，请跳到 [下一节](3-netbox.md) .

### Ubuntu

```no-highlight
# apt-get install -y redis-server
```

### CentOS

```no-highlight
# yum install -y epel-release
# yum install -y redis
# systemctl start redis
# systemctl enable redis
```

您可以修改 Redis 位于 `/etc/redis.conf` 或 `/etc/redis/redis.conf` 下的配置信息, 通常情况下默认配置即可满足使用要求.

## 确认服务状态

使用 `redis-cli` 工具确认 Redis 服务可用:

```no-highlight
$ redis-cli ping
PONG
```
