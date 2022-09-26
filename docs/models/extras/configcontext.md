# Configuration Contexts

Context data is made available to [devices](../dcim/device.md) and/or [virtual machines](../virtualization/virtualmachine.md) based on their relationships to other objects in NetBox. For example, context data can be associated only with devices assigned to a particular site, or only to virtual machines in a certain cluster.

See the [context data documentation](../../features/context-data.md) for more information.

## Fields

### Name

A unique human-friendly name.

### Weight

A numeric value which influences the order in which context data is merged. Contexts with a lower weight are merged before those with a higher weight.

### Data

The context data expressed in JSON format.

### Is Active

If not selected, this config context will be excluded from rendering. This can be convenient to temporarily disable a config context.

### Object Assignment

Each configuration context may be assigned with any number of objects of the supported types. If no related objects are selected, it will be considered a "global" config context and apply to all devices and virtual machines.
