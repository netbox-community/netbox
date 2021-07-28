# Caching

NetBox supports database query caching using [django-cacheops](https://github.com/Suor/django-cacheops) and Redis. When a query is made, the results are cached in Redis for a short period of time, as defined by the [CACHE_TIMEOUT](../configuration/optional-settings.md#cache_timeout) parameter. Within that time, all recurrences of that specific query will return the pre-fetched results from the cache.

!!! warning
    In NetBox v2.11.10 and later queryset caching is disabled by default, and must be configured.

If a change is made to any of the objects returned by the query within that time, or if the timeout expires, the results are automatically invalidated and the next request for those results will be sent to the database.

## Invalidating Cached Data

Although caching is performed automatically and rarely requires administrative intervention, NetBox provides the `invalidate` management command to force invalidation of cached results. This command can reference a specific object by its type and numeric ID:

```no-highlight
$ python netbox/manage.py invalidate dcim.Device.34
```

Alternatively, it can also delete all cached results for an object type:

```no-highlight
$ python netbox/manage.py invalidate dcim.Device
```

Finally, calling it with the `all` argument will force invalidation of the entire cache database:

```no-highlight
$ python netbox/manage.py invalidate all
```
