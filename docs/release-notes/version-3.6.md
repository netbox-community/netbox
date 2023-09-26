# NetBox v3.6

## v3.6.3 (FUTURE)

### Enhancements

* [#12732](https://github.com/netbox-community/netbox/issues/12732) - Add toggle to hide disconnected interfaces under device view

### Bug Fixes

* [#13506](https://github.com/netbox-community/netbox/issues/13506) - Enable creating a config template which references a data file via the REST API
* [#13666](https://github.com/netbox-community/netbox/issues/13666) - Cleanly handle reports without any test methods defined
* [#13839](https://github.com/netbox-community/netbox/issues/13839) - Restore original text color for HTML code elements
* [#13845](https://github.com/netbox-community/netbox/issues/13845) - Fix `AttributeError` exception when attaching front/rear images to a device type
* [#13871](https://github.com/netbox-community/netbox/issues/13871) - Fix rack filtering for empty location during device bulk import
* [#13891](https://github.com/netbox-community/netbox/issues/13891) - Allow designating an IP address as primary for device/VM while assigning it to an interface

---

## v3.6.2 (2023-09-20)

### Enhancements

* [#13245](https://github.com/netbox-community/netbox/issues/13245) - Add interface types for QSFP112 and OSFP-RHS
* [#13563](https://github.com/netbox-community/netbox/issues/13563) - Add support for other delimiting characters when using CSV import

### Bug Fixes

* [#11209](https://github.com/netbox-community/netbox/issues/11209) - Hide available IP/VLAN listing when sorting under a parent prefix or VLAN range
* [#11617](https://github.com/netbox-community/netbox/issues/11617) - Raise validation error on the presence of an unknown CSV header during bulk import
* [#12219](https://github.com/netbox-community/netbox/issues/12219) - Fix dashboard widget heading contrast under dark mode
* [#12685](https://github.com/netbox-community/netbox/issues/12685) - Render Markdown in custom field help text on object edit forms
* [#13653](https://github.com/netbox-community/netbox/issues/13653) - Tweak color of error text to improve legibility
* [#13701](https://github.com/netbox-community/netbox/issues/13701) - Correct display of power feed legs under device view
* [#13706](https://github.com/netbox-community/netbox/issues/13706) - Restore extra filters dropdown on device interfaces list
* [#13721](https://github.com/netbox-community/netbox/issues/13721) - Filter VLAN choices by selected site (if any) when creating a prefix
* [#13727](https://github.com/netbox-community/netbox/issues/13727) - Fix exception when viewing rendered config for VM without a role assigned
* [#13745](https://github.com/netbox-community/netbox/issues/13745) - Optimize counter field migrations for large databases
* [#13756](https://github.com/netbox-community/netbox/issues/13756) - Fix exception when sorting module bay list by installed module status
* [#13757](https://github.com/netbox-community/netbox/issues/13757) - Fix RecursionError exception when assigning config context to a device type
* [#13767](https://github.com/netbox-community/netbox/issues/13767) - Fix support for comments when creating a new service via web UI
* [#13782](https://github.com/netbox-community/netbox/issues/13782) - Fix tag exclusion support for contact assignments
* [#13791](https://github.com/netbox-community/netbox/issues/13791) - Preserve whitespace in values when performing bulk rename of objects via web UI
* [#13809](https://github.com/netbox-community/netbox/issues/13809) - Avoid TypeError exception when editing active configuration with statically defined `CUSTOM_VALIDATORS`
* [#13813](https://github.com/netbox-community/netbox/issues/13813) - Fix member count for newly created virtual chassis
* [#13818](https://github.com/netbox-community/netbox/issues/13818) - Restore missing tags field on L2VPN termination edit form

---

## v3.6.1 (2023-09-06)

### Enhancements

* [#12870](https://github.com/netbox-community/netbox/issues/12870) - Support setting token expiration time using the provisioning API endpoint
* [#13444](https://github.com/netbox-community/netbox/issues/13444) - Add bulk rename functionality to the global device component lists
* [#13638](https://github.com/netbox-community/netbox/issues/13638) - Add optional `staff_only` attribute to MenuItem

### Bug Fixes

* [#12553](https://github.com/netbox-community/netbox/issues/12552) - Ensure `family` attribute is always returned when creating aggregates and prefixes via REST API
* [#13619](https://github.com/netbox-community/netbox/issues/13619) - Fix exception when viewing IP address assigned to a virtual machine
* [#13596](https://github.com/netbox-community/netbox/issues/13596) - Always display "render config" tab for devices and virtual machines
* [#13620](https://github.com/netbox-community/netbox/issues/13620) - Show admin menu items only for staff users
* [#13622](https://github.com/netbox-community/netbox/issues/13622) - Fix exception when viewing current config and no revisions have been created
* [#13626](https://github.com/netbox-community/netbox/issues/13626) - Correct filtering of recent activity list under user view
* [#13628](https://github.com/netbox-community/netbox/issues/13628) - Remove stale references to obsolete NAPALM integration
* [#13630](https://github.com/netbox-community/netbox/issues/13630) - Fix display of active status under user view
* [#13632](https://github.com/netbox-community/netbox/issues/13632) - Avoid raising exception when checking if FHRP group IP address is primary
* [#13642](https://github.com/netbox-community/netbox/issues/13642) - Suppress warning about unreflected model changes when applying migrations
* [#13657](https://github.com/netbox-community/netbox/issues/13657) - Fix decoding of data file content
* [#13674](https://github.com/netbox-community/netbox/issues/13674) - Fix retrieving individual report via REST API
* [#13682](https://github.com/netbox-community/netbox/issues/13682) - Fix error message returned when validation of custom field default value fails
* [#13684](https://github.com/netbox-community/netbox/issues/13684) - Enable modifying the configuration when maintenance mode is enabled

---

## v3.6.0 (2023-08-30)

### Breaking Changes

* PostgreSQL 11 is no longer supported (dropped in Django 4.2). NetBox v3.6 requires PostgreSQL 12 or later.
* The `boto3` and `dulwich` packages are no longer installed automatically. If needed for S3/git remote data backend support, add them to `local_requirements.txt` to ensure their installation.
* The `device_role` field on the Device model has been renamed to `role`. The `device_role` field has been temporarily retained on the REST API serializer for devices for backward compatibility, but is read-only.
* The `choices` array field has been removed from the CustomField model. Any defined choices are automatically migrated to CustomFieldChoiceSets, accessible via the new `choice_set` field on the CustomField model.
* The `napalm_driver` and `napalm_args` fields (which were deprecated in v3.5) have been removed from the Platform model.
* The `device` and `device_id` filter for interfaces will no longer include interfaces from virtual chassis peers. Two new filters, `virtual_chassis_member` and `virtual_chassis_member_id`, have been introduced to match all interfaces belonging to the specified device's virtual chassis (if any).
* Reports and scripts are now returned within a `results` list when fetched via the REST API, consistent with other models.
* Superusers can no longer retrieve API token keys via the web UI if [`ALLOW_TOKEN_RETRIEVAL`](https://docs.netbox.dev/en/stable/configuration/security/#allow_token_retrieval) is disabled. (The admin view has been removed per [#13044](https://github.com/netbox-community/netbox/issues/13044).)

### New Features

#### Relocated Admin UI Views ([#12589](https://github.com/netbox-community/netbox/issues/12589), [#12590](https://github.com/netbox-community/netbox/issues/12590), [#12591](https://github.com/netbox-community/netbox/issues/12591), [#13044](https://github.com/netbox-community/netbox/issues/13044))

Management views for the following object types, previously available only under the backend admin interface, have been relocated to the primary user interface:

* Users
* Groups
* Object permissions
* API tokens
* Configuration revisions

This migration provides a more consistent user experience and unlocks advanced functionality not feasible using Django's built-in views. The admin UI is scheduled for complete removal in NetBox v4.0.

#### Configurable Default Permissions ([#13038](https://github.com/netbox-community/netbox/issues/13038))

Administrators now have the option of configuring default permissions for _all_ users globally, regardless of explicit permission or group assignments granted in the database. This is accomplished by defining the `DEFAULT_PERMISSIONS` configuration parameter. By default, all users are granted permission to manage their own bookmarks and API tokens.

#### User Bookmarks ([#8248](https://github.com/netbox-community/netbox/issues/8248))

Users can now bookmark their favorite objects in NetBox. Bookmarks are accessible under each user's personal bookmarks list, and can also be added as a dashboard widget.

#### Custom Field Choice Sets ([#12988](https://github.com/netbox-community/netbox/issues/12988))

Selection and multi-select custom fields now employ discrete, reusable choice sets containing the valid options for each field. A choice set may be shared by multiple custom fields. Additionally, each choice within a set can now specify both a raw value and a human-friendly label (see [#13241](https://github.com/netbox-community/netbox/issues/13241)). Pre-existing custom field choices are migrated to choice sets automatically during the upgrade process.

#### Pre-Defined Location Choices for Custom Fields ([#12194](https://github.com/netbox-community/netbox/issues/12194))

Users now have the option to employ one of several pre-defined sets of choices when creating a custom field. These include:

* IATA airport codes
* ISO 3166 country codes
* UN/LOCODE location identifiers

When defining a choice set, one of the above can be employed as the base set, with the option to define extra, custom choices as well.

#### Restrict Tag Usage by Object Type ([#11541](https://github.com/netbox-community/netbox/issues/11541))

Tags may now be restricted to use with designated object types. Tags that have no specific object types assigned may be used with any object that supports tag assignment.

### Enhancements

* [#6347](https://github.com/netbox-community/netbox/issues/6347) - Cache the number of assigned components for devices and virtual machines
* [#8137](https://github.com/netbox-community/netbox/issues/8137) - Add a field for designating the out-of-band (OOB) IP address for devices
* [#10197](https://github.com/netbox-community/netbox/issues/10197) - Cache the number of member devices on each virtual chassis
* [#11305](https://github.com/netbox-community/netbox/issues/11305) - Add GPS coordinate fields to the device model
* [#11478](https://github.com/netbox-community/netbox/issues/11478) - Introduce `virtual_chassis_member` filter for interfaces & restore default behavior for `device` filter
* [#11519](https://github.com/netbox-community/netbox/issues/11519) - Add a SQL index for IP address host values to optimize queries
* [#11732](https://github.com/netbox-community/netbox/issues/11732) - Prevent inadvertent overwriting of object attributes by competing users
* [#11936](https://github.com/netbox-community/netbox/issues/11936) - Introduce support for tags and custom fields on webhooks
* [#12175](https://github.com/netbox-community/netbox/issues/12175) - Permit racks to start numbering at values greater than one
* [#12210](https://github.com/netbox-community/netbox/issues/12210) - Add tenancy assignment for power feeds
* [#12461](https://github.com/netbox-community/netbox/issues/12461) - Add config template rendering for virtual machines
* [#12814](https://github.com/netbox-community/netbox/issues/12814) - Expose NetBox models within ConfigTemplate rendering context
* [#12882](https://github.com/netbox-community/netbox/issues/12882) - Add tag support for contact assignments
* [#13037](https://github.com/netbox-community/netbox/issues/13037) - Return reports & scripts within a `results` list when fetched via the REST API
* [#13170](https://github.com/netbox-community/netbox/issues/13170) - Add `rf_role` to InterfaceTemplate
* [#13269](https://github.com/netbox-community/netbox/issues/13269) - Cache the number of assigned component templates for device types

### Bug Fixes

* [#13513](https://github.com/netbox-community/netbox/issues/13513) - Prevent exception when rendering bookmarks widget for anonymous user
* [#13599](https://github.com/netbox-community/netbox/issues/13599) - Fix errant counter increments when editing device/VM components
* [#13605](https://github.com/netbox-community/netbox/issues/13605) - Optimize cached counter migrations to avoid excessive memory consumption

### Other Changes

* Work has begun on introducing translation and localization support in NetBox. This work is being performed in preparation for release 4.0.
* [#6391](https://github.com/netbox-community/netbox/issues/6391) - Rename the `device_role` field on Device to `role` for consistency with VirtualMachine
* [#9077](https://github.com/netbox-community/netbox/issues/9077) - Prevent the errant execution of dangerous instance methods in Django templates
* [#11766](https://github.com/netbox-community/netbox/issues/11766) - Remove obsolete custom `ChoiceField` and `MultipleChoiceField` classes
* [#12180](https://github.com/netbox-community/netbox/issues/12180) - All API endpoints for available objects (e.g. IP addresses) now inherit from a common parent view
* [#12237](https://github.com/netbox-community/netbox/issues/12237) - Upgrade Django to v4.2
* [#12320](https://github.com/netbox-community/netbox/issues/12320) - Remove obsolete fields `napalm_driver` and `napalm_args` from Platform
* [#12794](https://github.com/netbox-community/netbox/issues/12794) - Avoid direct imports of Django's stock user model
* [#12906](https://github.com/netbox-community/netbox/issues/12906) - The `boto3` (AWS) and `dulwich` (git) packages for remote data sources are now optional requirements
* [#12964](https://github.com/netbox-community/netbox/issues/12964) - Drop support for PostgreSQL 11
* [#13309](https://github.com/netbox-community/netbox/issues/13309) - User account-specific resources have been moved to a new `account` app for better organization

### REST API Changes

* Introduced the following endpoints:
    * `/api/extras/bookmarks/`
    * `/api/extras/custom-field-choice-sets/`
* Added the `/api/extras/custom-fields/{id}/choices/` endpoint for select and multi-select custom fields
* dcim.Device
    * Renamed `device_role` to `device`. Added a read-only `device_role` field for limited backward compatibility.
    * Added the `latitude` and `longitude` fields (for GPS coordinates)
    * Added the `oob_ip` field for out-of-band IP address assignment
* dcim.DeviceType
    * Added read-only counter fields for assigned component templates:
        * `console_port_template_count`
        * `console_server_port_template_count`
        * `power_port_template_count`
        * `power_outlet_template_count`
        * `interface_template_count`
        * `front_port_template_count`
        * `rear_port_template_count`
        * `device_bay_template_count`
        * `module_bay_template_count`
        * `inventory_item_template_count`
* dcim.InterfaceTemplate
    * Added the `rf_role` field
* dcim.Platform
    * Removed the `napalm_driver` and `napalm_args` fields
* dcim.PowerFeed
    * Added the `tenant` field
* dcim.Rack
    * Added the `starting_unit` field
* dcim.VirtualChassis
    * Added the read-only `member_count` field
* extras.CustomField
    * Removed the `choices` array field
    * Added the `choice_set` foreign key field (to ChoiceSet)
* extras.Report
    * Reports are now returned within a `results` list
* extras.Script
    * Scripts are now returned within a `results` list
* extras.Tag
    * Added the `object_types` field for optional restriction to specific object types
* extras.Webhook
    * Added `custom_fields` and `tags` support
* tenancy.ContactAssignment
    * Added `tags` support
* virtualization.VirtualMachine
    * Added the `oob_ip` field for out-of-band IP address assignment
