[Redis](https://redis.io/) is an in-memory key-value store which NetBox employs for caching and queuing. This section entails the installation and configuration of a local Redis instance. If you already have a Redis service in place, skip to [the next section](3-netbox.md).

#### Ubuntu

```no-highlight
# apt-get install -y redis-server
```

#### CentOS

```no-highlight
# yum install -y redis
```

You may wish to modify the Redis configuration at `/etc/redis.conf` or `/etc/redis/redis.conf`, however in most cases the default configuration is sufficient.

## Verify Service Status

Use the `redis-cli` utility to ensure the Redis service is functional:

```no-highlight
$ redis-cli ping
PONG
```
