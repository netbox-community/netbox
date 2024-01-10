# NetBox v4.0

## v4.0.0 (FUTURE)

### Enhancements

* [#14637](https://github.com/netbox-community/netbox/issues/14637) - Upgrade to Django 5.0
* [#14672](https://github.com/netbox-community/netbox/issues/14672) - Add support for Python 3.12

### Other Changes

* [#14092](https://github.com/netbox-community/netbox/issues/14092) - Remove backward compatibility for importing plugin resources from `extras.plugins` (now `netbox.plugins`)
* [#14638](https://github.com/netbox-community/netbox/issues/14638) - Drop support for Python 3.8 and 3.9
* [#14657](https://github.com/netbox-community/netbox/issues/14657) - Remove backward compatibility for old permissions mapping under `ActionsMixin`
* [#14658](https://github.com/netbox-community/netbox/issues/14658) - Remove backward compatibility for importing `process_webhook()` (now `extras.webhooks.send_webhook()`)
