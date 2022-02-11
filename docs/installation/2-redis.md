# Redis Installation

## Install Redis

[Redis](https://redis.io/) is an in-memory key-value store which NetBox employs for caching and queuing. This section entails the installation and configuration of a local Redis instance. If you already have a Redis service in place, skip to [the next section](3-netbox.md).

!!! warning "Redis v4.0 or later required"
    NetBox v2.9.0 and later require Redis v4.0 or higher. If your distribution does not offer a recent enough release, you will need to build Redis from source. Please see [the Redis installation documentation](https://github.com/redis/redis) for further details.

=== "Ubuntu"

    ```no-highlight
    sudo apt install -y redis-server
    ```

=== "CentOS"

    ```no-highlight
    sudo yum install -y redis
    sudo systemctl start redis
    sudo systemctl enable redis
    ```

Before continuing, verify that your installed version of Redis is at least v4.0:

```no-highlight
redis-server -v
```

You may wish to modify the Redis configuration at `/etc/redis.conf` or `/etc/redis/redis.conf`, however in most cases the default configuration is sufficient.

## Verify Service Status

Use the `redis-cli` utility to ensure the Redis service is functional:

```no-highlight
redis-cli ping
```

If successful, you should receive a `PONG` response from the server.
