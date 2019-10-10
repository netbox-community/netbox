# v1.8.4 (2017-02-03)

## Improvements

* [#856](https://github.com/netbox-community/netbox/issues/856) - Strip whitespace from fields during CSV import

## Bug Fixes

* [#851](https://github.com/netbox-community/netbox/issues/851) - Resolve encoding issues during import/export (Python 3)
* [#854](https://github.com/netbox-community/netbox/issues/854) - Correct processing of get_return_url() in ObjectDeleteView
* [#859](https://github.com/netbox-community/netbox/issues/859) - Fix Javascript for connection status toggle button on device view
* [#861](https://github.com/netbox-community/netbox/issues/861) - Avoid overwriting device primary IP assignment from alternate family during bulk import of IP addresses
* [#865](https://github.com/netbox-community/netbox/issues/865) - Fix server error when attempting to delete a protected object parent (Python 3)

---

# v1.8.3 (2017-01-26)

## Improvements

* [#782](https://github.com/netbox-community/netbox/issues/782) - Allow filtering devices list by manufacturer
* [#820](https://github.com/netbox-community/netbox/issues/820) - Add VLAN column to parent prefixes table on IP address view
* [#821](https://github.com/netbox-community/netbox/issues/821) - Support for comma separation in bulk IP/interface creation
* [#827](https://github.com/netbox-community/netbox/issues/827) - **Introduced support for Python 3**
* [#836](https://github.com/netbox-community/netbox/issues/836) - Add "deprecated" status for IP addresses
* [#841](https://github.com/netbox-community/netbox/issues/841) - Merged search and filter forms on all object lists

## Bug Fixes

* [#816](https://github.com/netbox-community/netbox/issues/816) - Redirect back to parent prefix view after deleting child prefixes termination
* [#817](https://github.com/netbox-community/netbox/issues/817) - Update last_updated time of a circuit when editing a child termination
* [#830](https://github.com/netbox-community/netbox/issues/830) - Redirect user to device view after editing a device component
* [#840](https://github.com/netbox-community/netbox/issues/840) - Correct API path resolution for secrets when BASE_PATH is configured
* [#844](https://github.com/netbox-community/netbox/issues/844) - Apply order_naturally() to API interfaces list
* [#845](https://github.com/netbox-community/netbox/issues/845) - Fix missing edit/delete buttons on object tables for non-superusers

---

# v1.8.2 (2017-01-18)

## Improvements

* [#284](https://github.com/netbox-community/netbox/issues/284) - Enabled toggling of interface display order per device type
* [#760](https://github.com/netbox-community/netbox/issues/760) - Redirect user back to device view after deleting an assigned IP address
* [#783](https://github.com/netbox-community/netbox/issues/783) - Add a description field to the Circuit model
* [#797](https://github.com/netbox-community/netbox/issues/797) - Add description column to VLANs table
* [#803](https://github.com/netbox-community/netbox/issues/803) - Clarify that no child objects are deleted when deleting a prefix
* [#805](https://github.com/netbox-community/netbox/issues/805) - Linkify site column in device table

## Bug Fixes

* [#776](https://github.com/netbox-community/netbox/issues/776) - Prevent circuits from appearing twice while searching
* [#778](https://github.com/netbox-community/netbox/issues/778) - Corrected an issue preventing multiple interfaces with the same position ID from appearing in a device's interface list
* [#785](https://github.com/netbox-community/netbox/issues/785) - Trigger validation error when importing a prefix assigned to a nonexistent VLAN
* [#802](https://github.com/netbox-community/netbox/issues/802) - Fixed enforcement of ENFORCE_GLOBAL_UNIQUE for prefixes
* [#807](https://github.com/netbox-community/netbox/issues/807) - Redirect user back to form when adding IP addresses in bulk and "create and add another" is clicked
* [#810](https://github.com/netbox-community/netbox/issues/810) - Suppress unique IP validation on invalid IP addresses and prefixes

---

# v1.8.1 (2017-01-04)

## Improvements

* [#771](https://github.com/netbox-community/netbox/issues/771) - Don't automatically redirect user when only one object is returned in a list

## Bug Fixes

* [#764](https://github.com/netbox-community/netbox/issues/764) - Encapsulate in double quotes values containing commas when exporting to CSV
* [#767](https://github.com/netbox-community/netbox/issues/767) - Fixes xconnect_id error when searching for circuits
* [#769](https://github.com/netbox-community/netbox/issues/769) - Show default value for boolean custom fields
* [#772](https://github.com/netbox-community/netbox/issues/772) - Fixes TypeError in API RackUnitListView when no device is excluded

---

# v1.8.0 (2017-01-03)

## New Features

### Point-to-Point Circuits ([#49](https://github.com/netbox-community/netbox/issues/49))

Until now, NetBox has supported tracking only one end of a data circuit. This is fine for Internet connections where you don't care (or know) much about the provider side of the circuit, but many users need the ability to track inter-site circuits as well. This release expands circuit modeling so that each circuit can have an A and/or Z side. Each endpoint must be terminated to a site, and may optionally be terminated to a specific device and interface within that site.

### L4 Services ([#539](https://github.com/netbox-community/netbox/issues/539))

Our first major community contribution introduces the ability to track discrete TCP and UDP services associated with a device (for example, SSH or HTTP). Each service can optionally be assigned to one or more specific IP addresses belonging to the device. Thanks to [@if-fi](https://github.com/if-fi) for the addition!

## Improvements

* [#122](https://github.com/netbox-community/netbox/issues/122) - Added comments field to device types
* [#181](https://github.com/netbox-community/netbox/issues/181) - Implemented support for bulk IP address creation
* [#613](https://github.com/netbox-community/netbox/issues/613) - Added prefixes column to VLAN list; added VLAN column to prefix list
* [#716](https://github.com/netbox-community/netbox/issues/716) - Add ASN field to site bulk edit form
* [#722](https://github.com/netbox-community/netbox/issues/722) - Enabled custom fields for device types
* [#743](https://github.com/netbox-community/netbox/issues/743) - Enabled bulk creation of all device components
* [#756](https://github.com/netbox-community/netbox/issues/756) - Added contact details to site model

## Bug Fixes

* [#563](https://github.com/netbox-community/netbox/issues/563) - Allow a device to be flipped from one rack face to the other without moving it
* [#658](https://github.com/netbox-community/netbox/issues/658) - Enabled conditional treatment of network/broadcast IPs for a prefix by defining it as a pool
* [#741](https://github.com/netbox-community/netbox/issues/741) - Hide "select all" button for users without edit permissions
* [#744](https://github.com/netbox-community/netbox/issues/744) - Fixed export of sites without an AS number
* [#747](https://github.com/netbox-community/netbox/issues/747) - Fixed natural_order_by integer cast error on large numbers
* [#751](https://github.com/netbox-community/netbox/issues/751) - Fixed python-cryptography installation issue on Debian
* [#763](https://github.com/netbox-community/netbox/issues/763) - Added missing fields to CSV exports for racks and prefixes
