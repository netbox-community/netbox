# NetBox v3.1

## v3.1.11 (2022-04-05)

### Enhancements

* [#8163](https://github.com/netbox-community/netbox/issues/8163) - Show bridge interface members under interface view
* [#8365](https://github.com/netbox-community/netbox/issues/8365) - Enable filtering child devices by parent device ID
* [#8785](https://github.com/netbox-community/netbox/issues/8785) - Permit wildcard values in IP address DNS names
* [#8790](https://github.com/netbox-community/netbox/issues/8790) - Include site and prefixes columns in VLAN group VLANs table
* [#8830](https://github.com/netbox-community/netbox/issues/8830) - Add Checkpoint ClusterXL protocol for FHRP groups
* [#8974](https://github.com/netbox-community/netbox/issues/8974) - Use monospace font for text areas in config revision form
* [#9012](https://github.com/netbox-community/netbox/issues/9012) - Linkify circuits count in providers list
* [#9036](https://github.com/netbox-community/netbox/issues/9036) - Add bulk edit capability for site contact fields

### Bug Fixes

* [#8866](https://github.com/netbox-community/netbox/issues/8866) - Prevent exception when searching for a rack position with no rack specified under device edit view
* [#9009](https://github.com/netbox-community/netbox/issues/9009) - Fix device count for racks in global search results

---

## v3.1.10 (2022-03-25)

### Enhancements

* [#8232](https://github.com/netbox-community/netbox/issues/8232) - Use a different color for 100% utilization bars
* [#8457](https://github.com/netbox-community/netbox/issues/8457) - Enable adding non-racked devices from site & location views
* [#8553](https://github.com/netbox-community/netbox/issues/8553) - Add missing object types to global search form
* [#8575](https://github.com/netbox-community/netbox/issues/8575) - Add rack columns to cables list
* [#8645](https://github.com/netbox-community/netbox/issues/8645) - Enable filtering objects by assigned contacts & contact roles
* [#8926](https://github.com/netbox-community/netbox/issues/8926) - Add device type, role columns to device bay table

### Bug Fixes

* [#8696](https://github.com/netbox-community/netbox/issues/8696) - Fix help link under FHRP group assigment creation view
* [#8813](https://github.com/netbox-community/netbox/issues/8813) - Retain global search bar query after submitting
* [#8820](https://github.com/netbox-community/netbox/issues/8820) - Fix navbar background color in dark mode
* [#8850](https://github.com/netbox-community/netbox/issues/8850) - Show airflow field on device REST API serializer when config context data is included
* [#8905](https://github.com/netbox-community/netbox/issues/8905) - Disable ordering by assigned tags to prevent erroneous results
* [#8919](https://github.com/netbox-community/netbox/issues/8919) - Fix filtering of VLAN groups by site under prefix edit form
* [#8924](https://github.com/netbox-community/netbox/issues/8924) - Improve load time of custom script list
* [#8932](https://github.com/netbox-community/netbox/issues/8932) - Fix error when setting null value for interface `rf_role` via REST API
* [#8935](https://github.com/netbox-community/netbox/issues/8935) - Correct ordering of next/previous racks to use naturalized names
* [#8947](https://github.com/netbox-community/netbox/issues/8947) - Retain filter parameters when handling an export template exception
* [#8951](https://github.com/netbox-community/netbox/issues/8951) - Allow changing device type & platform to different manufacturer simultaneously
* [#8952](https://github.com/netbox-community/netbox/issues/8952) - Device images in rear rack elevations should be hyperlinked

---

## v3.1.9 (2022-03-07)

### Enhancements

* [#8594](https://github.com/netbox-community/netbox/issues/8594) - Enable filtering by exact description match for all applicable models
* [#8629](https://github.com/netbox-community/netbox/issues/8629) - Add description to tag table search function
* [#8664](https://github.com/netbox-community/netbox/issues/8664) - Show assigned ASNs/sites under list views
* [#8736](https://github.com/netbox-community/netbox/issues/8736) - Add PC and UPC fiber end faces for LC/SC/LSH port types
* [#8758](https://github.com/netbox-community/netbox/issues/8758) - Allow empty string substitution when renaming objects in bulk
* [#8762](https://github.com/netbox-community/netbox/issues/8762) - Link to rack elevations list from site view
* [#8766](https://github.com/netbox-community/netbox/issues/8766) - Add SCTP to service protocols list

### Bug Fixes

* [#8546](https://github.com/netbox-community/netbox/issues/8546) - Fix bulk import to restrict bridge, parent, and LAG to device interfaces
* [#8633](https://github.com/netbox-community/netbox/issues/8633) - Prevent navigation sidebar pin from disappearing at certain breakpoints
* [#8674](https://github.com/netbox-community/netbox/issues/8674) - Fix rendering of tabbed content in documentation
* [#8710](https://github.com/netbox-community/netbox/issues/8710) - Fix dynamic scope selection form fields when creating a VLAN group
* [#8713](https://github.com/netbox-community/netbox/issues/8713) - Restore missing "add" button on services list view
* [#8715](https://github.com/netbox-community/netbox/issues/8715) - Avoid returning multiple objects when restricting querysets using multiple tags in permissions
* [#8717](https://github.com/netbox-community/netbox/issues/8717) - Fix redirection after bulk edit/delete of prefixes from aggregate view
* [#8724](https://github.com/netbox-community/netbox/issues/8724) - Fix exception during device import with invalid device type
* [#8807](https://github.com/netbox-community/netbox/issues/8807) - Correct REST API URL for FHRP group assignments
* [#8808](https://github.com/netbox-community/netbox/issues/8808) - Fix members count under FHRP group list

---

## v3.1.8 (2022-02-15)

### Enhancements

* [#7150](https://github.com/netbox-community/netbox/issues/7150) - Linkify devices on the far side of a rack elevation
* [#8398](https://github.com/netbox-community/netbox/issues/8398) - Embiggen configuration form fields for banner message content
* [#8556](https://github.com/netbox-community/netbox/issues/8556) - Add full username column to changelog table
* [#8620](https://github.com/netbox-community/netbox/issues/8620) - Enable tab completion for `nbshell`

### Bug Fixes

* [#8331](https://github.com/netbox-community/netbox/issues/8331) - Implement `replaceAll` string utility function to improve browser compatibility
* [#8391](https://github.com/netbox-community/netbox/issues/8391) - Null date columns should return empty strings during CSV export
* [#8548](https://github.com/netbox-community/netbox/issues/8548) - Fix display of VC members when position is zero
* [#8561](https://github.com/netbox-community/netbox/issues/8561) - Include option to connect a rear port to a console port
* [#8564](https://github.com/netbox-community/netbox/issues/8564) - Fix errant table configuration key `available_columns`
* [#8577](https://github.com/netbox-community/netbox/issues/8577) - Show contact assignment counts in global search results
* [#8578](https://github.com/netbox-community/netbox/issues/8578) - Object change log tables should honor user's configured preferences
* [#8604](https://github.com/netbox-community/netbox/issues/8604) - Fix tag filter on config context list filter form
* [#8609](https://github.com/netbox-community/netbox/issues/8609) - Display validation error when attempting to assign VLANs to interface with no mode during bulk edit
* [#8611](https://github.com/netbox-community/netbox/issues/8611) - Fix bulk editing for certain custom link, webhook, and journal entry fields

---

## v3.1.7 (2022-02-03)

### Enhancements

* [#7504](https://github.com/netbox-community/netbox/issues/7504) - Include IP range data under IPAM role views
* [#8275](https://github.com/netbox-community/netbox/issues/8275) - Introduce alternative ASDOT-formatted column for ASNs
* [#8367](https://github.com/netbox-community/netbox/issues/8367) - Add ASNs to global search function
* [#8368](https://github.com/netbox-community/netbox/issues/8368) - Enable controlling the order of custom script form fields with `field_order`
* [#8381](https://github.com/netbox-community/netbox/issues/8381) - Add contacts to global search function
* [#8462](https://github.com/netbox-community/netbox/issues/8462) - Linkify manufacturer column in device type table
* [#8476](https://github.com/netbox-community/netbox/issues/8476) - Bring the ASN Web UI up to the standard set by other objects
* [#8494](https://github.com/netbox-community/netbox/issues/8494) - Include locations count under tenant view
* [#8517](https://github.com/netbox-community/netbox/issues/8517) - Render boolean custom fields as icons in object tables
* [#8530](https://github.com/netbox-community/netbox/issues/8530) - Indicate CSV or YAML as format for "all data" export

### Bug Fixes

* [#8315](https://github.com/netbox-community/netbox/issues/8315) - Fix display of NAT link for primary IPv4 address under device view
* [#8377](https://github.com/netbox-community/netbox/issues/8377) - Fix calculation of absolute cable lengths when specified in fractional units
* [#8425](https://github.com/netbox-community/netbox/issues/8425) - Fix exception when viewing change list/records with removed plugins
* [#8456](https://github.com/netbox-community/netbox/issues/8456) - Fix redundant display of VRF RD in prefix view
* [#8465](https://github.com/netbox-community/netbox/issues/8465) - Accept empty string values for Interface `rf_channel` in REST API
* [#8498](https://github.com/netbox-community/netbox/issues/8498) - Fix display of selected content type filters in object list views
* [#8499](https://github.com/netbox-community/netbox/issues/8499) - Content types REST API endpoint should not require model permission
* [#8512](https://github.com/netbox-community/netbox/issues/8512) - Correct file permissions to allow execution of housekeeping script
* [#8527](https://github.com/netbox-community/netbox/issues/8527) - Fix display of changelog retention period

---

## v3.1.6 (2022-01-17)

### Enhancements

* [#8246](https://github.com/netbox-community/netbox/issues/8246) - Show human-friendly values for commit rates in circuits table
* [#8262](https://github.com/netbox-community/netbox/issues/8262) - Add cable count to tenant stats
* [#8265](https://github.com/netbox-community/netbox/issues/8265) - Add Stackwise-n interface types
* [#8293](https://github.com/netbox-community/netbox/issues/8293) - Show 4-byte ASNs in ASDOT notation
* [#8302](https://github.com/netbox-community/netbox/issues/8302) - Linkify role column in device & VM tables
* [#8337](https://github.com/netbox-community/netbox/issues/8337) - Enable sorting object tables by created & updated times

### Bug Fixes

* [#8279](https://github.com/netbox-community/netbox/issues/8279) - Fix display of virtual chassis members in rack elevations
* [#8285](https://github.com/netbox-community/netbox/issues/8285) - Fix `cluster_count` under tenant REST API serializer
* [#8287](https://github.com/netbox-community/netbox/issues/8287) - Correct label in export template form
* [#8301](https://github.com/netbox-community/netbox/issues/8301) - Fix delete button for various object children views
* [#8305](https://github.com/netbox-community/netbox/issues/8305) - Fix assignment of custom field data to FHRP groups via UI
* [#8306](https://github.com/netbox-community/netbox/issues/8306) - Redirect user to previous page after login
* [#8314](https://github.com/netbox-community/netbox/issues/8314) - Prevent custom fields with default values from appearing as applied filters erroneously
* [#8317](https://github.com/netbox-community/netbox/issues/8317) - Fix CSV import of multi-select custom field values
* [#8319](https://github.com/netbox-community/netbox/issues/8319) - Custom URL fields should honor `ALLOWED_URL_SCHEMES` config parameter
* [#8342](https://github.com/netbox-community/netbox/issues/8342) - Restore `created` & `last_updated` fields missing from several REST API serializers
* [#8357](https://github.com/netbox-community/netbox/issues/8357) - Add missing tags field to location filter form
* [#8358](https://github.com/netbox-community/netbox/issues/8358) - Fix inconsistent styling of custom fields on filter & bulk edit forms

---

## v3.1.5 (2022-01-06)

### Enhancements

* [#8231](https://github.com/netbox-community/netbox/issues/8231) - Use in-page dialogs for confirming object deletion
* [#8244](https://github.com/netbox-community/netbox/issues/8244) - Add length & length unit fields to cable filter form
* [#8252](https://github.com/netbox-community/netbox/issues/8252) - Linkify type and group columns in clusters table

### Bug Fixes

* [#8213](https://github.com/netbox-community/netbox/issues/8213) - Fix ValueError exception under prefix IP addresses view
* [#8224](https://github.com/netbox-community/netbox/issues/8224) - Fix KeyError exception when creating FHRP group with IP address and protocol "other"
* [#8226](https://github.com/netbox-community/netbox/issues/8226) - Honor return URL after populating a device bay
* [#8228](https://github.com/netbox-community/netbox/issues/8228) - Optional ChoiceVar fields should not force a selection
* [#8255](https://github.com/netbox-community/netbox/issues/8255) - Fix bulk editing of authentication parameters for wireless LANs and links

---

## v3.1.4 (2022-01-03)

### Enhancements

* [#8192](https://github.com/netbox-community/netbox/issues/8192) - Add "add prefix" button to aggregate child prefixes view
* [#8194](https://github.com/netbox-community/netbox/issues/8194) - Enable bulk user assignment to groups under admin UI
* [#8197](https://github.com/netbox-community/netbox/issues/8197) - Allow filtering sites by group when connecting a cable
* [#8210](https://github.com/netbox-community/netbox/issues/8210) - Establish `netbox/local/` as a path for local resources

### Bug Fixes

* [#8187](https://github.com/netbox-community/netbox/issues/8187) - Fix rendering of tags column in object tables
* [#8191](https://github.com/netbox-community/netbox/issues/8191) - Fix return URL when adding IP addresses to VM interfaces
* [#8196](https://github.com/netbox-community/netbox/issues/8196) - Fix IndexError exception when viewing large IPv6 prefixes in UI
* [#8201](https://github.com/netbox-community/netbox/issues/8201) - Custom integer fields should allow negative integers as minimum/maximum values

---

## v3.1.3 (2021-12-29)

### Enhancements

* [#6782](https://github.com/netbox-community/netbox/issues/6782) - Enable the inclusion of custom links in tables
* [#7600](https://github.com/netbox-community/netbox/issues/7600) - Include count of available IPs on prefix view
* [#8034](https://github.com/netbox-community/netbox/issues/8034) - Enable specifying custom field validators during CSV import
* [#8100](https://github.com/netbox-community/netbox/issues/8100) - Add "other" choice for FHRP group protocol
* [#8175](https://github.com/netbox-community/netbox/issues/8175) - Display parent object when attaching an image

### Bug Fixes

* [#7246](https://github.com/netbox-community/netbox/issues/7246) - Don't attempt to URL-decode NAPALM response payloads
* [#7290](https://github.com/netbox-community/netbox/issues/7290) - Defer loading API-backed form fields
* [#7887](https://github.com/netbox-community/netbox/issues/7887) - Forward `HTTP_X_FORWARDED_FOR` to custom scripts
* [#7962](https://github.com/netbox-community/netbox/issues/7962) - Fix user menu under report/script result view
* [#7972](https://github.com/netbox-community/netbox/issues/7972) - Standardize name of `RemoteUserBackend` logger
* [#8097](https://github.com/netbox-community/netbox/issues/8097) - Fix styling of Markdown tables
* [#8127](https://github.com/netbox-community/netbox/issues/8127) - Fix disassociation of interface under IP address edit view
* [#8131](https://github.com/netbox-community/netbox/issues/8131) - Restore annotation of available IPs under prefix IPs view
* [#8134](https://github.com/netbox-community/netbox/issues/8134) - Fix bulk editing of objects within dynamic tables
* [#8139](https://github.com/netbox-community/netbox/issues/8139) - Fix rendering of table configuration form under VM interfaces view
* [#8140](https://github.com/netbox-community/netbox/issues/8140) - Restore missing fields on wireless LAN & link REST API serializers

---

## v3.1.2 (2021-12-20)

### Enhancements

* [#7661](https://github.com/netbox-community/netbox/issues/7661) - Remove forced styling of custom banners
* [#7665](https://github.com/netbox-community/netbox/issues/7665) - Add toggle to show only available child prefixes
* [#7999](https://github.com/netbox-community/netbox/issues/7999) - Add 6 GHz and 60 GHz wireless channels
* [#8057](https://github.com/netbox-community/netbox/issues/8057) - Dynamic object tables using HTMX
* [#8080](https://github.com/netbox-community/netbox/issues/8080) - Link to NAT IPs for device/VM primary IPs
* [#8081](https://github.com/netbox-community/netbox/issues/8081) - Allow creating services directly from navigation menu
* [#8083](https://github.com/netbox-community/netbox/issues/8083) - Removed "related devices" panel from device view
* [#8108](https://github.com/netbox-community/netbox/issues/8108) - Improve breadcrumb links for device/VM components

### Bug Fixes

* [#7674](https://github.com/netbox-community/netbox/issues/7674) - Fix inadvertent application of device type context to virtual machines
* [#8074](https://github.com/netbox-community/netbox/issues/8074) - Ordering VMs by name should reference naturalized value
* [#8077](https://github.com/netbox-community/netbox/issues/8077) - Fix exception when attaching image to location, circuit, or power panel
* [#8078](https://github.com/netbox-community/netbox/issues/8078) - Add missing wireless models to `lsmodels()` in `nbshell`
* [#8079](https://github.com/netbox-community/netbox/issues/8079) - Fix validation of LLDP neighbors when connected device has an asset tag
* [#8088](https://github.com/netbox-community/netbox/issues/8088) - Improve legibility of text in labels with light-colored backgrounds
* [#8092](https://github.com/netbox-community/netbox/issues/8092) - Rack elevations should not include device asset tags
* [#8096](https://github.com/netbox-community/netbox/issues/8096) - Fix DataError during change logging of objects with very long string representations
* [#8101](https://github.com/netbox-community/netbox/issues/8101) - Preserve return URL when using "create and add another" button
* [#8102](https://github.com/netbox-community/netbox/issues/8102) - Raise validation error when attempting to assign an IP address to multiple objects

---

## v3.1.1 (2021-12-13)

### Enhancements

* [#8047](https://github.com/netbox-community/netbox/issues/8047) - Display sorting indicator in table column headers

### Bug Fixes

* [#5869](https://github.com/netbox-community/netbox/issues/5869) - Fix permissions evaluation under available prefix/IP REST API endpoints
* [#7519](https://github.com/netbox-community/netbox/issues/7519) - Return a 409 status for unfulfillable available prefix/IP requests
* [#7690](https://github.com/netbox-community/netbox/issues/7690) - Fix custom field integer support for MultiValueNumberFilter
* [#7990](https://github.com/netbox-community/netbox/issues/7990) - Fix `title` display on contact detail view
* [#7996](https://github.com/netbox-community/netbox/issues/7996) - Show WWN field in interface creation form
* [#8001](https://github.com/netbox-community/netbox/issues/8001) - Correct verbose name for wireless LAN group model
* [#8003](https://github.com/netbox-community/netbox/issues/8003) - Fix cable tracing across bridged interfaces with no cable
* [#8005](https://github.com/netbox-community/netbox/issues/8005) - Fix contact email display
* [#8009](https://github.com/netbox-community/netbox/issues/8009) - Validate IP addresses for uniqueness when creating an FHRP group
* [#8010](https://github.com/netbox-community/netbox/issues/8010) - Allow filtering devices by multiple serial numbers
* [#8019](https://github.com/netbox-community/netbox/issues/8019) - Exclude metrics endpoint when `LOGIN_REQUIRED` is true
* [#8030](https://github.com/netbox-community/netbox/issues/8030) - Validate custom field names
* [#8033](https://github.com/netbox-community/netbox/issues/8033) - Fix display of zero values for custom integer fields in tables
* [#8035](https://github.com/netbox-community/netbox/issues/8035) - Redirect back to parent prefix after creating IP address(es) where applicable
* [#8038](https://github.com/netbox-community/netbox/issues/8038) - Placeholder filter should display zero integer values
* [#8042](https://github.com/netbox-community/netbox/issues/8042) - Fix filtering cables list by site slug or rack name
* [#8051](https://github.com/netbox-community/netbox/issues/8051) - Contact group parent assignment should not be required under REST API

---

## v3.1.0 (2021-12-06)

!!! warning "PostgreSQL 10 Required"
    NetBox v3.1 requires PostgreSQL 10 or later.

### Breaking Changes

* The `tenant` and `tenant_id` filters for the Cable model now filter on the tenant assigned directly to each cable, rather than on the parent object of either termination.
* The `cable_peer` and `cable_peer_type` attributes of cable termination models have been renamed to `link_peer` and `link_peer_type`, respectively, to accommodate wireless links between interfaces.
* Exported webhooks and custom fields now reference associated content types by raw string value (e.g. "dcim.site") rather than by human-friendly name.
* The 128GFC interface type has been corrected from `128gfc-sfp28` to `128gfc-qsfp28`.

### New Features

#### Contact Objects ([#1344](https://github.com/netbox-community/netbox/issues/1344))

A set of new models for tracking contact information has been introduced within the tenancy app. Users may now create individual contact objects to be associated with various models within NetBox. Each contact has a name, title, email address, etc. Contacts can be arranged in hierarchical groups for ease of management.

When assigning a contact to an object, the user must select a predefined role (e.g. "billing" or "technical") and may optionally indicate a priority relative to other contacts associated with the object. There is no limit on how many contacts can be assigned to an object, nor on how many objects to which a contact can be assigned.

#### Wireless Networks ([#3979](https://github.com/netbox-community/netbox/issues/3979))

This release introduces two new models to represent wireless networks:

* Wireless LAN - A multi-access wireless segment to which any number of wireless interfaces may be attached
* Wireless Link - A point-to-point connection between exactly two wireless interfaces

Both types of connection include SSID and authentication attributes. Additionally, the interface model has been extended to include several attributes pertinent to wireless operation:

* Wireless role - Access point or station
* Channel - A predefined channel within a standardized band
* Channel frequency & width - Customizable channel attributes (e.g. for licensed bands)

#### Dynamic Configuration Updates ([#5883](https://github.com/netbox-community/netbox/issues/5883))

Some parameters of NetBox's configuration are now accessible via the admin UI. These parameters can be modified by an administrator and take effect immediately upon application: There is no need to restart NetBox. Additionally, each iteration of the dynamic configuration is preserved in the database, and can be restored by an administrator at any time.

Dynamic configuration parameters may also still be defined within `configuration.py`, and the settings defined here take precedence over those defined via the user interface.

#### First Hop Redundancy Protocol (FHRP) Groups ([#6235](https://github.com/netbox-community/netbox/issues/6235))

A new FHRP group model has been introduced to aid in modeling the configurations of protocols such as HSRP, VRRP, and GLBP. Each FHRP group may be assigned one or more virtual IP addresses, as well as an authentication type and key. Member device and VM interfaces may be associated with one or more FHRP groups, with each assignment receiving a numeric priority designation.

#### Conditional Webhooks ([#6238](https://github.com/netbox-community/netbox/issues/6238))

Webhooks now include a `conditions` field, which may be used to specify conditions under which a webhook triggers. For example, you may wish to generate outgoing requests for a device webhook only when its status is "active" or "staged". This can be done by declaring conditional logic in JSON:

```json
{
  "attr": "status.value",
  "op": "in",
  "value": ["active", "staged"]
}
```

Multiple conditions may be nested using AND/OR logic as well. For more information, please see the [conditional logic documentation](../reference/conditions.md). 

#### Interface Bridging ([#6346](https://github.com/netbox-community/netbox/issues/6346))

A `bridge` field has been added to the interface model for devices and virtual machines. This can be set to reference another interface on the same parent device/VM to indicate a direct layer two bridging adjacency. Additionally, "bridge" has been added as an interface type. (However, interfaces of any type may be designated as bridged.)

Multiple interfaces can be bridged to a single virtual interface to effect a bridge group. Alternatively, two physical interfaces can be bridged to one another, to effect an internal cross-connect.

#### Multiple ASNs per Site ([#6732](https://github.com/netbox-community/netbox/issues/6732))

With the introduction of the new ASN model, NetBox now supports the assignment of multiple ASNs per site. Each ASN instance must have a 32-bit AS number, and may optionally be assigned to a RIR and/or Tenant.

The `asn` integer field on the site model has been preserved to maintain backward compatability until a later release.

#### Single Sign-On (SSO) Authentication ([#7649](https://github.com/netbox-community/netbox/issues/7649))

Support for single sign-on (SSO) authentication has been added via the [python-social-auth](https://github.com/python-social-auth) library. NetBox administrators can configure one of the [supported authentication backends](https://python-social-auth.readthedocs.io/en/latest/intro.html#auth-providers) to enable SSO authentication for users.

### Enhancements

* [#1337](https://github.com/netbox-community/netbox/issues/1337) - Add WWN field to interfaces
* [#1943](https://github.com/netbox-community/netbox/issues/1943) - Relax uniqueness constraint on cluster names
* [#3839](https://github.com/netbox-community/netbox/issues/3839) - Add `airflow` field for devices types and devices
* [#5143](https://github.com/netbox-community/netbox/issues/5143) - Include a device's asset tag in its display value
* [#6497](https://github.com/netbox-community/netbox/issues/6497) - Extend tag support to organizational models
* [#6615](https://github.com/netbox-community/netbox/issues/6615) - Add filter lookups for custom fields
* [#6711](https://github.com/netbox-community/netbox/issues/6711) - Add `longtext` custom field type with Markdown support
* [#6715](https://github.com/netbox-community/netbox/issues/6715) - Add tenant assignment for cables
* [#6874](https://github.com/netbox-community/netbox/issues/6874) - Add tenant assignment for locations
* [#7354](https://github.com/netbox-community/netbox/issues/7354) - Relax uniqueness constraints on region, site group, and location names
* [#7452](https://github.com/netbox-community/netbox/issues/7452) - Add `json` custom field type
* [#7530](https://github.com/netbox-community/netbox/issues/7530) - Move device type component lists to separate views
* [#7606](https://github.com/netbox-community/netbox/issues/7606) - Model transmit power for interfaces
* [#7619](https://github.com/netbox-community/netbox/issues/7619) - Permit custom validation rules to be defined as plain data or dotted path to class
* [#7761](https://github.com/netbox-community/netbox/issues/7761) - Extend cable tracing across bridged interfaces
* [#7812](https://github.com/netbox-community/netbox/issues/7812) - Enable change logging for image attachments
* [#7858](https://github.com/netbox-community/netbox/issues/7858) - Standardize the representation of content types across import & export functions

### Bug Fixes

* [#7589](https://github.com/netbox-community/netbox/issues/7589) - Correct 128GFC interface type identifier

### Other Changes

* [#7318](https://github.com/netbox-community/netbox/issues/7318) - Raise minimum required PostgreSQL version from 9.6 to 10

### REST API Changes

* Added the following endpoints for ASNs:
    * `/api/ipam/asn/`
* Added the following endpoints for FHRP groups:
    * `/api/ipam/fhrp-groups/`
    * `/api/ipam/fhrp-group-assignments/`
* Added the following endpoints for contacts:
    * `/api/tenancy/contact-assignments/`
    * `/api/tenancy/contact-groups/`
    * `/api/tenancy/contact-roles/`
    * `/api/tenancy/contacts/`
* Added the following endpoints for wireless networks:
    * `/api/wireless/wireless-lans/`
    * `/api/wireless/wireless-lan-groups/`
    * `/api/wireless/wireless-links/`
* Added `tags` field to the following models:
    * circuits.CircuitType
    * dcim.DeviceRole
    * dcim.Location
    * dcim.Manufacturer
    * dcim.Platform
    * dcim.RackRole
    * dcim.Region
    * dcim.SiteGroup
    * ipam.RIR
    * ipam.Role
    * ipam.VLANGroup
    * tenancy.ContactGroup
    * tenancy.ContactRole
    * tenancy.TenantGroup
    * virtualization.ClusterGroup
    * virtualization.ClusterType
* circuits.CircuitTermination
    * `cable_peer` has been renamed to `link_peer`
    * `cable_peer_type` has been renamed to `link_peer_type`
* dcim.Cable
    * Added `tenant` field
* dcim.ConsolePort
    * `cable_peer` has been renamed to `link_peer`
    * `cable_peer_type` has been renamed to `link_peer_type`
* dcim.ConsoleServerPort
    * `cable_peer` has been renamed to `link_peer`
    * `cable_peer_type` has been renamed to `link_peer_type`
* dcim.Device
    * The `display` field now includes the device's asset tag, if set
    * Added `airflow` field
* dcim.DeviceType
    * Added `airflow` field 
* dcim.FrontPort
    * `cable_peer` has been renamed to `link_peer`
    * `cable_peer_type` has been renamed to `link_peer_type`
* dcim.Interface
    * `cable_peer` has been renamed to `link_peer`
    * `cable_peer_type` has been renamed to `link_peer_type`
    * Added `bridge` field
    * Added `rf_channel` field
    * Added `rf_channel_frequency` field
    * Added `rf_channel_width` field
    * Added `rf_role` field
    * Added `tx_power` field
    * Added `wireless_link` field
    * Added `wwn` field
    * Added `count_fhrp_groups` read-only field
* dcim.Location
    * Added `tenant` field
* dcim.PowerFeed
    * `cable_peer` has been renamed to `link_peer`
    * `cable_peer_type` has been renamed to `link_peer_type`
* dcim.PowerOutlet
    * `cable_peer` has been renamed to `link_peer`
    * `cable_peer_type` has been renamed to `link_peer_type`
* dcim.PowerPort
    * `cable_peer` has been renamed to `link_peer`
    * `cable_peer_type` has been renamed to `link_peer_type`
* dcim.RearPort
    * `cable_peer` has been renamed to `link_peer`
    * `cable_peer_type` has been renamed to `link_peer_type`
* dcim.Site
    * Added `asns` relationship to ipam.ASN
* extras.ImageAttachment
    * Added the `last_updated` field
* extras.Webhook
    * Added the `conditions` field
* virtualization.VMInterface
    * Added `bridge` field
    * Added `count_fhrp_groups` read-only field
