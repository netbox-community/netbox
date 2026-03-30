# Virtual Machine Types

A virtual machine type defines a reusable classification and default configuration for [virtual machines](./virtualmachine.md).

A type can optionally provide default values for a VM's [platform](../dcim/platform.md), vCPU allocation, and memory allocation. When a virtual machine is created with an assigned type, any unset values among these fields will inherit their defaults from the type. Changes made to a virtual machine type do **not** apply retroactively to existing virtual machines.

## Fields

### Name

A unique human-friendly name.

### Slug

A unique URL-friendly identifier. (This value can be used for filtering.)

### Default Platform

If defined, virtual machines instantiated with this type will automatically inherit the selected platform when no explicit platform is provided.

### Default vCPUs

The default number of vCPUs to assign when creating a virtual machine from this type.

### Default Memory

The default amount of memory, in megabytes, to assign when creating a virtual machine from this type.
