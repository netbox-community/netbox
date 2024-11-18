# Wireless LANs

A wireless LAN is a set of interfaces connected via a common wireless channel, identified by its SSID and authentication parameters. Wireless [interfaces](../dcim/interface.md) can be associated with wireless LANs to model multi-acess wireless segments.

## Fields

### SSID

The service set identifier (SSID) for the wireless network.

### Group

The [wireless LAN group](./wirelesslangroup.md) to which this wireless LAN is assigned (if any).

### Status

The operational status of the wireless network.

!!! tip
    Additional statuses may be defined by setting `WirelessLAN.status` under the [`FIELD_CHOICES`](../../configuration/data-validation.md#field_choices) configuration parameter.

### VLAN

Each wireless LAN can optionally be mapped to a [VLAN](../ipam/vlan.md), to model a bridge between wired and wireless segments.

### Authentication Type

The type of wireless authentication in use. Options include:

* Open
* WEP
* WPA Personal (PSK)
* WPA Enterprise

### Authentication Cipher

The security cipher used to apply wireless authentication. Options include:

* Auto (automatic)
* TKIP
* AES

### Pre-Shared Key

The security key configured on each client to grant access to the secured wireless LAN. This applies only to certain authentication types.

### Scope

The [region](../dcim/region.md), [site](../dcim/site.md), [site group](../dcim/sitegroup.md) or [location](../dcim/location.md) with which this wireless LAN is associated.
