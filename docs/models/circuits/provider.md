# Providers

A provider is any entity which provides some form of connectivity of among sites or organizations within a site. While this obviously includes carriers which offer Internet and private transit service, it might also include Internet exchange (IX) points and even organizations with whom you peer directly. Each [circuit](./circuit.md) within NetBox must be assigned a provider and a circuit ID which is unique to that provider.

## Fields

### Name

A unique human-friendly name.

### Slug

A unique URL-friendly identifier. (This value can be used for filtering.)

### ASNs

The [AS numbers](../ipam/asn.md) assigned to this provider (optional).

### Portal URL

The URL for the provider's customer service portal.

### NOC Contact

Contact details for the provider's network operations center (NOC).

### Admin Contact

Administrative contact details for the provider.
