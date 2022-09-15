# Regional Internet Registries (RIRs)

[Regional Internet registries](https://en.wikipedia.org/wiki/Regional_Internet_registry) are responsible for the allocation of globally-routable address space. The five RIRs are ARIN, RIPE, APNIC, LACNIC, and AFRINIC. However, some address space has been set aside for internal use, such as defined in RFCs 1918 and 6598. NetBox considers these RFCs as a sort of RIR as well; that is, an authority which "owns" certain address space. There also exist lower-tier registries which serve particular geographic areas.

Users can create whatever RIRs they like, but each [aggregate](./aggregate.md) must be assigned to one RIR. For example, suppose your organization has been allocated 104.131.0.0/16 by ARIN. It also makes use of RFC 1918 addressing internally. You would first create RIRs named "ARIN" and "RFC 1918," then create an aggregate for each of these top-level prefixes, assigning it to its respective RIR.

## Fields

### Name

A unique human-friendly name.

### Slug

A unique URL-friendly identifier. (This value can be used for filtering.)

### Private

Designates this RIR as an authority for private/local IP space only (e.g. an RFC).
