# NetBox v3.0

## v3.0-beta1 (FUTURE)

### Breaking Changes

* The default CSV export format for all objects now includes all available data. Additionally, the CSV headers now use human-friendly titles rather than the raw field names.

### New Features

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

CustomValidator can also be subclassed to enforce more complex logic by overriding its `validate()` method. See the [custom validation](../additional-features/custom-validation.md) documentation for more details.

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

### REST API Changes

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
