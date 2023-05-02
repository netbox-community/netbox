# ASNs

An Autonomous System Number (ASN) is a numeric identifier used in the BGP protocol to identify which [autonomous system](https://en.wikipedia.org/wiki/Autonomous_system_%28Internet%29) a particular prefix is originating and transiting through. NetBox support both 32- and 64- ASNs.

ASNs must be globally unique within NetBox, and may be allocated from within a [defined range](./asnrange.md). Each ASN may be assigned to multiple [sites](../dcim/site.md).

## Fields

### AS Number

The 32- or 64-bit AS number.

### RIR

The [Regional Internet Registry](./rir.md) or similar authority responsible for the allocation of this particular ASN.

### Sites

The [site(s)](../dcim/site.md) to which this ASN is assigned.
