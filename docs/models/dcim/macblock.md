# MAC Address Blocks

A MAC address block represents a contiguous range of [MAC addresses](./macaddress.md), defined by a prefix (the first address in the block) and a prefix length (the number of leading bits shared by every address in it). This mirrors the blocks assigned by the IEEE: an organizationally unique identifier (OUI, or MA-L block) such as `BC:24:11` is a MAC address block with a prefix length of 24, spanning the MAC addresses `BC:24:11:00:00:00` through `BC:24:11:FF:FF:FF`. The smaller MA-M and MA-S blocks have lengths of 28 and 36 bits, respectively. Blocks can also represent ranges within an assigned block which are set aside for a particular purpose, such as a virtualization cluster.

A MAC address belongs to every MAC address block which contains it: MAC addresses are not explicitly assigned to blocks. The MAC address view shows the most specific block which contains it.

Each MAC address block shows its utilization (the percentage of its MAC addresses which exist in NetBox), and its MAC addresses. A new MAC address can be created from the first available address within the block, using either the UI or the REST API (`/api/dcim/mac-blocks/<id>/available-mac-addresses/`).

## Fields

### Prefix

The first MAC address in the block, for example `BC:24:11:00:00:00`. Any bits beyond the prefix length are cleared when the prefix is saved.

### Prefix Length

The number of leading bits which are shared by all MAC addresses in the block (1 to 48). Defaults to 24, the length of an OUI.

### Name

An optional name for the block, such as the organization to which it is assigned.

### Enforce Unique

If enabled, duplicate MAC addresses are not permitted within this block. Uniqueness cannot be enforced on a block which already contains duplicate MAC addresses.

### Description

An optional human-readable description of the MAC address block.

### Comments

Free-form Markdown-supported notes regarding the MAC address block.
