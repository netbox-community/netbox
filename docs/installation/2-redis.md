# Redis Installation

## Install Redis

[Redis](https://redis.io/) is an in-memory key-value store which NetBox employs for caching and queuing. This section entails the installation and configuration of a local Redis instance. If you already have a Redis service in place, skip to [the next section](3-netbox.md).

!!! note
    NetBox v2.9.0 and later require Redis v4.0 or higher. If your distribution does not offer a recent enough release, you will need to build Redis from source. Please see [the Redis installation documentation](https://github.com/redis/redis) for further details.

### Ubuntu

```no-highlight
# apt-get install -y redis-server
```

### CentOS
We will be installing Redis server via remi repo, as netbox requires Redis v4.0 or later.
```no-highlight
# yum -y install http://rpms.remirepo.net/enterprise/remi-release-7.rpm
# yum --enablerepo=remi install redis
# systemctl start redis
# systemctl enable redis
```
Confirm if Redis v4.0 or later has been installed. 

```
# yum list installed | grep redis
redis.x86_64                       6.0.8-1.el7.remi                 @remi    
```

You may wish to modify the Redis configuration at `/etc/redis.conf` or `/etc/redis/redis.conf`, however in most cases the default configuration is sufficient.

## Verify Service Status

Use the `redis-cli` utility to ensure the Redis service is functional:

```no-highlight
$ redis-cli ping
PONG
```
