# Caching

To improve performance, NetBox supports caching for most object and list views. Caching is implemented using Redis,
and [django-cacheops](https://github.com/Suor/django-cacheops)

Several management commands are avaliable for administrators to manually invalidate cache entries in extenuating circumstances.

To invalidate a specifc model instance (for example a Device with ID 34):
```
python netbox/manage.py invalidate dcim.Device.34
```

To invalidate all instance of a model:
```
python netbox/manage.py invalidate dcim.Device
```

To flush the entire cache database:
```
python netbox/manage.py invalidate all
```
