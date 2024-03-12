# NetBox v4.0

## v4.0.0 (FUTURE)

### Breaking Changes

* The deprecated `device_role` & `device_role_id` filters for devices have been removed. (Use `role` and `role_id` instead.)
* The legacy reports functionality has been dropped. Reports will be automatically converted to custom scripts on upgrade.

### New Features

#### Complete UI Refresh ([#12128](https://github.com/netbox-community/netbox/issues/12128))

The NetBox user interface has been completely refreshed and updated.

#### Dynamic REST API Fields ([#15087](https://github.com/netbox-community/netbox/issues/15087))

The REST API now supports specifying which fields to include in the response data.

### Enhancements

* [#12851](https://github.com/netbox-community/netbox/issues/12851) - Replace bleach HTML sanitization library with nh3
* [#13283](https://github.com/netbox-community/netbox/issues/13283) - Display additional context on API-backed dropdown fields
* [#14237](https://github.com/netbox-community/netbox/issues/14237) - Automatically clear dependent selection fields when modifying a parent selection
* [#14637](https://github.com/netbox-community/netbox/issues/14637) - Upgrade to Django 5.0
* [#14672](https://github.com/netbox-community/netbox/issues/14672) - Add support for Python 3.12
* [#14728](https://github.com/netbox-community/netbox/issues/14728) - The plugins list view has been moved from the legacy admin UI to the main NetBox UI
* [#14729](https://github.com/netbox-community/netbox/issues/14729) - All background task views have been moved from the legacy admin UI to the main NetBox UI
* [#14438](https://github.com/netbox-community/netbox/issues/14438) - Track individual custom scripts as database objects
* [#15131](https://github.com/netbox-community/netbox/issues/15131) - Automatically annotate related object counts on REST API querysets
* [#15238](https://github.com/netbox-community/netbox/issues/15238) - Include the `description` field in "brief" REST API serializations

### Other Changes

* [#12325](https://github.com/netbox-community/netbox/issues/12325) - The Django admin UI is now disabled by default (set `DJANGO_ADMIN_ENABLED` to True to enable it)
* [#12510](https://github.com/netbox-community/netbox/issues/12510) - Dropped support for legacy reports
* [#12795](https://github.com/netbox-community/netbox/issues/12795) - NetBox now uses custom User and Group models rather than the stock models provided by Django
* [#13647](https://github.com/netbox-community/netbox/issues/13647) - Squash all database migrations prior to v3.7
* [#14092](https://github.com/netbox-community/netbox/issues/14092) - Remove backward compatibility for importing plugin resources from `extras.plugins` (now `netbox.plugins`)
* [#14638](https://github.com/netbox-community/netbox/issues/14638) - Drop support for Python 3.8 and 3.9
* [#14657](https://github.com/netbox-community/netbox/issues/14657) - Remove backward compatibility for old permissions mapping under `ActionsMixin`
* [#14658](https://github.com/netbox-community/netbox/issues/14658) - Remove backward compatibility for importing `process_webhook()` (now `extras.webhooks.send_webhook()`)
* [#14740](https://github.com/netbox-community/netbox/issues/14740) - Remove the obsolete `BootstrapMixin` form mixin class
* [#15042](https://github.com/netbox-community/netbox/issues/15042) - Rearchitect the logic for registering models & model features
* [#15099](https://github.com/netbox-community/netbox/issues/15099) - Remove obsolete `device_role` and `device_role_id` filters for devices
* [#15100](https://github.com/netbox-community/netbox/issues/15100) - Remove obsolete `NullableCharField` class
* [#15277](https://github.com/netbox-community/netbox/issues/15277) - Replace references to ContentType without ObjectType proxy model & standardize field names
* [#15292](https://github.com/netbox-community/netbox/issues/15292) - Remove obsolete `device_role` attribute from Device model (this field was renamed to `role` in v3.6)

### REST API Changes

* The `/api/extras/content-types/` endpoint has moved to `/api/extras/object-types/`
* dcim.Device
  * The obsolete read-only attribute `device_role` has been removed (replaced by `role` in v3.6)
* extras.CustomField
  * `content_types` has been renamed to `object_types`
  * The `content_types` filter is now `object_type`
  * The `content_type_id` filter is now `object_type_id`
* extras.CustomLink
  * `content_types` has been renamed to `object_types`
  * The `content_types` filter is now `object_type`
  * The `content_type_id` filter is now `object_type_id`
* extras.EventRule
  * `content_types` has been renamed to `object_types`
  * The `content_types` filter is now `object_type`
  * The `content_type_id` filter is now `object_type_id`
* extras.ExportTemplate
  * `content_types` has been renamed to `object_types`
  * The `content_types` filter is now `object_type`
  * The `content_type_id` filter is now `object_type_id`
* extras.ImageAttachment
  * `content_type` has been renamed to `object_type`
  * The `content_type` filter is now `object_type`
* extras.SavedFilter
  * `content_types` has been renamed to `object_types`
  * The `content_types` filter is now `object_type`
  * The `content_type_id` filter is now `object_type_id`
* tenancy.ContactAssignment
  * `content_type` has been renamed to `object_type`
  * The `content_type_id` filter is now `object_type_id`
