# NetBox v2.0 Release Notes

## v2.0.10 (2017-07-14)

### Bug Fixes

* [#1312](https://github.com/netbox-community/netbox/issues/1312) - Catch error when attempting to activate a user key with an invalid private key
* [#1333](https://github.com/netbox-community/netbox/issues/1333) - Corrected label on is_console_server field of DeviceType bulk edit form
* [#1338](https://github.com/netbox-community/netbox/issues/1338) - Allow importing prefixes with "container" status
* [#1339](https://github.com/netbox-community/netbox/issues/1339) - Fixed disappearing checkbox column under django-tables2 v1.7+
* [#1342](https://github.com/netbox-community/netbox/issues/1342) - Allow designation of users and groups when creating/editing a secret role

---

## v2.0.9 (2017-07-10)

### Bug Fixes

* [#1319](https://github.com/netbox-community/netbox/issues/1319) - Fixed server error when attempting to create console/power connections
* [#1325](https://github.com/netbox-community/netbox/issues/1325) - Retain interface attachment when editing a circuit termination

---

## v2.0.8 (2017-07-05)

### Enhancements

* [#1298](https://github.com/netbox-community/netbox/issues/1298) - Calculate prefix utilization based on its status (container or non-container)
* [#1303](https://github.com/netbox-community/netbox/issues/1303) - Highlight installed interface connections in green on device view
* [#1315](https://github.com/netbox-community/netbox/issues/1315) - Enforce lowercase file extensions for image attachments

### Bug Fixes

* [#1279](https://github.com/netbox-community/netbox/issues/1279) - Fix primary_ip assignment during IP address import
* [#1281](https://github.com/netbox-community/netbox/issues/1281) - Show LLDP neighbors tab on device view only if necessary conditions are met
* [#1282](https://github.com/netbox-community/netbox/issues/1282) - Fixed tooltips on "mark connected/planned" toggle buttons for device connections
* [#1288](https://github.com/netbox-community/netbox/issues/1288) - Corrected permission name for deleting image attachments
* [#1289](https://github.com/netbox-community/netbox/issues/1289) - Retain inside NAT assignment when editing an IP address
* [#1297](https://github.com/netbox-community/netbox/issues/1297) - Allow passing custom field choice selection PKs to API as string-quoted integers
* [#1299](https://github.com/netbox-community/netbox/issues/1299) - Corrected permission name for adding services to devices

---

## v2.0.7 (2017-06-15)

### Enhancements

* [#626](https://github.com/netbox-community/netbox/issues/626) - Added bulk disconnect function for console/power/interface connections on device view

### Bug Fixes

* [#1238](https://github.com/netbox-community/netbox/issues/1238) - Fix error when editing an IP with a NAT assignment which has no assigned device
* [#1263](https://github.com/netbox-community/netbox/issues/1263) - Differentiate add and edit permissions for objects
* [#1265](https://github.com/netbox-community/netbox/issues/1265) - Fix console/power/interface connection validation when selecting a device via live search
* [#1266](https://github.com/netbox-community/netbox/issues/1266) - Prevent terminating a circuit to an already-connected interface
* [#1268](https://github.com/netbox-community/netbox/issues/1268) - Fix CSV import error under Python 3
* [#1273](https://github.com/netbox-community/netbox/issues/1273) - Corrected status choices in IP address import form
* [#1274](https://github.com/netbox-community/netbox/issues/1274) - Exclude unterminated circuits from topology maps
* [#1275](https://github.com/netbox-community/netbox/issues/1275) - Raise validation error on prefix import when multiple VLANs are found

---

## v2.0.6 (2017-06-12)

### Enhancements

* [#40](https://github.com/netbox-community/netbox/issues/40) - Added IP utilization graph to prefix list
* [#704](https://github.com/netbox-community/netbox/issues/704) - Allow filtering VLANs by group when editing prefixes
* [#913](https://github.com/netbox-community/netbox/issues/913) - Added headers to object CSV exports
* [#990](https://github.com/netbox-community/netbox/issues/990) - Enable logging configuration in configuration.py
* [#1180](https://github.com/netbox-community/netbox/issues/1180) - Simplified the process of finding related devices when viewing a device

### Bug Fixes

* [#1253](https://github.com/netbox-community/netbox/issues/1253) - Improved `upgrade.sh` to allow forcing Python2

---

## v2.0.5 (2017-06-08)

### Notes

The maximum number of objects an API consumer can request has been set to 1000 (e.g. `?limit=1000`). This limit can be modified by defining `MAX_PAGE_SIZE` in confgiuration.py. (To remove this limit, set `MAX_PAGE_SIZE=0`.)

### Enhancements

* [#655](https://github.com/netbox-community/netbox/issues/655) - Implemented header-based CSV import of objects
* [#1190](https://github.com/netbox-community/netbox/issues/1190) - Allow partial string matching when searching on custom fields
* [#1237](https://github.com/netbox-community/netbox/issues/1237) - Enabled setting limit=0 to disable pagination in API requests; added `MAX_PAGE_SIZE` configuration setting

### Bug Fixes

* [#837](https://github.com/netbox-community/netbox/issues/837) - Enforce uniqueness where applicable during bulk import of IP addresses
* [#1226](https://github.com/netbox-community/netbox/issues/1226) - Improved validation for custom field values submitted via the API
* [#1232](https://github.com/netbox-community/netbox/issues/1232) - Improved rack space validation on bulk import of devices (see #655)
* [#1235](https://github.com/netbox-community/netbox/issues/1235) - Fix permission name for adding/editing inventory items
* [#1236](https://github.com/netbox-community/netbox/issues/1236) - Truncate rack names in elevations list; add facility ID
* [#1239](https://github.com/netbox-community/netbox/issues/1239) - Fix server error when creating VLANGroup via API
* [#1243](https://github.com/netbox-community/netbox/issues/1243) - Catch ValueError in IP-based object filters
* [#1244](https://github.com/netbox-community/netbox/issues/1244) - Corrected "device" secrets filter to accept a device name

---

## v2.0.4 (2017-05-25)

### Bug Fixes

* [#1206](https://github.com/netbox-community/netbox/issues/1206) - Fix redirection in admin UI after activating secret keys when BASE_PATH is set
* [#1207](https://github.com/netbox-community/netbox/issues/1207) - Include nested LAG serializer when showing interface connections (API)
* [#1210](https://github.com/netbox-community/netbox/issues/1210) - Fix TemplateDoesNotExist errors on browsable API views
* [#1212](https://github.com/netbox-community/netbox/issues/1212) - Allow assigning new VLANs to global VLAN groups
* [#1213](https://github.com/netbox-community/netbox/issues/1213) - Corrected table header ordering links on object list views
* [#1214](https://github.com/netbox-community/netbox/issues/1214) - Add status to list of required fields on child device import form
* [#1219](https://github.com/netbox-community/netbox/issues/1219) - Fix image attachment URLs when BASE_PATH is set
* [#1220](https://github.com/netbox-community/netbox/issues/1220) - Suppressed innocuous warning about untracked migrations under Python 3
* [#1229](https://github.com/netbox-community/netbox/issues/1229) - Fix validation error on forms where API search is used

---

## v2.0.3 (2017-05-18)

### Enhancements

* [#1196](https://github.com/netbox-community/netbox/issues/1196) - Added a lag_id filter to the API interfaces view
* [#1198](https://github.com/netbox-community/netbox/issues/1198) - Allow filtering unracked devices on device list

### Bug Fixes

* [#1157](https://github.com/netbox-community/netbox/issues/1157) - Hide nav menu search bar on small displays
* [#1186](https://github.com/netbox-community/netbox/issues/1186) - Corrected VLAN edit form so that site assignment is not required
* [#1187](https://github.com/netbox-community/netbox/issues/1187) - Fixed table pagination by introducing a custom table template
* [#1188](https://github.com/netbox-community/netbox/issues/1188) - Serialize interface LAG as nested objected (API)
* [#1189](https://github.com/netbox-community/netbox/issues/1189) - Enforce consistent ordering of objects returned by a global search
* [#1191](https://github.com/netbox-community/netbox/issues/1191) - Bulk selection of IPs under a prefix incorrect when "select all" is used
* [#1195](https://github.com/netbox-community/netbox/issues/1195) - Unable to create an interface connection when searching for peer device
* [#1197](https://github.com/netbox-community/netbox/issues/1197) - Fixed status assignment during bulk import of devices, prefixes, IPs, and VLANs
* [#1199](https://github.com/netbox-community/netbox/issues/1199) - Bulk import of secrets does not prompt user to generate a session key
* [#1200](https://github.com/netbox-community/netbox/issues/1200) - Form validation error when connecting power ports to power outlets

---

## v2.0.2 (2017-05-15)

### Enhancements

* [#1122](https://github.com/netbox-community/netbox/issues/1122) - Include NAT inside IPs in IP address list
* [#1137](https://github.com/netbox-community/netbox/issues/1137) - Allow filtering devices list by rack
* [#1170](https://github.com/netbox-community/netbox/issues/1170) - Include A and Z sites for circuits in global search results
* [#1172](https://github.com/netbox-community/netbox/issues/1172) - Linkify racks in side-by-side elevations view
* [#1177](https://github.com/netbox-community/netbox/issues/1177) - Render planned connections as dashed lines on topology maps
* [#1179](https://github.com/netbox-community/netbox/issues/1179) - Adjust topology map text color based on node background
* On all object edit forms, allow filtering the tenant list by tenant group

### Bug Fixes

* [#1158](https://github.com/netbox-community/netbox/issues/1158) - Exception thrown when creating a device component with an invalid name
* [#1159](https://github.com/netbox-community/netbox/issues/1159) - Only superusers can see "edit IP" buttons on the device interfaces list
* [#1160](https://github.com/netbox-community/netbox/issues/1160) - Linkify secrets and tenants in global search results
* [#1161](https://github.com/netbox-community/netbox/issues/1161) - Fix "add another" behavior when creating an API token
* [#1166](https://github.com/netbox-community/netbox/issues/1166) - Fixed bulk IP address creation when assigning tenants
* [#1168](https://github.com/netbox-community/netbox/issues/1168) - Total count of objects missing from list view paginator
* [#1171](https://github.com/netbox-community/netbox/issues/1171) - Allow removing site assignment when bulk editing VLANs
* [#1173](https://github.com/netbox-community/netbox/issues/1173) - Tweak interface manager to fall back to naive ordering

---

## v2.0.1 (2017-05-10)

### Bug Fixes

* [#1149](https://github.com/netbox-community/netbox/issues/1149) - Port list does not populate when creating a console or power connection
* [#1150](https://github.com/netbox-community/netbox/issues/1150) - Error when uploading image attachments with Unicode names under Python 2
* [#1151](https://github.com/netbox-community/netbox/issues/1151) - Server error: name 'escape' is not defined
* [#1152](https://github.com/netbox-community/netbox/issues/1152) - Unable to edit user keys
* [#1153](https://github.com/netbox-community/netbox/issues/1153) - UnicodeEncodeError when searching for non-ASCII characters on Python 2

---

## v2.0.0 (2017-05-09)

### New Features

#### API 2.0 ([#113](https://github.com/netbox-community/netbox/issues/113))

The NetBox API has been completely rewritten and now features full read/write ability.

#### Image Attachments ([#152](https://github.com/netbox-community/netbox/issues/152))

Users are now able to attach photos and other images to sites, racks, and devices. (Please ensure that the new `media` directory is writable by the system account NetBox runs as.)

#### Global Search ([#159](https://github.com/netbox-community/netbox/issues/159))

NetBox now supports searching across all primary object types at once.

#### Rack Elevations View ([#951](https://github.com/netbox-community/netbox/issues/951))

A new view has been introduced to display the elevations of multiple racks side-by-side.

### Enhancements

* [#154](https://github.com/netbox-community/netbox/issues/154) - Expanded device status field to include options other than active/offline
* [#430](https://github.com/netbox-community/netbox/issues/430) - Include circuits when rendering topology maps
* [#578](https://github.com/netbox-community/netbox/issues/578) - Show topology maps not assigned to a site on the home view
* [#1100](https://github.com/netbox-community/netbox/issues/1100) - Add a "view all" link to completed bulk import views is_pool for prefixes)
* [#1110](https://github.com/netbox-community/netbox/issues/1110) - Expand bulk edit forms to include boolean fields (e.g. toggle is_pool for prefixes)

### Bug Fixes

From v1.9.6:

* [#403](https://github.com/netbox-community/netbox/issues/403) - Record console/power/interface connects and disconnects as user actions
* [#853](https://github.com/netbox-community/netbox/issues/853) -  Added "status" field to device bulk import form
* [#1101](https://github.com/netbox-community/netbox/issues/1101) - Fix AJAX scripting for device component selection forms
* [#1103](https://github.com/netbox-community/netbox/issues/1103) - Correct handling of validation errors when creating IP addresses in bulk
* [#1104](https://github.com/netbox-community/netbox/issues/1104) - Fix VLAN assignment on prefix import
* [#1115](https://github.com/netbox-community/netbox/issues/1115) - Enabled responsive (side-scrolling) tables for small screens
* [#1116](https://github.com/netbox-community/netbox/issues/1116) - Correct object links on recursive deletion error
* [#1125](https://github.com/netbox-community/netbox/issues/1125) - Include MAC addresses on a device's interface list
* [#1144](https://github.com/netbox-community/netbox/issues/1144) - Allow multiple status selections for Prefix, IP address, and VLAN filters

From beta3:

* [#1113](https://github.com/netbox-community/netbox/issues/1113) - Fixed server error when attempting to delete an image attachment
* [#1114](https://github.com/netbox-community/netbox/issues/1114) - Suppress OSError when attempting to access a deleted image attachment
* [#1126](https://github.com/netbox-community/netbox/issues/1126) - Fixed server error when editing a user key via admin UI attachment
* [#1132](https://github.com/netbox-community/netbox/issues/1132) - Prompt user to unlock session key when importing secrets

### Additional Changes

* The Module DCIM model has been renamed to InventoryItem to better reflect its intended function, and to make room for work on [#824](https://github.com/netbox-community/netbox/issues/824).
* Redundant portions of the admin UI have been removed ([#973](https://github.com/netbox-community/netbox/issues/973)).
* The Docker build components have been moved into [their own repository](https://github.com/netbox-community/netbox-docker).
