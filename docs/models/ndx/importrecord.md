# NDX Import Records

An import record tracks an object (such as a device type) which was imported from the [NetBox Data Exchange](../../features/ndx.md) catalog. Import records are created and updated automatically when entries are imported, and are deleted along with the objects they track. A record may be deleted to stop tracking an object without affecting the object itself.

## Fields

### Object

The NetBox object created from the catalog entry.

### NDX ID

The catalog's unique identifier for the entry, in the form `<vendor slug>/<slug>`.

### Entry Type

The type of catalog entry (e.g. `device-type`, `module-type`, or `rack-type`).

### Vendor Slug

The catalog's identifier for the entry's vendor.

### Source

The origin of the catalog entry: NetBox Labs, the community device type library, or both.

### Checksum

The catalog's checksum for the entry's vendor at the time of import. This is used to detect updates.

### Update Available

Indicates that the catalog has changed since the entry was imported. This flag is set by the periodic catalog sync, and is cleared when the entry is re-imported.

### Last Imported

The date and time at which the entry was most recently imported.
