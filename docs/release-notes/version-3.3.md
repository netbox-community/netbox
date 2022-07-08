# NetBox v3.3

## v3.3.0 (FUTURE)

### Breaking Changes

* Device position and rack unit values are now reported as decimals (e.g. `1.0` or `1.5`) to support modeling half-height rack units.
* The `nat_outside` relation on the IP address model now returns a list of zero or more related IP addresses, rather than a single instance (or None).
* Several fields on the cable API serializers have been altered to support multiple-object cable terminations:

| Old Name             | Old Type | New Name              | New Type |
|----------------------|----------|-----------------------|----------|
| `termination_a_type` | string   | `a_terminations_type` | string   |
| `termination_b_type` | string   | `b_terminations_type` | string   |
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

#### Half-Height Rack Units ([#51](https://github.com/netbox-community/netbox/issues/51))

#### PoE Interface Attributes ([#1099](https://github.com/netbox-community/netbox/issues/1099))

#### L2VPN Modeling ([#8157](https://github.com/netbox-community/netbox/issues/8157))

#### Restrict API Tokens by Client IP ([#8233](https://github.com/netbox-community/netbox/issues/8233))

#### Reference User in Permission Constraints ([#9074](https://github.com/netbox-community/netbox/issues/9074))

#### Multi-object Cable Terminations ([#9102](https://github.com/netbox-community/netbox/issues/9102))

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
* [#8495](https://github.com/netbox-community/netbox/issues/8495) - Enable custom field grouping
* [#8511](https://github.com/netbox-community/netbox/issues/8511) - Enable custom fields and tags for circuit terminations
* [#8995](https://github.com/netbox-community/netbox/issues/8995) - Enable arbitrary ordering of REST API results
* [#9070](https://github.com/netbox-community/netbox/issues/9070) - Hide navigation menu items based on user permissions
* [#9166](https://github.com/netbox-community/netbox/issues/9166) - Add UI visibility toggle for custom fields
* [#9177](https://github.com/netbox-community/netbox/issues/9177) - Add tenant assignment for wireless LANs & links
* [#9536](https://github.com/netbox-community/netbox/issues/9536) - Track API token usage times
* [#9582](https://github.com/netbox-community/netbox/issues/9582) - Enable assigning config contexts based on device location

### Plugins API

* [#9075](https://github.com/netbox-community/netbox/issues/9075) - Introduce `AbortRequest` exception for cleanly interrupting object mutations
* [#9092](https://github.com/netbox-community/netbox/issues/9092) - Add support for `ObjectChildrenView` generic view
* [#9228](https://github.com/netbox-community/netbox/issues/9228) - Subclasses of `ChangeLoggingMixin` can override `serialize_object()` to control JSON serialization for change logging
* [#9414](https://github.com/netbox-community/netbox/issues/9414) - Add `clone()` method to NetBoxModel for copying instance attributes
* [#9647](https://github.com/netbox-community/netbox/issues/9647) - Introduce `customfield_value` template tag

### Other Changes

* [#9261](https://github.com/netbox-community/netbox/issues/9261) - `NetBoxTable` no longer automatically clears pre-existing calls to `prefetch_related()` on its queryset
* [#9434](https://github.com/netbox-community/netbox/issues/9434) - Enabled `django-rich` test runner for more user-friendly output

### REST API Changes

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
    * Added the `device` field
    * Added the `l2vpn_termination` read-only field
wireless.WirelessLAN
    * Added `tenant` field
wireless.WirelessLink
    * Added `tenant` field
