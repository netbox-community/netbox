# NetBox v2.2 Release Notes

## v2.2.10 (2018-02-21)

### Enhancements

* [#78](https://github.com/netbox-community/netbox/issues/78) - Extended topology maps to support console and power connections
* [#1693](https://github.com/netbox-community/netbox/issues/1693) - Allow specifying loose or exact matching for custom field filters
* [#1714](https://github.com/netbox-community/netbox/issues/1714) - Standardized CSV export functionality for all object lists
* [#1876](https://github.com/netbox-community/netbox/issues/1876) - Added explanatory title text to disabled NAPALM buttons on device view
* [#1885](https://github.com/netbox-community/netbox/issues/1885) - Added a device filter field for primary IP

### Bug Fixes

* [#1858](https://github.com/netbox-community/netbox/issues/1858) - Include device/VM count for cluster list in global search results
* [#1859](https://github.com/netbox-community/netbox/issues/1859) - Implemented support for line breaks within CSV fields
* [#1860](https://github.com/netbox-community/netbox/issues/1860) - Do not populate initial values for custom fields when editing objects in bulk
* [#1869](https://github.com/netbox-community/netbox/issues/1869) - Corrected ordering of VRFs with duplicate names
* [#1886](https://github.com/netbox-community/netbox/issues/1886) - Allow setting the primary IPv4/v6 address for a virtual machine via the web UI

---

## v2.2.9 (2018-01-31)

### Enhancements

* [#144](https://github.com/netbox-community/netbox/issues/144) - Implemented bulk import/edit/delete views for InventoryItems
* [#1073](https://github.com/netbox-community/netbox/issues/1073) - Include prefixes/IPs from all VRFs when viewing the children of a container prefix in the global table
* [#1366](https://github.com/netbox-community/netbox/issues/1366) - Enable searching for regions by name/slug
* [#1406](https://github.com/netbox-community/netbox/issues/1406) - Display tenant description as title text in object tables
* [#1824](https://github.com/netbox-community/netbox/issues/1824) - Add virtual machine count to platforms list
* [#1835](https://github.com/netbox-community/netbox/issues/1835) - Consistent positioning of previous/next rack buttons

### Bug Fixes

* [#1621](https://github.com/netbox-community/netbox/issues/1621) - Tweaked LLDP interface name evaluation logic
* [#1765](https://github.com/netbox-community/netbox/issues/1765) - Improved rendering of null options for model choice fields in filter forms
* [#1807](https://github.com/netbox-community/netbox/issues/1807) - Populate VRF from parent when creating a new prefix
* [#1809](https://github.com/netbox-community/netbox/issues/1809) - Populate tenant assignment from parent when creating a new prefix
* [#1818](https://github.com/netbox-community/netbox/issues/1818) - InventoryItem API serializer no longer requires specifying a null value for items with no parent
* [#1845](https://github.com/netbox-community/netbox/issues/1845) - Correct display of VMs in list with no role assigned
* [#1850](https://github.com/netbox-community/netbox/issues/1850) - Fix TypeError when attempting IP address import if only unnamed devices exist

---

## v2.2.8 (2017-12-20)

### Enhancements

* [#1771](https://github.com/netbox-community/netbox/issues/1771) - Added name filter for racks
* [#1772](https://github.com/netbox-community/netbox/issues/1772) - Added position filter for devices
* [#1773](https://github.com/netbox-community/netbox/issues/1773) - Moved child prefixes table to its own view
* [#1774](https://github.com/netbox-community/netbox/issues/1774) - Include a button to refine search results for all object types under global search
* [#1784](https://github.com/netbox-community/netbox/issues/1784) - Added `cluster_type` filters for virtual machines

### Bug Fixes

* [#1766](https://github.com/netbox-community/netbox/issues/1766) - Fixed display of "select all" button on device power outlets list
* [#1767](https://github.com/netbox-community/netbox/issues/1767) - Use proper template for 404 responses
* [#1778](https://github.com/netbox-community/netbox/issues/1778) - Preserve initial VRF assignment when adding IP addresses in bulk from a prefix
* [#1783](https://github.com/netbox-community/netbox/issues/1783) - Added `vm_role` filter for device roles
* [#1785](https://github.com/netbox-community/netbox/issues/1785) - Omit filter forms from browsable API
* [#1787](https://github.com/netbox-community/netbox/issues/1787) - Added missing site field to virtualization cluster CSV export

---

## v2.2.7 (2017-12-07)

### Enhancements

* [#1722](https://github.com/netbox-community/netbox/issues/1722) - Added virtual machine count to site view
* [#1737](https://github.com/netbox-community/netbox/issues/1737) - Added a `contains` API filter to find all prefixes containing a given IP or prefix

### Bug Fixes

* [#1712](https://github.com/netbox-community/netbox/issues/1712) - Corrected tenant inheritance for new IP addresses created from a parent prefix
* [#1721](https://github.com/netbox-community/netbox/issues/1721) - Differentiated child IP count from utilization percentage for prefixes
* [#1740](https://github.com/netbox-community/netbox/issues/1740) - Delete session_key cookie on logout
* [#1741](https://github.com/netbox-community/netbox/issues/1741) - Fixed Unicode support for secret plaintexts
* [#1743](https://github.com/netbox-community/netbox/issues/1743) - Include number of instances for device types in global search
* [#1751](https://github.com/netbox-community/netbox/issues/1751) - Corrected filtering for IPv6 addresses containing letters
* [#1756](https://github.com/netbox-community/netbox/issues/1756) - Improved natural ordering of console server ports and power outlets

---

## v2.2.6 (2017-11-16)

### Enhancements

* [#1669](https://github.com/netbox-community/netbox/issues/1669) - Clicking "add an IP" from the prefix view will default to the first available IP within the prefix

### Bug Fixes

* [#1397](https://github.com/netbox-community/netbox/issues/1397) - Display global search in navigation menu unless display is less than 1200px wide
* [#1599](https://github.com/netbox-community/netbox/issues/1599) - Reduce mobile cut-off for navigation menu to 960px
* [#1715](https://github.com/netbox-community/netbox/issues/1715) - Added missing import buttons on object lists
* [#1717](https://github.com/netbox-community/netbox/issues/1717) - Fixed interface validation for virtual machines
* [#1718](https://github.com/netbox-community/netbox/issues/1718) - Set empty label to "Global" or VRF field in IP assignment form

---

## v2.2.5 (2017-11-14)

### Enhancements

* [#1512](https://github.com/netbox-community/netbox/issues/1512) - Added a view to search for an IP address being assigned to an interface
* [#1679](https://github.com/netbox-community/netbox/issues/1679) - Added IP address roles to device/VM interface lists
* [#1683](https://github.com/netbox-community/netbox/issues/1683) - Replaced default 500 handler with custom middleware to provide preliminary troubleshooting assistance
* [#1684](https://github.com/netbox-community/netbox/issues/1684) - Replaced prefix `parent` filter with `within` and `within_include`

### Bug Fixes

* [#1471](https://github.com/netbox-community/netbox/issues/1471) - Correct bulk selection of IP addresses within a prefix assigned to a VRF
* [#1642](https://github.com/netbox-community/netbox/issues/1642) - Validate device type classification when creating console server ports and power outlets
* [#1650](https://github.com/netbox-community/netbox/issues/1650) - Correct numeric ordering for interfaces with no alphabetic type
* [#1676](https://github.com/netbox-community/netbox/issues/1676) - Correct filtering of child prefixes upon bulk edit/delete from the parent prefix view
* [#1689](https://github.com/netbox-community/netbox/issues/1689) - Disregard IP address mask when filtering for child IPs of a prefix
* [#1696](https://github.com/netbox-community/netbox/issues/1696) - Fix for NAPALM v2.0+
* [#1699](https://github.com/netbox-community/netbox/issues/1699) - Correct nested representation in the API of primary IPs for virtual machines and add missing primary_ip property
* [#1701](https://github.com/netbox-community/netbox/issues/1701) - Fixed validation in `extras/0008_reports.py` migration for certain versions of PostgreSQL
* [#1703](https://github.com/netbox-community/netbox/issues/1703) - Added API serializer validation for custom integer fields
* [#1705](https://github.com/netbox-community/netbox/issues/1705) - Fixed filtering of devices with a status of offline

---

## v2.2.4 (2017-10-31)

### Bug Fixes

* [#1670](https://github.com/netbox-community/netbox/issues/1670) - Fixed server error when calling certain filters (regression from #1649)

---

## v2.2.3 (2017-10-31)

### Enhancements

* [#999](https://github.com/netbox-community/netbox/issues/999) - Display devices on which circuits are terminated in circuits list
* [#1491](https://github.com/netbox-community/netbox/issues/1491) - Added initial data for the virtualization app
* [#1620](https://github.com/netbox-community/netbox/issues/1620) - Loosen IP address search filter to match all IPs that start with the given string
* [#1631](https://github.com/netbox-community/netbox/issues/1631) - Added a `post_run` method to the Report class
* [#1666](https://github.com/netbox-community/netbox/issues/1666) - Allow modifying the owner of a rack reservation

### Bug Fixes

* [#1513](https://github.com/netbox-community/netbox/issues/1513) - Correct filtering of custom field choices
* [#1603](https://github.com/netbox-community/netbox/issues/1603) - Hide selection checkboxes for tables with no available actions
* [#1618](https://github.com/netbox-community/netbox/issues/1618) - Allow bulk deletion of all virtual machines
* [#1619](https://github.com/netbox-community/netbox/issues/1619) - Correct text-based filtering of IP network and address fields
* [#1624](https://github.com/netbox-community/netbox/issues/1624) - Add VM count to device roles table
* [#1634](https://github.com/netbox-community/netbox/issues/1634) - Cluster should not be a required field when importing child devices
* [#1649](https://github.com/netbox-community/netbox/issues/1649) - Correct filtering on null values (e.g. ?tenant_id=0) for django-filters v1.1.0+
* [#1653](https://github.com/netbox-community/netbox/issues/1653) - Remove outdated description for DeviceType's `is_network_device` flag
* [#1664](https://github.com/netbox-community/netbox/issues/1664) - Added missing `serial` field in default rack CSV export

---

## v2.2.2 (2017-10-17)

### Enhancements

* [#1580](https://github.com/netbox-community/netbox/issues/1580) - Allow cluster assignment when bulk importing devices
* [#1587](https://github.com/netbox-community/netbox/issues/1587) - Add primary IP column for virtual machines in global search results

### Bug Fixes

* [#1498](https://github.com/netbox-community/netbox/issues/1498) - Avoid duplicating nodes when generating topology maps
* [#1579](https://github.com/netbox-community/netbox/issues/1579) - Devices already assigned to a cluster cannot be added to a different cluster
* [#1582](https://github.com/netbox-community/netbox/issues/1582) - Add `virtual_machine` attribute to IPAddress
* [#1584](https://github.com/netbox-community/netbox/issues/1584) - Colorized virtual machine role column
* [#1585](https://github.com/netbox-community/netbox/issues/1585) - Fixed slug-based filtering of virtual machines
* [#1605](https://github.com/netbox-community/netbox/issues/1605) - Added clusters and virtual machines to object list for global search
* [#1609](https://github.com/netbox-community/netbox/issues/1609) - Added missing `virtual_machine` field to IP address interface serializer

---

## v2.2.1 (2017-10-12)

### Bug Fixes

* [#1576](https://github.com/netbox-community/netbox/issues/1576) - Moved PostgreSQL validation logic into the relevant migration (fixed ImproperlyConfigured exception on init)

---

## v2.2.0 (2017-10-12)

**Note:** This release requires PostgreSQL 9.4 or higher. Do not attempt to upgrade unless you are running at least PostgreSQL 9.4.

**Note:** The release replaces the deprecated pycrypto library with [pycryptodome](https://github.com/Legrandin/pycryptodome). The upgrade script has been extended to automatically uninstall the old library, but please verify your installed packages with `pip freeze | grep pycrypto` if you run into problems.

### New Features

#### Virtual Machines and Clusters ([#142](https://github.com/netbox-community/netbox/issues/142))

Our second-most popular feature request has arrived! NetBox now supports the creation of virtual machines, which can be assigned virtual interfaces and IP addresses. VMs are arranged into clusters, each of which has a type and (optionally) a group.

#### Custom Validation Reports ([#1511](https://github.com/netbox-community/netbox/issues/1511))

Users can now create custom reports which are run to validate data in NetBox. Reports work very similar to Python unit tests: Each report inherits from NetBox's Report class and contains one or more test method. Reports can be run and retrieved via the web UI, API, or CLI. See [the docs](http://netbox.readthedocs.io/en/stable/miscellaneous/reports/) for more info.

### Enhancements

* [#494](https://github.com/netbox-community/netbox/issues/494) - Include asset tag in device info pop-up on rack elevation
* [#1444](https://github.com/netbox-community/netbox/issues/1444) - Added a `serial` field to the rack model
* [#1479](https://github.com/netbox-community/netbox/issues/1479) - Added an IP address role for CARP
* [#1506](https://github.com/netbox-community/netbox/issues/1506) - Extended rack facility ID field from 30 to 50 characters
* [#1510](https://github.com/netbox-community/netbox/issues/1510) - Added ability to search by name when adding devices to a cluster
* [#1527](https://github.com/netbox-community/netbox/issues/1527) - Replace deprecated pycrypto library with pycryptodome
* [#1551](https://github.com/netbox-community/netbox/issues/1551) - Added API endpoints listing static field choices for each app
* [#1556](https://github.com/netbox-community/netbox/issues/1556) - Added CPAK, CFP2, and CFP4 100GE interface form factors
* Added CSV import views for all object types

### Bug Fixes

* [#1550](https://github.com/netbox-community/netbox/issues/1550) - Corrected interface connections link in navigation menu
* [#1554](https://github.com/netbox-community/netbox/issues/1554) - Don't require form_factor when creating an interface assigned to a virtual machine
* [#1557](https://github.com/netbox-community/netbox/issues/1557) - Added filtering for virtual machine interfaces
* [#1567](https://github.com/netbox-community/netbox/issues/1567) - Prompt user for session key when importing secrets

### API Changes

* Introduced the virtualization app and its associated endpoints at `/api/virtualization`
* Added the `/api/extras/reports` endpoint for fetching and running reports
* The `ipam.Service` and `dcim.Interface` models now have a `virtual_machine` field in addition to the `device` field. Only one of the two fields may be defined for each object
* Added a `vm_role` field to `dcim.DeviceRole`, which indicates whether a role is suitable for assigned to a virtual machine
* Added a `serial` field to 'dcim.Rack` for serial numbers
* Each app now has a `_choices` endpoint, which lists the available options for all model field with static choices (e.g. interface form factors)
