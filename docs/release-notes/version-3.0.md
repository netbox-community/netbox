# NetBox v3.0

## v3.0-beta1 (FUTURE)

### Breaking Changes

* The default CSV export format for all objects now includes all available data. Additionally, the CSV headers now use human-friendly titles rather than the raw field names.
* Support for queryset caching configuration (`caching_config`) has been removed from the plugins API (see [#6639](https://github.com/netbox-community/netbox/issues/6639)).
* The `cacheops_*` metrics have been removed from the Prometheus exporter (see [#6639](https://github.com/netbox-community/netbox/issues/6639)).

### New Features

### REST API Token Provisioning ([#5264](https://github.com/netbox-community/netbox/issues/5264))

This release introduces the `/api/users/tokens/` REST API endpoint, which includes a child endpoint that can be employed by a user to provision a new REST API token. This allows a user to gain REST API access without needing to first create a token via the web UI.

```
$ curl -X POST \
-H "Content-Type: application/json" \
-H "Accept: application/json; indent=4" \
https://netbox/api/users/tokens/provision/
{
    "username": "hankhill",
    "password: "I<3C3H8",
}
```

If the supplied credentials are valid, NetBox will create and return a new token for the user.

#### Custom Model Validation ([#5963](https://github.com/netbox-community/netbox/issues/5963))

This release introduces the [`CUSTOM_VALIDATORS`](../configuration/optional-settings.md#custom_validators) configuration parameter, which allows administrators to map NetBox models to custom validator classes to enforce custom validation logic. For example, the following configuration requires every site to have a name of at least ten characters and a description:

```python
from extras.validators import CustomValidator

CUSTOM_VALIDATORS = {
    'dcim.site': (
        CustomValidator({
            'name': {
                'min_length': 10,
            },
            'description': {
                'required': True,
            }
        }),
    )
}
```

CustomValidator can also be subclassed to enforce more complex logic by overriding its `validate()` method. See the [custom validation](../customization/custom-validation.md) documentation for more details.

### Enhancements

* [#2434](https://github.com/netbox-community/netbox/issues/2434) - Add option to assign IP address upon creating a new interface
* [#3665](https://github.com/netbox-community/netbox/issues/3665) - Enable rendering export templates via REST API
* [#3682](https://github.com/netbox-community/netbox/issues/3682) - Add `color` field to front and rear ports
* [#4609](https://github.com/netbox-community/netbox/issues/4609) - Allow marking prefixes as fully utilized
* [#5806](https://github.com/netbox-community/netbox/issues/5806) - Add kilometer and mile as choices for cable length unit
* [#6154](https://github.com/netbox-community/netbox/issues/6154) - Allow decimal values for cable lengths
* [#6590](https://github.com/netbox-community/netbox/issues/6590) - Introduce a nightly housekeeping command to clear expired sessions and change records

### Other Changes

* [#5532](https://github.com/netbox-community/netbox/issues/5532) - Drop support for Python 3.6
* [#5994](https://github.com/netbox-community/netbox/issues/5994) - Drop support for `display_field` argument on ObjectVar
* [#6068](https://github.com/netbox-community/netbox/issues/6068) - Drop support for legacy static CSV export
* [#6338](https://github.com/netbox-community/netbox/issues/6338) - Decimal fields are no longer coerced to strings in REST API
* [#6639](https://github.com/netbox-community/netbox/issues/6639) - Drop support for queryset caching (django-cacheops)

### REST API Changes

* Added the `/api/users/tokens/` endpoint
    * The `provision/` child endpoint can be used to provision new REST API tokens by supplying a valid username and password
* dcim.Cable
    * `length` is now a decimal value
* dcim.Device
    * Removed the `display_name` attribute (use `display` instead)
* dcim.DeviceType
    * Removed the `display_name` attribute (use `display` instead)
* dcim.FrontPort
    * Added `color` field
* dcim.FrontPortTemplate
    * Added `color` field
* dcim.Rack
    * Removed the `display_name` attribute (use `display` instead)
* dcim.RearPort
    * Added `color` field
* dcim.RearPortTemplate
    * Added `color` field
* dcim.Site
    * `latitude` and `longitude` are now decimal fields rather than strings
* extras.ContentType
    * Removed the `display_name` attribute (use `display` instead)
* ipam.Prefix
    * Added the `mark_utilized` boolean field
* ipam.VLAN
    * Removed the `display_name` attribute (use `display` instead)
* ipam.VRF
    * Removed the `display_name` attribute (use `display` instead)
* virtualization.VirtualMachine
    * `vcpus` is now a decimal field rather than a string
