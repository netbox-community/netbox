# Redis Installation

## Install Redis

[Redis](https://redis.io/) is an in-memory key-value store which NetBox employs for caching and queuing. This section entails the installation and configuration of a local Redis instance. If you already have a Redis service in place, skip to [the next section](3-netbox.md).

```no-highlight
sudo apt install -y redis-server
```

Before continuing, verify that your installed version of Redis is at least v6.0:

!!! warning "Redis v5.x is deprecated"
    Support for Redis versions older than 6.0 is deprecated and will be removed in NetBox v4.7.

```no-highlight
redis-server -v
```

You may wish to modify the Redis configuration at `/etc/redis.conf` or `/etc/redis/redis.conf`, however in most cases the default configuration is sufficient.

!!! danger "Restrict access to Redis"
    NetBox's background workers execute jobs read from Redis, so anyone able to write to the `tasks` database can run
    arbitrary code on a worker. Treat Redis as trusted infrastructure: keep it bound to `localhost` (the default) or a
    private network, and enable authentication if it is reachable by any other host. See
    [Redis configuration](../configuration/required-parameters.md#redis) for details.

## Verify Service Status

Use the `redis-cli` utility to ensure the Redis service is functional:

```no-highlight
redis-cli ping
```

If successful, you should receive a `PONG` response from the server.
