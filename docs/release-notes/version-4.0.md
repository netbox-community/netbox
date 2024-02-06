# NetBox v4.0

## v4.0.0 (FUTURE)

### New Features

#### Complete UI Refresh ([#12128](https://github.com/netbox-community/netbox/issues/12128))

The NetBox user interface has been completely refreshed and updated.

### Enhancements

* [#12851](https://github.com/netbox-community/netbox/issues/12851) - Replace bleach HTML sanitization library with nh3
* [#14637](https://github.com/netbox-community/netbox/issues/14637) - Upgrade to Django 5.0
* [#14672](https://github.com/netbox-community/netbox/issues/14672) - Add support for Python 3.12
* [#14728](https://github.com/netbox-community/netbox/issues/14728) - The plugins list view has been moved from the legacy admin UI to the main NetBox UI
* [#14729](https://github.com/netbox-community/netbox/issues/14729) - All background task views have been moved from the legacy admin UI to the main NetBox UI

### Other Changes

* [#12325](https://github.com/netbox-community/netbox/issues/12325) - The Django admin UI is now disabled by default (set `DJANGO_ADMIN_ENABLED` to True to enable it)
* [#12795](https://github.com/netbox-community/netbox/issues/12795) - NetBox now uses a custom User model rather than the stock model provided by Django
* [#13647](https://github.com/netbox-community/netbox/issues/13647) - Squash all database migrations prior to v3.7
* [#14092](https://github.com/netbox-community/netbox/issues/14092) - Remove backward compatibility for importing plugin resources from `extras.plugins` (now `netbox.plugins`)
* [#14638](https://github.com/netbox-community/netbox/issues/14638) - Drop support for Python 3.8 and 3.9
* [#14657](https://github.com/netbox-community/netbox/issues/14657) - Remove backward compatibility for old permissions mapping under `ActionsMixin`
* [#14658](https://github.com/netbox-community/netbox/issues/14658) - Remove backward compatibility for importing `process_webhook()` (now `extras.webhooks.send_webhook()`)
* [#14740](https://github.com/netbox-community/netbox/issues/14740) - Remove the obsolete `BootstrapMixin` form mixin class
