# VLAN Translation Policies

!!! info "This feature was introduced in NetBox v4.2."

VLAN translation is a feature that consists of VLAN translation policies and [VLAN translation rules](./vlantranslationrule.md). Many rules can belong to a policy, and each rule defines a mapping of a local to remote VLAN ID (VID). A policy can then be assigned to an [Interface](../dcim/interface.md) or [VMInterface](../virtualization/vminterface.md), and all VLAN translation rules associated with that policy will be visible in the interface details.

There are uniqueness constraints on `(policy, local_vid)` and on `(policy, remote_vid)` in the `VLANTranslationRule` model. Thus, you cannot have multiple rules linked to the same policy that have the same local VID or the same remote VID. A set of policies and rules might look like this:

Policy 1:
- Rule: 100 -> 200
- Rule: 101 -> 201

Policy 2:
- Rule: 100 -> 300
- Rule: 101 -> 301

However this is not allowed:

Policy 3:
- Rule: 100 -> 200
- Rule: 100 -> 300


## Fields

### Name

A unique human-friendly name.
