# NetBox v3.6

## v3.6.0 (FUTURE)

### Breaking Changes

* PostgreSQL 11 is no longer supported (due to adopting Django 4.2). NetBox v3.6 requires PostgreSQL 12 or later.
* The `napalm_driver` and `napalm_args` fields (which were deprecated in v3.5) have been removed from the platform model.

### New Features

#### Relocated Admin Views ([#12589](https://github.com/netbox-community/netbox/issues/12589), [#12590](https://github.com/netbox-community/netbox/issues/12590), [#12591](https://github.com/netbox-community/netbox/issues/12591), [#13044](https://github.com/netbox-community/netbox/issues/13044))

Management views for the following object types, previously available only under the backend admin interface, have been relocated to the primary user interface:

* Users
* Groups
* Object permissions
* API tokens
* Configuration revisions

The admin UI is scheduled for removal in NetBox v4.0.

#### Configurable Default Permissions ([#13038](https://github.com/netbox-community/netbox/issues/13038))

Administrators now have the option of configuring a set of default permissions to be applied to _all_ users, regardless of explicit permission or group assignment. This is accomplished by defining the `DEFAULT_PERMISSIONS` configuration parameter.

#### User Bookmarks ([#8248](https://github.com/netbox-community/netbox/issues/8248))

Users can now bookmark their most commonly-visited objects in NetBox. Bookmarks will display both on the dashboard (if configured) and on a user-specific bookmarks view.

#### Custom Field Choice Sets ([#12988](https://github.com/netbox-community/netbox/issues/12988))

Select and multi-select custom fields now employ discrete, reusable choice sets containing the valid options for each field. A choice set may be shared by multiple custom fields. Additionally, each choice within a set can now specify both a value and a human-friendly label (see [#13241](https://github.com/netbox-community/netbox/issues/13241)).

#### Pre-Defined Location Choices for Custom Fields ([#12194](https://github.com/netbox-community/netbox/issues/12194))

Users now have the option to employ one of several pre-defined choice sets when creating a custom field. These include:

* IATA airport codes
* ISO 3166 country codes
* UN/LOCODE identifiers

Extra choices may also be appended to the pre-defined sets as needed.

#### Restrict Tag Usage by Object Type ([#11541](https://github.com/netbox-community/netbox/issues/11541))

Tags may now be restricted to use with designated object types. Tags that have no specific object types assigned may be used with any object that supports tag assignment.

### Enhancements

* [#6347](https://github.com/netbox-community/netbox/issues/6347) - Cache the number of assigned components for devices and virtual machines
* [#8137](https://github.com/netbox-community/netbox/issues/8137) - Add a field for designating the out-of-band (OOB) IP address for devices
* [#10197](https://github.com/netbox-community/netbox/issues/10197) - Cache the number of member devices on each virtual chassis
* [#11305](https://github.com/netbox-community/netbox/issues/11305) - Add GPS coordinate fields to the device model
* [#12175](https://github.com/netbox-community/netbox/issues/12175) - Permit racks to start numbering at values greater than one
* [#12210](https://github.com/netbox-community/netbox/issues/12210) - Add tenancy assignment for power feeds
* [#13170](https://github.com/netbox-community/netbox/issues/13170) - Add `rf_role` to InterfaceTemplate
* [#13269](https://github.com/netbox-community/netbox/issues/13269) - Cache the number of assigned component templates for device types

### Other Changes

* Work has begun on introducing translation and localization support in NetBox. This work is being performed in preparation for release 4.0.
* [#9077](https://github.com/netbox-community/netbox/issues/9077) - Prevent the errant execution of dangerous instance methods in Django templates
* [#11766](https://github.com/netbox-community/netbox/issues/11766) - Remove obsolete custom `ChoiceField` and `MultipleChoiceField` classes
* [#12180](https://github.com/netbox-community/netbox/issues/12180) - All API endpoints for available objects (e.g. IP addresses) now inherit from a common parent view
* [#12237](https://github.com/netbox-community/netbox/issues/12237) - Upgrade Django to v4.2
* [#12794](https://github.com/netbox-community/netbox/issues/12794) - Avoid direct imports of Django's stock user model
* [#12320](https://github.com/netbox-community/netbox/issues/12320) - Remove obsolete fields `napalm_driver` and `napalm_args` from Platform
* [#12964](https://github.com/netbox-community/netbox/issues/12964) - Drop support for PostgreSQL 11
