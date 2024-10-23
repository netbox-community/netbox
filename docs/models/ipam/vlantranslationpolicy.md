# VLAN Translation Policies

VLAN translation is a feature that consists of VLAN translation policies and [VLAN translation rules](./vlantranslationrule.md). Many rules can belong to a policy, and each rule defines a mapping of a local to remote VLAN ID (VID). A policy can then be assigned to an [Interface](../dcim/interface.md) or [VMInterface](../virtualization/vminterface.md), and all VLAN translation rules associated with that policy will be visible in the interface details.

Within a policy, local VIDs and remote VIDs are independently unique. Thus, two different policies may contain rules that define a local VID of 100 or a remote VID of 200, but two rules within a single policy with `local_vid=100` or with `remote_vid=200` are prohibited.

## Fields

### Name

A unique human-friendly name.

### Description

A brief description of the policy and/or its purpose.
