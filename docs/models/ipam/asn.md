# ASN

ASN is short for Autonomous System Number.  This identifier is used in the BGP protocol to identify which "autonomous system" a particular prefix is originating and transiting through.

The AS number model within NetBox allows you to model some of this real-world relationship.

Within NetBox:

* AS numbers are globally unique
* Each AS number must be associated with a RIR (ARIN, RFC 6996, etc)
* Each AS number can be associated with many different sites
* Each site can have many different AS numbers
* Each AS number can be assigned to a single tenant


