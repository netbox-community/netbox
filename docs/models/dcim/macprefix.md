# MAC Prefixes

A MAC prefix represents a block of [MAC addresses](./macaddress.md) which share a common leading sequence of bits. For example, an organizationally unique identifier (OUI) such as `BC:24:11` is a MAC prefix with a length of 24 bits, which spans the MAC addresses `BC:24:11:00:00:00` through `BC:24:11:FF:FF:FF`. MAC prefixes can also represent the smaller blocks assigned by the IEEE (MA-M and MA-S blocks have lengths of 28 and 36 bits, respectively), or blocks within an OUI set aside for a particular purpose, such as a virtualization cluster.

A MAC address belongs to every MAC prefix which contains it: MAC addresses are not explicitly assigned to prefixes. The MAC address view shows the most specific prefix which contains it.

Each MAC prefix shows its utilization (the percentage of its MAC addresses which exist in NetBox), and its MAC addresses. A new MAC address can be created from the first available address within the prefix, using either the UI or the REST API (`/api/dcim/mac-prefixes/<id>/available-mac-addresses/`).

## Fields

### Prefix

The first MAC address in the block, for example `BC:24:11:00:00:00`. Any bits beyond the prefix length are cleared when the prefix is saved.

### Prefix Length

The number of leading bits which are shared by all MAC addresses in the block (1 to 48). Defaults to 24, the length of an OUI.

### Name

An optional name for the block, such as the organization to which it is assigned.

### Enforce Unique

If enabled, duplicate MAC addresses are not permitted within this prefix. Uniqueness cannot be enforced on a prefix which already contains duplicate MAC addresses.

### Description

An optional human-readable description of the MAC prefix.

### Comments

Free-form Markdown-supported notes regarding the MAC prefix.
