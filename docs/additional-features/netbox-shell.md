NetBox includes a Python shell within which objects can be directly queried, created, modified, and deleted. To enter the shell, run the following command:

```
./manage.py nbshell
```

This will launch a customized version of [the built-in Django shell](https://docs.djangoproject.com/en/dev/ref/django-admin/#shell) with all relevant NetBox models pre-loaded. (If desired, the stock Django shell is also available by executing `./manage.py shell`.)

```
$ ./manage.py nbshell
### NetBox interactive shell (jstretch-laptop)
### Python 2.7.6 | Django 1.11.3 | NetBox 2.1.0-dev
### lsmodels() will show available models. Use help(<model>) for more info.
```

The function `lsmodels()` will print a list of all available NetBox models:

```
>>> lsmodels()
DCIM:
  ConsolePort
  ConsolePortTemplate
  ConsoleServerPort
  ConsoleServerPortTemplate
  Device
  ...
```

## Querying Objects

Objects are retrieved by forming a [Django queryset](https://docs.djangoproject.com/en/dev/topics/db/queries/#retrieving-objects). The base queryset for an object takes the form `<model>.objects.all()`, which will return a (truncated) list of all objects of that type.

```
>>> Device.objects.all()
<QuerySet [<Device: TestDevice1>, <Device: TestDevice2>, <Device: TestDevice3>, <Device: TestDevice4>, <Device: TestDevice5>, '...(remaining elements truncated)...']>
```

Use a `for` loop to cycle through all objects in the list:

```
>>> for device in Device.objects.all():
...   print(device.name, device.device_type)
...
(u'TestDevice1', <DeviceType: PacketThingy 9000>)
(u'TestDevice2', <DeviceType: PacketThingy 9000>)
(u'TestDevice3', <DeviceType: PacketThingy 9000>)
(u'TestDevice4', <DeviceType: PacketThingy 9000>)
(u'TestDevice5', <DeviceType: PacketThingy 9000>)
...
```

To count all objects matching the query, replace `all()` with `count()`:

```
>>> Device.objects.count()
1274
```

To retrieve a particular object (typically by its primary key or other unique field), use `get()`:

```
>>> Site.objects.get(pk=7)
<Site: Test Lab>
```

### Filtering Querysets

In most cases, you want to retrieve only a specific subset of objects. To filter a queryset, replace `all()` with `filter()` and pass one or more keyword arguments. For example:

```
>>> Device.objects.filter(status=STATUS_ACTIVE)
<QuerySet [<Device: TestDevice1>, <Device: TestDevice2>, <Device: TestDevice3>, <Device: TestDevice8>, <Device: TestDevice9>, '...(remaining elements truncated)...']>
```

Querysets support slicing to return a specific range of objects.

```
>>> Device.objects.filter(status=STATUS_ACTIVE)[:3]
<QuerySet [<Device: TestDevice1>, <Device: TestDevice2>, <Device: TestDevice3>]>
```

The `count()` method can be appended to the queryset to return a count of objects rather than the full list.

```
>>> Device.objects.filter(status=STATUS_ACTIVE).count()
982
```

Relationships with other models can be traversed by concatenating field names with a double-underscore. For example, the following will return all devices assigned to the tenant named "Pied Piper."

```
>>> Device.objects.filter(tenant__name='Pied Piper')
```

This approach can span multiple levels of relations. For example, the following will return all IP addresses assigned to a device in North America:

```
>>> IPAddress.objects.filter(interface__device__site__region__slug='north-america')
```

!!! note
    While the above query is functional, it is very inefficient. There are ways to optimize such requests, however they are out of the scope of this document. For more information, see the [Django queryset method reference](https://docs.djangoproject.com/en/dev/ref/models/querysets/) documentation.

Reverse relationships can be traversed as well. For example, the following will find all devices with an interface named "em0":

```
>>> Device.objects.filter(interfaces__name='em0')
```

Character fields can be filtered against partial matches using the `contains` or `icontains` field lookup (the later of which is case-insensitive).

```
>>> Device.objects.filter(name__icontains='testdevice')
```

Similarly, numeric fields can be filtered by values less than, greater than, and/or equal to a given value.

```
>>> VLAN.objects.filter(vid__gt=2000)
```

Multiple filters can be combined to further refine a queryset.

```
>>> VLAN.objects.filter(vid__gt=2000, name__icontains='engineering')
```

To return the inverse of a filtered queryset, use `exclude()` instead of `filter()`.

```
>>> Device.objects.count()
4479
>>> Device.objects.filter(status=STATUS_ACTIVE).count()
4133
>>> Device.objects.exclude(status=STATUS_ACTIVE).count()
346
```

!!! info
    The examples above are intended only to provide a cursory introduction to queryset filtering. For an exhaustive list of the available filters, please consult the [Django queryset API docs](https://docs.djangoproject.com/en/dev/ref/models/querysets/).

## Creating and Updating Objects

New objects can be created by instantiating the desired model, defining values for all required attributes, and calling `save()` on the instance.

```
>>> lab1 = Site.objects.get(pk=7)
>>> myvlan = VLAN(vid=123, name='MyNewVLAN', site=lab1)
>>> myvlan.save()
```

Alternatively, the above can be performed as a single operation:

```
>>> VLAN(vid=123, name='MyNewVLAN', site=Site.objects.get(pk=7)).save()
```

To modify an object, retrieve it, update the desired field(s), and call `save()` again.

```
>>> vlan = VLAN.objects.get(pk=1280)
>>> vlan.name
u'MyNewVLAN'
>>> vlan.name = 'BetterName'
>>> vlan.save()
>>> VLAN.objects.get(pk=1280).name
u'BetterName'
```

!!! warning
    The Django ORM provides methods to create/edit many objects at once, namely `bulk_create()` and `update()`. These are best avoided in most cases as they bypass a model's built-in validation and can easily lead to database corruption if not used carefully.

## Deleting Objects

To delete an object, simply call `delete()` on its instance. This will return a dictionary of all objects (including related objects) which have been deleted as a result of this operation.

```
>>> vlan
<VLAN: 123 (BetterName)>
>>> vlan.delete()
(1, {u'extras.CustomFieldValue': 0, u'ipam.VLAN': 1})
```

To delete multiple objects at once, call `delete()` on a filtered queryset. It's a good idea to always sanity-check the count of selected objects _before_ deleting them.

```
>>> Device.objects.filter(name__icontains='test').count()
27
>>> Device.objects.filter(name__icontains='test').delete()
(35, {u'extras.CustomFieldValue': 0, u'dcim.DeviceBay': 0, u'secrets.Secret': 0, u'dcim.InterfaceConnection': 4, u'extras.ImageAttachment': 0, u'dcim.Device': 27, u'dcim.Interface': 4, u'dcim.ConsolePort': 0, u'dcim.PowerPort': 0})
```

!!! warning
    Deletions are immediate and irreversible. Always think very carefully before calling `delete()` on an instance or queryset.
