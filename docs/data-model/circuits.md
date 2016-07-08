The circuits component of NetBox deals with the management of long-haul Internet and private transit links and providers.

[TOC]

# Providers

A provider is any entity which provides some form of connectivity. This obviously includes carriers which offer Internet and private transit service. However, it might also include Internet exchange (IX) points and even organizations with whom you peer directly.

Each provider may be assigned an autonomous system number (ASN) for reference. Each provider can also be assigned account and contact information, as well as miscellaneous comments.

---

# Circuits

A circuit represents a single physical data link connecting two endpoints. Each circuit belongs to a provider and must be assigned circuit ID which is unique to that provider. Each circuit must also be assigned to a site, and may optionally be connected to a specific interface on a specific device within that site.

NetBox also tracks miscellaneous circuit attributes (most of which are optional), including:

* Date of installation
* Port speed
* Commit rate
* Cross-connect ID
* Patch panel information

### Circuit Types

Circuits can be classified by type. For example:

* Internet transit
* Out-of-band connectivity
* Peering
* Private backhaul

Each circuit must be assigned exactly one circuit type.