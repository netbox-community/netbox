# VLAN Translation Rules

!!! info "This feature was introduced in NetBox v4.2."

A VLAN translation rule represents a one-to-one mapping of a local VLAN ID (VID) to a remote VID. Many rules can belong to a single policy.

See [VLAN translation policies](./vlantranslationpolicy.md) for an overview of the VLAN Translation feature.

## Fields

### Policy

The [VLAN Translation Policy](./vlantranslationpolicy.md) to which this rule belongs.

### Local VID

VLAN ID (1-4094) in the local network which is to be translated to a remote VID.

### Remote VID

VLAN ID (1-4094) in the remote network to which the local VID will be translated.
