# Data Files

A data file object is the representation in NetBox's database of some file belonging to a remote [data source](./datasource.md). Data files are synchronized automatically, and cannot be modified locally (although they can be deleted).

## Fields

### Source

The [data source](./datasource.md) to which this file belongs.

### Path

The path to the file, relative to its source's URL. For example, a file at `/opt/config-data/routing/bgp/peer.yaml` with a source URL of `file:///opt/config-data/` would have its path set to `routing/bgp/peer.yaml`.

### Last Updated

The date and time at which the file most recently updated from its source. Note that this attribute is updated only when the file's contents have been modified. Re-synchronizing the data source will not update this timestamp if the upstream file's data has not changed.

### Size

The file's size, in bytes.

### Hash

A [SHA256 hash](https://en.wikipedia.org/wiki/SHA-2) of the file's data. This can be compared to a hash taken from the original file to determine whether any changes have been made.
