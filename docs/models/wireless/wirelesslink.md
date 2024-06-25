# Wireless Links

A wireless link represents a connection between exactly two wireless interfaces. Unlike a [wireless LAN](./wirelesslan.md), which permit an arbitrary number of client associations, wireless links are used to model point-to-point wireless connections.

## Fields

### Interfaces

Select two interfaces: One for side A and one for side B. (Both must be wireless interfaces.)

### Status

The operational status of the link. Options include:

* Connected
* Planned
* Decommissioning

### SSID

The service set identifier (SSID) for the wireless link (optional).

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

### Distance

The numeric distance of the link, including a unit designation (e.g. 100 meters or 25 feet).
