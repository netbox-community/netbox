# NetBox v3.6

## v3.6.0 (FUTURE)

### Breaking Changes

* PostgreSQL 11 is no longer supported (due to adopting Django 4.2). NetBox v3.6 requires PostgreSQL 12 or later.
* The `napalm_driver` and `napalm_args` fields (which were deprecated in v3.5) have been removed from the platform model.

### Enhancements

* [#11305](https://github.com/netbox-community/netbox/issues/11305) - Add GPS coordinate fields to the device model
* [#12175](https://github.com/netbox-community/netbox/issues/12175) - Permit racks to start numbering at values greater than one

### Other Changes

* [#9077](https://github.com/netbox-community/netbox/issues/9077) - Prevent the errant execution of dangerous instance methods in Django templates
* [#11766](https://github.com/netbox-community/netbox/issues/11766) - Remove obsolete custom `ChoiceField` and `MultipleChoiceField` classes
* [#12180](https://github.com/netbox-community/netbox/issues/12180) - All API endpoints for available objects (e.g. IP addresses) now inherit from a common parent view
* [#12794](https://github.com/netbox-community/netbox/issues/12794) - Avoid direct imports of Django's stock user model
* [#12320](https://github.com/netbox-community/netbox/issues/12320) - Remove obsolete fields `napalm_driver` and `napalm_args` from Platform
* [#12964](https://github.com/netbox-community/netbox/issues/12964) - Drop support for PostgreSQL
