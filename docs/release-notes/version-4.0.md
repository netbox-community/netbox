# NetBox v4.0

## v4.0.2 (FUTURE)

---

## v4.0.1 (2024-05-09)

### Enhancements

* [#15148](https://github.com/netbox-community/netbox/issues/15148) - Add copy-to-clipboard button for config context data
* [#15328](https://github.com/netbox-community/netbox/issues/15328) - Add a virtual machines UI tab for host devices
* [#15451](https://github.com/netbox-community/netbox/issues/15451) - Add 2.5 and 5 Gbps backplane Ethernet interface types
* [#16010](https://github.com/netbox-community/netbox/issues/16010) - Enable Prometheus middleware only if metrics are enabled

### Bug Fixes

* [#15968](https://github.com/netbox-community/netbox/issues/15968) - Avoid resizing quick search field to display clear button
* [#15973](https://github.com/netbox-community/netbox/issues/15973) - Fix AttributeError exception when modifying cable termination type
* [#15977](https://github.com/netbox-community/netbox/issues/15977) - Hide all admin menu items for non-authenticated users
* [#15982](https://github.com/netbox-community/netbox/issues/15982) - Restore the "assign IP" tab for assigning existing IP addresses to interfaces
* [#15992](https://github.com/netbox-community/netbox/issues/15992) - Fix AttributeError exception when Sentry integration is enabled
* [#15995](https://github.com/netbox-community/netbox/issues/15995) - Permit nullable fields referenced by unique constraints to be omitted from REST API requests
* [#15999](https://github.com/netbox-community/netbox/issues/15999) - Fix layout of login form labels for certain languages
* [#16003](https://github.com/netbox-community/netbox/issues/16003) - Enable cache busting for `setmode.js` asset to avoid breaking dark mode support on upgrade
* [#16011](https://github.com/netbox-community/netbox/issues/16011) - Fix site tenant assignment by PK via REST API
* [#16020](https://github.com/netbox-community/netbox/issues/16020) - Include Python version in system UI view
* [#16022](https://github.com/netbox-community/netbox/issues/16022) - Fix database migration failure when encountering a script module which no longer exists on disk
* [#16025](https://github.com/netbox-community/netbox/issues/16025) - Fix execution of scripts via the `runscript` management command
* [#16031](https://github.com/netbox-community/netbox/issues/16031) - Render Markdown content in script log messages
* [#16051](https://github.com/netbox-community/netbox/issues/16051) - Translate "empty" text for object tables
* [#16061](https://github.com/netbox-community/netbox/issues/16061) - Omit hidden fields from display within event rule edit form

---

## v4.0.0 (2024-05-06)

!!! tip "Plugin Maintainers"
    Please see the dedicated [plugin migration guide](../plugins/development/migration-v4.md) for a checklist of changes that may be needed to ensure compatibility with NetBox v4.0.

### Breaking Changes

* Support for Python 3.8 and 3.9 has been removed.
* The format for GraphQL query filters has changed. Please see the GraphQL documentation for details and examples.
* The deprecated `device_role` & `device_role_id` filters for devices have been removed. (Use `role` and `role_id` instead.)
* The obsolete `device_role` field has been removed from the REST API serializer for devices. (Use `role` instead.)
* The legacy reports functionality has been dropped. Reports will be automatically converted to custom scripts on upgrade.
* The `parent` and `parent_id` filters for locations now return only immediate children of the specified location. (Use `ancestor` and `ancestor_id` to return _all_ descendants.)
* The `object_type` field on the CustomField model has been renamed to `related_object_type`.
* The `utilities.utils` module has been removed and its resources reorganized into separate modules organized by function.
* The obsolete `NullableCharField` class has been removed. (Use Django's stock `CharField` class with `null=True` instead.)
* The `annotated_date` template filter and `annotated_now` template tag have been removed.

### New Features

#### Complete UI Refresh ([#12128](https://github.com/netbox-community/netbox/issues/12128))

The NetBox user interface has been completely refreshed and updated. This massive effort entailed:

* Refactoring the base HTML templates
* Moving from Boostrap 5.0 to Bootstrap 5.3
* Adopting the [Tabler](https://tabler.io/) UI theme
* Replacing slim-select with [Tom-Select](https://tom-select.js.org/)
* Displaying additional object attributes in dropdown form fields
* Enabling opt-in HTMX-powered navigation (see [#14736](https://github.com/netbox-community/netbox/issues/14736))
* Widespread cleanup & standardization of UI components

#### Dynamic REST API Fields ([#15087](https://github.com/netbox-community/netbox/issues/15087))

The REST API now supports specifying which fields to include in the response data. For example, the response to a request for

```
GET /api/dcim/sites/?fields=name,status,region,tenant
```

will include only the four specified fields in the representation of each site. Additionally, the underlying database queries effected by such requests have been optimized to omit fields which are not included in the response, resulting in a substantial performance improvement.

#### Strawberry GraphQL Engine ([#9856](https://github.com/netbox-community/netbox/issues/9856))

The GraphQL engine has been changed from using Graphene-Django to Strawberry-Django. Changes include:

* Queryset Optimizer - reduces the number of database queries when querying related tables
* Updated GraphiQL Browser
* The format for GraphQL query filters and lookups has changed. Please see the GraphQL documentation for details and examples.

#### Advanced Form Rendering Functionality ([#14739](https://github.com/netbox-community/netbox/issues/14739))

New resources have been introduced to enable advanced form rendering without a need for custom HTML templates. These include:

* FieldSet - Represents a grouping of form fields (replaces the use of lists/tuples)
* InlineFields - Multiple fields rendered on a single row
* TabbedGroups - Fieldsets rendered under navigable tabs within a form
* ObjectAttribute - Renders a read-only representation of a particular object attribute (for reference)

#### Legacy Admin UI Disabled ([#12325](https://github.com/netbox-community/netbox/issues/12325))

The legacy admin user interface is now disabled by default, and the few remaining views it provided have been relocated to the primary UI. NetBox deployments which still depend on the legacy admin functionality for plugins can enable it by setting the `DJANGO_ADMIN_ENABLED` configuration parameter to true.

### Enhancements

* [#12776](https://github.com/netbox-community/netbox/issues/12776) - Introduce the `htmx_table` template tag to simplify the rendering of embedded tables
* [#12851](https://github.com/netbox-community/netbox/issues/12851) - Replace the deprecated Bleach HTML sanitization library with nh3
* [#13283](https://github.com/netbox-community/netbox/issues/13283) - Display additional context on API-backed dropdown form fields (e.g. object descriptions)
* [#13918](https://github.com/netbox-community/netbox/issues/13918) - Add `facility` field to Location model
* [#14237](https://github.com/netbox-community/netbox/issues/14237) - Automatically clear dependent selection form fields when modifying a parent selection
* [#14279](https://github.com/netbox-community/netbox/issues/14279) - Make the current request available as context when running custom validators
* [#14454](https://github.com/netbox-community/netbox/issues/14454) - Include member devices in the REST API representation of virtual chassis
* [#14637](https://github.com/netbox-community/netbox/issues/14637) - Upgrade to Django 5.0
* [#14672](https://github.com/netbox-community/netbox/issues/14672) - Add support for Python 3.12
* [#14728](https://github.com/netbox-community/netbox/issues/14728) - The plugins list view has been moved from the legacy admin UI to the main NetBox UI
* [#14729](https://github.com/netbox-community/netbox/issues/14729) - All background task views have been moved from the legacy admin UI to the main NetBox UI
* [#14736](https://github.com/netbox-community/netbox/issues/14736) - Introduce a user preference to enable HTMX-powered navigation
* [#14438](https://github.com/netbox-community/netbox/issues/14438) - Track individual custom scripts as database objects
* [#15131](https://github.com/netbox-community/netbox/issues/15131) - Automatically annotate related object counts on REST API querysets
* [#15237](https://github.com/netbox-community/netbox/issues/15237) - Ensure consistent filtering ability for all model fields by testing for missing/incorrect filters
* [#15238](https://github.com/netbox-community/netbox/issues/15238) - Include the `description` field in "brief" REST API serializations
* [#15278](https://github.com/netbox-community/netbox/issues/15278) - BaseModelSerializer now takes a `nested` keyword argument allowing it to represent a related object
* [#15383](https://github.com/netbox-community/netbox/issues/15383) - Standardize filtering logic for the parents of recursively-nested models (parent & ancestor filters)
* [#15413](https://github.com/netbox-community/netbox/issues/15413) - The global search engine now supports caching of non-field object attributes
* [#15490](https://github.com/netbox-community/netbox/issues/15490) - Custom validators can now reference related object attributes via dotted paths
* [#15547](https://github.com/netbox-community/netbox/issues/15547) - Add comments field to CustomField model
* [#15712](https://github.com/netbox-community/netbox/issues/15712) - Enable image attachments for virtual machines
* [#15735](https://github.com/netbox-community/netbox/issues/15735) - Display all dates & times in ISO 8601 format consistently
* [#15754](https://github.com/netbox-community/netbox/issues/15754) - Remove `is_staff` restriction on admin menu items
* [#15764](https://github.com/netbox-community/netbox/issues/15764) - Increase maximum value of Device `vc_position` field
* [#15915](https://github.com/netbox-community/netbox/issues/15915) - Provide a comprehensive system status view with export functionality

### Bug Fixes (from Beta2)

* [#15630](https://github.com/netbox-community/netbox/issues/15630) - Ensure consistent toggling between light & dark UI modes
* [#15802](https://github.com/netbox-community/netbox/issues/15802) - Improve hyperlink color contrast in dark mode
* [#15809](https://github.com/netbox-community/netbox/issues/15809) - Fix GraphQL union support for nullable fields
* [#15815](https://github.com/netbox-community/netbox/issues/15815) - Convert dashboard widgets referencing old user/group models
* [#15826](https://github.com/netbox-community/netbox/issues/15826) - Update `EXEMPT_EXCLUDE_MODELS` to reference new user & group models
* [#15831](https://github.com/netbox-community/netbox/issues/15831) - Fix LDAP group mirroring
* [#15838](https://github.com/netbox-community/netbox/issues/15838) - Fix AttributeError exception when rendering custom date fields
* [#15852](https://github.com/netbox-community/netbox/issues/15852) - Update total results count when filtering object lists
* [#15853](https://github.com/netbox-community/netbox/issues/15853) - Correct background color for cable trace SVG images in dark mode
* [#15855](https://github.com/netbox-community/netbox/issues/15855) - Fix AttributeError exception when creating an event rule tied to a custom script
* [#15944](https://github.com/netbox-community/netbox/issues/15944) - Fix styling of paginator when displayed above an object list

### Other Changes

* [#10587](https://github.com/netbox-community/netbox/issues/10587) - Enable pagination and filtering for custom script logs
* [#12325](https://github.com/netbox-community/netbox/issues/12325) - The Django admin UI is now disabled by default (set `DJANGO_ADMIN_ENABLED` to True to enable it)
* [#12510](https://github.com/netbox-community/netbox/issues/12510) - Dropped support for legacy reports
* [#12795](https://github.com/netbox-community/netbox/issues/12795) - NetBox now uses custom User and Group models rather than the stock models provided by Django
* [#13647](https://github.com/netbox-community/netbox/issues/13647) - Squash all database migrations prior to v3.7
* [#14092](https://github.com/netbox-community/netbox/issues/14092) - Remove backward compatibility for importing plugin resources from `extras.plugins` (now `netbox.plugins`)
* [#14638](https://github.com/netbox-community/netbox/issues/14638) - Drop support for Python 3.8 and 3.9
* [#14657](https://github.com/netbox-community/netbox/issues/14657) - Remove backward compatibility for old permissions mapping under `ActionsMixin`
* [#14658](https://github.com/netbox-community/netbox/issues/14658) - Remove backward compatibility for importing `process_webhook()` from `extras.webhooks_worker` (now `extras.webhooks.send_webhook()`)
* [#14740](https://github.com/netbox-community/netbox/issues/14740) - Remove the obsolete `BootstrapMixin` form mixin class
* [#15042](https://github.com/netbox-community/netbox/issues/15042) - The logic for registering models & model features now executes under the `ready()` method of individual app configs, rather than relying on the `class_prepared` signal
* [#15099](https://github.com/netbox-community/netbox/issues/15099) - Remove obsolete `device_role` and `device_role_id` filters for devices
* [#15100](https://github.com/netbox-community/netbox/issues/15100) - Remove obsolete `NullableCharField` class
* [#15154](https://github.com/netbox-community/netbox/issues/15154) - The installation documentation been extended to include instructions and an example configuration file for uWSGI as an alternative to gunicorn
* [#15193](https://github.com/netbox-community/netbox/issues/15193) - Switch to compiled distribution of the `psycopg` library
* [#15277](https://github.com/netbox-community/netbox/issues/15277) - Replace references to ContentType without ObjectType proxy model & standardize field names
* [#15292](https://github.com/netbox-community/netbox/issues/15292) - Remove obsolete `device_role` attribute from Device model (this field was renamed to `role` in v3.6)
* [#15357](https://github.com/netbox-community/netbox/issues/15357) - The `object_type` field on the CustomField model has been renamed to `related_object_type` to avoid confusion with its `object_types` field
* [#15401](https://github.com/netbox-community/netbox/issues/15401) - PostgreSQL indexes and sequence tables for the relocated L2VPN models (see [#14311](https://github.com/netbox-community/netbox/issues/14311)) have been renamed 
* [#15462](https://github.com/netbox-community/netbox/issues/15462) - Relocate resources from the `utilities.utils` module
* [#15464](https://github.com/netbox-community/netbox/issues/15464) - The many-to-many relationships for ObjectPermission are now defined on the custom User and Group models
* [#15736](https://github.com/netbox-community/netbox/issues/15736) - Remove obsolete `annotated_date` template filter & `annotated_now` template tag
* [#15738](https://github.com/netbox-community/netbox/issues/15738) - Remove obsolete configuration parameters for date & time formatting
* [#15752](https://github.com/netbox-community/netbox/issues/15752) - Remove the obsolete `ENABLE_LOCALIZATION` configuration parameter
* [#15942](https://github.com/netbox-community/netbox/issues/15942) - Refactor `settings_and_registry()` context processor

### REST API Changes

* The `/api/extras/content-types/` endpoint has moved to `/api/extras/object-types/`
* The `/api/extras/reports/` endpoint has been removed
* The `description` field is now included by default when using "brief mode" for all relevant models
* dcim.Device
    * The obsolete read-only attribute `device_role` has been removed (replaced by `role` in v3.6)
* dcim.Location
    * Added the optional `location` field
* dcim.VirtualChassis
    * Added `members` field to list the member devices
* extras.CustomField
    * `content_types` has been renamed to `object_types`
    * `object_type` has been renamed to `related_object_type`
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
* users.Group
    * Added the `permissions` field
* users.User
    * Added the `permissions` field
