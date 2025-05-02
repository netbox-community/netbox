# Default Value Parameters

## DEFAULT_DASHBOARD

This parameter controls the content and layout of user's default dashboard. Once the dashboard has been created, the user is free to customize it as they please by adding, removing, and reconfiguring widgets.

This parameter must specify an iterable of dictionaries, each representing a discrete dashboard widget and its configuration. The follow widget attributes are supported:

* `widget`: Dotted path to the Python class (required)
* `width`: Default widget width (between 1 and 12, inclusive)
* `height`: Default widget height, in rows
* `title`: Widget title
* `color`: Color of the widget's title bar, specified by name
* `config`: Dictionary mapping of any widget configuration parameters

A brief example configuration is provided below.

```python
DEFAULT_DASHBOARD = [
    {
        'widget': 'extras.ObjectCountsWidget',
        'width': 4,
        'height': 3,
        'title': 'Organization',
        'config': {
            'models': [
                'dcim.site',
                'tenancy.tenant',
                'tenancy.contact',
            ]
        }
    },
    {
        'widget': 'extras.ObjectCountsWidget',
        'width': 4,
        'height': 3,
        'title': 'IPAM',
        'color': 'blue',
        'config': {
            'models': [
                'ipam.prefix',
                'ipam.iprange',
                'ipam.ipaddress',
            ]
        }
    },
]
```

## DEFAULT_USER_PREFERENCES

!!! tip "Dynamic Configuration Parameter"

This is a dictionary defining the default preferences to be set for newly-created user accounts. For example, to set the default page size for all users to 100, define the following:

```python
DEFAULT_USER_PREFERENCES = {
    "pagination": {
        "per_page": 100
    }
}
```

For a complete list of available preferences, log into NetBox and navigate to `/user/preferences/`. A period in a preference name indicates a level of nesting in the JSON data. The example above maps to `pagination.per_page`.

---

## PAGINATE_COUNT

!!! tip "Dynamic Configuration Parameter"

Default: `50`

The default maximum number of objects to display per page within each list of objects.

---

## POWERFEED_DEFAULT_AMPERAGE

!!! tip "Dynamic Configuration Parameter"

Default: `15`

The default value for the `amperage` field when creating new power feeds.

---

## POWERFEED_DEFAULT_MAX_UTILIZATION

!!! tip "Dynamic Configuration Parameter"

Default: `80`

The default value (percentage) for the `max_utilization` field when creating new power feeds.

---

## POWERFEED_DEFAULT_VOLTAGE

!!! tip "Dynamic Configuration Parameter"

Default: `120`

The default value for the `voltage` field when creating new power feeds.

---

## RACK_ELEVATION_DEFAULT_UNIT_HEIGHT

!!! tip "Dynamic Configuration Parameter"

Default: `22`

Default height (in pixels) of a unit within a rack elevation. For best results, this should be approximately one tenth of `RACK_ELEVATION_DEFAULT_UNIT_WIDTH`.

---

## RACK_ELEVATION_DEFAULT_UNIT_WIDTH

!!! tip "Dynamic Configuration Parameter"

Default: `220`

Default width (in pixels) of a unit within a rack elevation.
