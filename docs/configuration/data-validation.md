# Data & Validation Parameters

## CUSTOM_VALIDATORS

!!! tip "Dynamic Configuration Parameter"

This is a mapping of models to [custom validators](../customization/custom-validation.md) that have been defined locally to enforce custom validation logic. An example is provided below:

```python
CUSTOM_VALIDATORS = {
    "dcim.Site": [
        {
            "name": {
                "min_length": 5,
                "max_length": 30
            }
        },
        "my_plugin.validators.Validator1"
    ],
    "dcim.Device": [
        "my_plugin.validators.Validator1"
    ]
}
```

!!! info "Case-Insensitive Model Names"
    Model identifiers are case-insensitive. Both `dcim.site` and `dcim.Site` are valid and equivalent.

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

In addition to plain tuples, each choice may be defined as a dictionary, which allows specifying a description (shown as a subtitle beneath the option) alongside the value, label, and color. `value` and `label` are required; `color` and `description` are optional:

```python
FIELD_CHOICES = {
    'dcim.Site.status': (
        {'value': 'foo', 'label': 'Foo', 'color': 'red', 'description': 'The foo status'},
        {'value': 'bar', 'label': 'Bar', 'color': 'green'},
    )
}
```

!!! info "New in NetBox v4.7"
    The dictionary-based format for declaring choices was introduced in NetBox v4.7. The tuple-based format remains supported, but will be deprecated in a future release and support for it will eventually be removed.

!!! info "Case-Insensitive Field Identifiers"
    Field identifiers are case-insensitive. Both `dcim.Site.status` and `dcim.site.status` are valid and equivalent.

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

---

## PROTECTION_RULES

!!! tip "Dynamic Configuration Parameter"

This is a mapping of models to [custom validators](../customization/custom-validation.md) against which an object is evaluated immediately prior to its deletion. If validation fails, the object is not deleted. An example is provided below:

```python
PROTECTION_RULES = {
    "dcim.Site": [
        {
            "status": {
                "eq": "decommissioning"
            }
        },
        "my_plugin.validators.Validator1",
    ]
}
```

!!! info "Case-Insensitive Model Names"
    Model identifiers are case-insensitive. Both `dcim.site` and `dcim.Site` are valid and equivalent.
