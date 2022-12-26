# Data & Validation Parameters

## CUSTOM_VALIDATORS

!!! tip "Dynamic Configuration Parameter"

This is a mapping of models to [custom validators](../customization/custom-validation.md) that have been defined locally to enforce custom validation logic. An example is provided below:

```python
CUSTOM_VALIDATORS = {
    "dcim.site": [
        {
            "name": {
                "min_length": 5,
                "max_length": 30
            }
        },
        "my_plugin.validators.Validator1"
    ],
    "dim.device": [
        "my_plugin.validators.Validator1"
    ]
}
```

---

## FIELD_CHOICES

Some static choice fields on models can be configured with custom values. This is done by defining `FIELD_CHOICES` as a dictionary mapping model fields to their choices. Each choice in the list must have a database value and a human-friendly label, and may optionally specify a color. (A list of available colors is provided below.)

The choices provided can either replace the stock choices provided by NetBox, or append to them. To _replace_ the available choices, specify the app, model, and field name separated by dots. For example, the site model would be referenced as `dcim.Site.status`. To _extend_ the available choices, append a plus sign to the end of this string (e.g. `dcim.Site.status+`).

For example, the following configuration would replace the default site status choices with the options Foo, Bar, and Baz:

```python
FIELD_CHOICES = {
    'dcim.Site.status': (
        ('foo', 'Foo', 'red'),
        ('bar', 'Bar', 'green'),
        ('baz', 'Baz', 'blue'),
    )
}
```

Appending a plus sign to the field identifier would instead _add_ these choices to the ones already offered:

```python
FIELD_CHOICES = {
    'dcim.Site.status+': (
        ...
    )
}
```

The following model fields support configurable choices:

* `circuits.Circuit.status`
* `dcim.Device.status`
* `dcim.Location.status`
* `dcim.Module.status`
* `dcim.PowerFeed.status`
* `dcim.Rack.status`
* `dcim.Site.status`
* `dcim.VirtualDeviceContext.status`
* `extras.JournalEntry.kind`
* `ipam.IPAddress.status`
* `ipam.IPRange.status`
* `ipam.Prefix.status`
* `ipam.VLAN.status`
* `virtualization.Cluster.status`
* `virtualization.VirtualMachine.status`
* `wireless.WirelessLAN.status`

The following colors are supported:

* `blue`
* `indigo`
* `purple`
* `pink`
* `red`
* `orange`
* `yellow`
* `green`
* `teal`
* `cyan`
* `gray`
* `black`
* `white`
