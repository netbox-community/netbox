# NetBox v3.3

## v3.3.2 (2022-09-02)

### Enhancements

* [#9477](https://github.com/netbox-community/netbox/issues/9477) - Enable clearing applied table column ordering
* [#10034](https://github.com/netbox-community/netbox/issues/10034) - Add L2VPN column to interface and VLAN tables
* [#10043](https://github.com/netbox-community/netbox/issues/10043) - Add support for `limit` query parameter to available VLANs API endpoint
* [#10060](https://github.com/netbox-community/netbox/issues/10060) - Add journal entries to global search
* [#10195](https://github.com/netbox-community/netbox/issues/10195) - Enable filtering of device components by rack
* [#10233](https://github.com/netbox-community/netbox/issues/10233) - Enable sorting rack elevations by facility ID

### Bug Fixes

* [#9328](https://github.com/netbox-community/netbox/issues/9328) - Hide available IPs when non-default ordering is applied
* [#9481](https://github.com/netbox-community/netbox/issues/9481) - Update child device location when parent location changes
* [#9832](https://github.com/netbox-community/netbox/issues/9832) - Improve error message when validating rack reservation units
* [#9895](https://github.com/netbox-community/netbox/issues/9895) - Various corrections to OpenAPI spec
* [#9962](https://github.com/netbox-community/netbox/issues/9962) - SSO login should respect `next` URL query parameter
* [#9963](https://github.com/netbox-community/netbox/issues/9963) - Fix support for custom `CSRF_COOKIE_NAME` value
* [#10155](https://github.com/netbox-community/netbox/issues/10155) - Fix rear port display when editing front port template for module type 
* [#10156](https://github.com/netbox-community/netbox/issues/10156) - Avoid forcing SVG image links to open in a new window
* [#10161](https://github.com/netbox-community/netbox/issues/10161) - Restore "set null" option for custom fields during bulk edit
* [#10176](https://github.com/netbox-community/netbox/issues/10176) - Correct utilization display for empty racks
* [#10177](https://github.com/netbox-community/netbox/issues/10177) - Correct display of custom fields when editing VM interfaces
* [#10178](https://github.com/netbox-community/netbox/issues/10178) - Display manufacturer name alongside device type under device view
* [#10181](https://github.com/netbox-community/netbox/issues/10181) - Restore MultiPartParser (regression from #10031)
* [#10184](https://github.com/netbox-community/netbox/issues/10184) - Fix vertical alignment when displaying object attributes with buttons
* [#10208](https://github.com/netbox-community/netbox/issues/10208) - Fix permissions evaluation for interface actions dropdown menu
* [#10217](https://github.com/netbox-community/netbox/issues/10217) - Handle exception when trace splits to multiple rear ports
* [#10220](https://github.com/netbox-community/netbox/issues/10220) - Validate IP version when assigning primary IPs to a virtual machine
* [#10231](https://github.com/netbox-community/netbox/issues/10231) - Correct API schema definition for several serializer fields

---

## v3.3.1 (2022-08-25)

### Enhancements

* [#6454](https://github.com/netbox-community/netbox/issues/6454) - Include contextual help when creating first objects in UI
* [#9935](https://github.com/netbox-community/netbox/issues/9935) - Add 802.11ay and "other" wireless interface types
* [#10031](https://github.com/netbox-community/netbox/issues/10031) - Enforce `application/json` content type for REST API requests
* [#10033](https://github.com/netbox-community/netbox/issues/10033) - Disable "add termination" button for point-to-point L2VPNs with two terminations
* [#10037](https://github.com/netbox-community/netbox/issues/10037) - Add "child interface" option to actions dropdown in interfaces list
* [#10038](https://github.com/netbox-community/netbox/issues/10038) - Add "L2VPN termination" option to actions dropdown in interfaces list
* [#10039](https://github.com/netbox-community/netbox/issues/10039) - Add "assign FHRP group" option to actions dropdown in interfaces list
* [#10061](https://github.com/netbox-community/netbox/issues/10061) - Replicate type when cloning L2VPN instances
* [#10066](https://github.com/netbox-community/netbox/issues/10066) - Use fixed column widths for custom field values in UI
* [#10133](https://github.com/netbox-community/netbox/issues/10133) - Enable nullifying device location during bulk edit

### Bug Fixes

* [#9663](https://github.com/netbox-community/netbox/issues/9663) - Omit available IP annotations when filtering prefix child IPs list
* [#10040](https://github.com/netbox-community/netbox/issues/10040) - Fix exception when ordering prefixes by flat representation
* [#10053](https://github.com/netbox-community/netbox/issues/10053) - Custom fields header should not be displayed when editing circuit terminations with no custom fields
* [#10055](https://github.com/netbox-community/netbox/issues/10055) - Fix extraneous NAT indicator by device primary IP
* [#10057](https://github.com/netbox-community/netbox/issues/10057) - Fix AttributeError exception when global search results include rack reservations
* [#10059](https://github.com/netbox-community/netbox/issues/10059) - Add identifier column to L2VPN table
* [#10070](https://github.com/netbox-community/netbox/issues/10070) - Add unique constraint for L2VPN slug
* [#10087](https://github.com/netbox-community/netbox/issues/10087) - Correct display of far end in console/power/interface connections tables
* [#10089](https://github.com/netbox-community/netbox/issues/10089) - `linkify` template filter should escape object representation
* [#10094](https://github.com/netbox-community/netbox/issues/10094) - Fix 404 when using "create and add another" to add contact assignments
* [#10108](https://github.com/netbox-community/netbox/issues/10108) - Linkify inside NAT IPs for primary device IPs in UI
* [#10109](https://github.com/netbox-community/netbox/issues/10109) - Fix available prefixes calculation for container prefixes in the global table
* [#10111](https://github.com/netbox-community/netbox/issues/10111) - Fix ValueError exception when searching for L2VPN objects
* [#10118](https://github.com/netbox-community/netbox/issues/10118) - Fix display of connected LLDP neighbors for devices
* [#10134](https://github.com/netbox-community/netbox/issues/10134) - Custom fields data serializer should return a 400 response for invalid data
* [#10135](https://github.com/netbox-community/netbox/issues/10135) - Fix SSO support for SAML2 IDPs
* [#10147](https://github.com/netbox-community/netbox/issues/10147) - Permit the creation of 0U device types via REST API

---

## v3.3.0 (2022-08-17)

### Breaking Changes

* Device position, device type height, and rack unit values are now reported as decimals (e.g. `1.0` or `1.5`) to support modeling half-height rack units.
* The `nat_outside` relation on the IP address model now returns a list of zero or more related IP addresses, rather than a single instance (or None).
* Several fields on the cable API serializers have been altered or removed to support multiple-object cable terminations:

| Old Name             | Old Type | New Name              | New Type |
|----------------------|----------|-----------------------|----------|
| `termination_a_type` | string   | _Removed_             | -        |
| `termination_b_type` | string   | _Removed_             | -        |
| `termination_a_id`   | integer  | _Removed_             | -        |
| `termination_b_id`   | integer  | _Removed_             | -        |
| `termination_a`      | object   | `a_terminations`      | list     |
| `termination_b`      | object   | `b_terminations`      | list     |

* As with the cable model, several API fields on all objects to which cables can be connected (interfaces, circuit terminations, etc.) have been changed:

| Old Name                       | Old Type | New Name                        | New Type |
|--------------------------------|----------|---------------------------------|----------|
| `link_peer`                    | object   | `link_peers`                    | list     |
| `link_peer_type`               | string   | `link_peers_type`               | string   |
| `connected_endpoint`           | object   | `connected_endpoints`           | list     |
| `connected_endpoint_type`      | string   | `connected_endpoints_type`      | string   |
| `connected_endpoint_reachable` | boolean  | `connected_endpoints_reachable` | boolean  |

* The cable path serialization returned by the `/paths/` endpoint for pass-through ports has been simplified, and the following fields removed: `origin_type`, `origin`, `destination_type`, `destination`. (Additionally, `is_complete` has been added.)

### New Features

#### Multi-object Cable Terminations ([#9102](https://github.com/netbox-community/netbox/issues/9102))

When creating a cable in NetBox, each end can now be attached to multiple termination points. This allows accurate modeling of duplex fiber connections to individual termination ports and breakout cables, for example. (Note that all terminations attached to one end of a cable must be the same object type, but do not need to connect to the same parent object.) Additionally, cable terminations can now be modified without needing to delete and recreate the cable.

#### L2VPN Modeling ([#8157](https://github.com/netbox-community/netbox/issues/8157))

NetBox can now model a variety of L2 VPN technologies, including VXLAN, VPLS, and others. Interfaces and VLANs can be attached to L2VPNs to track connectivity across an overlay. Similarly to VRFs, each L2VPN can also have import and export route targets associated with it.

#### PoE Interface Attributes ([#1099](https://github.com/netbox-community/netbox/issues/1099))

Two new fields have been added to the device interface model to track Power over Ethernet (PoE) capabilities:

* **PoE mode**: Power supplying equipment (PSE) or powered device (PD)
* **PoE type**: Applicable IEEE standard or other power type 

#### Half-Height Rack Units ([#51](https://github.com/netbox-community/netbox/issues/51))

Device type height can now be specified in 0.5U increments, allowing for the creation of devices consume partial rack units. Additionally, a device can be installed at the half-unit mark within a rack (e.g. U2.5). For example, two half-height devices positioned in sequence will consume a single rack unit; two consecutive 1.5U devices will consume 3U of space.

#### Restrict API Tokens by Client IP ([#8233](https://github.com/netbox-community/netbox/issues/8233))

API tokens can now be restricted to use by certain client IP addresses or networks. For example, an API token with its `allowed_ips` list set to `[192.0.2.0/24]` will permit authentication only from API clients within that network; requests from other sources will fail authentication. This enables administrators to restrict the use of a token to specific clients.

#### Reference User in Permission Constraints ([#9074](https://github.com/netbox-community/netbox/issues/9074))

NetBox's permission constraints have been expanded to support referencing the current user associated with a request using the special `$user` token. As an example, this enables an administrator to efficiently grant each user to edit his or her own journal entries, but not those created by other users.

```json
{
  "created_by": "$user"
}
```

#### Custom Field Grouping ([#8495](https://github.com/netbox-community/netbox/issues/8495))

A `group_name` field has been added to the custom field model to enable organizing related custom fields by group. Similarly to custom links, custom fields which have been assigned to the same group will be rendered within that group when viewing an object in the UI. (Custom field grouping has no effect on API operation.)

#### Toggle Custom Field Visibility ([#9166](https://github.com/netbox-community/netbox/issues/9166))

The behavior of each custom field within the NetBox UI can now be controlled individually by toggling its UI visibility. Three options are available:

* **Read/write**: The custom field is included when viewing and editing objects (default).
* **Read-only**: The custom field is displayed when viewing an object, but it cannot be edited via the UI. (It will appear in the form as a read-only field.)
* **Hidden**: The custom field will never be displayed within the UI. This option is recommended for fields which are not intended for use by human users.

Custom field UI visibility has no impact on API operation.

### Enhancements

* [#1202](https://github.com/netbox-community/netbox/issues/1202) - Support overlapping assignment of NAT IP addresses
* [#4350](https://github.com/netbox-community/netbox/issues/4350) - Illustrate reservations vertically alongside rack elevations
* [#4434](https://github.com/netbox-community/netbox/issues/4434) - Enable highlighting devices within rack elevations
* [#5303](https://github.com/netbox-community/netbox/issues/5303) - A virtual machine may be assigned to a site and/or cluster
* [#7120](https://github.com/netbox-community/netbox/issues/7120) - Add `termination_date` field to Circuit
* [#7744](https://github.com/netbox-community/netbox/issues/7744) - Add `status` field to Location
* [#8171](https://github.com/netbox-community/netbox/issues/8171) - Populate next available address when cloning an IP
* [#8222](https://github.com/netbox-community/netbox/issues/8222) - Enable the assignment of a VM to a specific host device within a cluster
* [#8471](https://github.com/netbox-community/netbox/issues/8471) - Add `status` field to Cluster
* [#8511](https://github.com/netbox-community/netbox/issues/8511) - Enable custom fields and tags for circuit terminations
* [#8995](https://github.com/netbox-community/netbox/issues/8995) - Enable arbitrary ordering of REST API results
* [#9070](https://github.com/netbox-community/netbox/issues/9070) - Hide navigation menu items based on user permissions
* [#9177](https://github.com/netbox-community/netbox/issues/9177) - Add tenant assignment for wireless LANs & links
* [#9391](https://github.com/netbox-community/netbox/issues/9391) - Remove 500-character limit for custom link text & URL fields
* [#9536](https://github.com/netbox-community/netbox/issues/9536) - Track API token usage times
* [#9582](https://github.com/netbox-community/netbox/issues/9582) - Enable assigning config contexts based on device location

### Bug Fixes (from Beta2)

* [#9758](https://github.com/netbox-community/netbox/issues/9758) - Display parent object of connected termination
* [#9900](https://github.com/netbox-community/netbox/issues/9900) - Pre-populate site & rack fields for cable connection form
* [#9938](https://github.com/netbox-community/netbox/issues/9938) - Exclude virtual interfaces from terminations list when connecting a cable
* [#9939](https://github.com/netbox-community/netbox/issues/9939) - Fix list of next nodes for split paths under trace view

### Plugins API

* [#9075](https://github.com/netbox-community/netbox/issues/9075) - Introduce `AbortRequest` exception for cleanly interrupting object mutations
* [#9092](https://github.com/netbox-community/netbox/issues/9092) - Add support for `ObjectChildrenView` generic view
* [#9228](https://github.com/netbox-community/netbox/issues/9228) - Subclasses of `ChangeLoggingMixin` can override `serialize_object()` to control JSON serialization for change logging
* [#9414](https://github.com/netbox-community/netbox/issues/9414) - Add `clone()` method to NetBoxModel for copying instance attributes
* [#9647](https://github.com/netbox-community/netbox/issues/9647) - Introduce `customfield_value` template tag

### Other Changes

* [#9261](https://github.com/netbox-community/netbox/issues/9261) - `NetBoxTable` no longer automatically clears pre-existing calls to `prefetch_related()` on its queryset
* [#9434](https://github.com/netbox-community/netbox/issues/9434) - Enabled `django-rich` test runner for more user-friendly output
* [#9903](https://github.com/netbox-community/netbox/issues/9903) - Implement a mechanism for automatically updating denormalized fields

### REST API Changes

* List results can now be ordered by field, by appending `?ordering={fieldname}` to the query. Multiple fields can be specified by separating the field names with a comma, e.g. `?ordering=site,name`. To invert the ordering, prepend a hyphen to the field name, e.g. `?ordering=-name`.
* Added the following endpoints:
    * `/api/dcim/cable-terminations/`
    * `/api/ipam/l2vpns/`
    * `/api/ipam/l2vpn-terminations/`
* circuits.Circuit
    * Added optional `termination_date` field
* circuits.CircuitTermination
    * `link_peer` has been renamed to `link_peers` and now returns a list of objects
    * `link_peer_type` has been renamed to `link_peers_type`
    * `connected_endpoint` has been renamed to `connected_endpoints` and now returns a list of objects
    * `connected_endpoint_type` has been renamed to `connected_endpoints_type`
    * `connected_endpoint_reachable` has been renamed to `connected_endpoints_reachable`
    * Added `custom_fields` and `tags` fields
* dcim.Cable
    * `termination_a_type` has been renamed to `a_terminations_type`
    * `termination_b_type` has been renamed to `b_terminations_type`
    * `termination_a` renamed to `a_terminations` and now returns a list of objects
    * `termination_b` renamed to `b_terminations` and now returns a list of objects
    * `termination_a_id` has been removed
    * `termination_b_id` has been removed
* dcim.ConsolePort
    * `link_peer` has been renamed to `link_peers` and now returns a list of objects
    * `link_peer_type` has been renamed to `link_peers_type`
    * `connected_endpoint` has been renamed to `connected_endpoints` and now returns a list of objects
    * `connected_endpoint_type` has been renamed to `connected_endpoints_type`
    * `connected_endpoint_reachable` has been renamed to `connected_endpoints_reachable`
* dcim.ConsoleServerPort
    * `link_peer` has been renamed to `link_peers` and now returns a list of objects
    * `link_peer_type` has been renamed to `link_peers_type`
    * `connected_endpoint` has been renamed to `connected_endpoints` and now returns a list of objects
    * `connected_endpoint_type` has been renamed to `connected_endpoints_type`
    * `connected_endpoint_reachable` has been renamed to `connected_endpoints_reachable`
* dcim.Device
    * The `position` field has been changed from an integer to a decimal
* dcim.DeviceType
    * The `u_height` field has been changed from an integer to a decimal
* dcim.FrontPort
    * `link_peer` has been renamed to `link_peers` and now returns a list of objects
    * `link_peer_type` has been renamed to `link_peers_type`
    * `connected_endpoint` has been renamed to `connected_endpoints` and now returns a list of objects
    * `connected_endpoint_type` has been renamed to `connected_endpoints_type`
    * `connected_endpoint_reachable` has been renamed to `connected_endpoints_reachable`
* dcim.Interface
    * `link_peer` has been renamed to `link_peers` and now returns a list of objects
    * `link_peer_type` has been renamed to `link_peers_type`
    * `connected_endpoint` has been renamed to `connected_endpoints` and now returns a list of objects
    * `connected_endpoint_type` has been renamed to `connected_endpoints_type`
    * `connected_endpoint_reachable` has been renamed to `connected_endpoints_reachable`
    * Added the optional `poe_mode` and `poe_type` fields
    * Added the `l2vpn_termination` read-only field
* dcim.InterfaceTemplate
    * Added the optional `poe_mode` and `poe_type` fields
* dcim.Location
    * Added required `status` field (default value: `active`)
* dcim.PowerOutlet
    * `link_peer` has been renamed to `link_peers` and now returns a list of objects
    * `link_peer_type` has been renamed to `link_peers_type`
    * `connected_endpoint` has been renamed to `connected_endpoints` and now returns a list of objects
    * `connected_endpoint_type` has been renamed to `connected_endpoints_type`
    * `connected_endpoint_reachable` has been renamed to `connected_endpoints_reachable`
* dcim.PowerFeed
    * `link_peer` has been renamed to `link_peers` and now returns a list of objects
    * `link_peer_type` has been renamed to `link_peers_type`
    * `connected_endpoint` has been renamed to `connected_endpoints` and now returns a list of objects
    * `connected_endpoint_type` has been renamed to `connected_endpoints_type`
    * `connected_endpoint_reachable` has been renamed to `connected_endpoints_reachable`
* dcim.PowerPort
    * `link_peer` has been renamed to `link_peers` and now returns a list of objects
    * `link_peer_type` has been renamed to `link_peers_type`
    * `connected_endpoint` has been renamed to `connected_endpoints` and now returns a list of objects
    * `connected_endpoint_type` has been renamed to `connected_endpoints_type`
    * `connected_endpoint_reachable` has been renamed to `connected_endpoints_reachable`
* dcim.Rack
    * The `elevation` endpoint now includes half-height rack units, and utilizes decimal values for the ID and name of each unit
* dcim.RearPort
    * `link_peer` has been renamed to `link_peers` and now returns a list of objects
    * `link_peer_type` has been renamed to `link_peers_type`
    * `connected_endpoint` has been renamed to `connected_endpoints` and now returns a list of objects
    * `connected_endpoint_type` has been renamed to `connected_endpoints_type`
    * `connected_endpoint_reachable` has been renamed to `connected_endpoints_reachable`
* extras.ConfigContext
    * Added the `locations` many-to-many field to track the assignment of ConfigContexts to Locations
* extras.CustomField
    * Added `group_name` and `ui_visibility` fields
* ipam.IPAddress
    * The `nat_inside` field no longer requires a unique value
    * The `nat_outside` field has changed from a single IP address instance to a list of multiple IP addresses
* ipam.VLAN
    * Added the `l2vpn_termination` read-only field
* users.Token
    * Added the `allowed_ips` array field
    * Added the read-only `last_used` datetime field
* virtualization.Cluster
    * Added required `status` field (default value: `active`)
* virtualization.VirtualMachine
    * The `site` field is now directly writable (rather than being inferred from the assigned cluster)
    * The `cluster` field is now optional. A virtual machine must have a site and/or cluster assigned.
    * Added the optional `device` field
    * Added the `l2vpn_termination` read-only field
wireless.WirelessLAN
    * Added `tenant` field
wireless.WirelessLink
    * Added `tenant` field
