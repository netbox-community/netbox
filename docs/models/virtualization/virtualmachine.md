# Virtual Machines

A virtual machine (VM) represents a virtual compute instance hosted within a [cluster](./cluster.md). Each VM must be assigned to a [site](../dcim/site.md) and/or cluster, and may optionally be assigned to a particular host [device](../dcim/device.md) within a cluster.

Virtual machines may have virtual [interfaces](./vminterface.md) assigned to them, but do not support any physical component. When a VM has one or more interfaces with IP addresses assigned, a primary IP for the device can be designated, for both IPv4 and IPv6.

## Fields

### Name

The virtual machine's configured name. Must be unique to the assigned cluster and tenant.

### Role

The functional [role](../dcim/devicerole.md) assigned to the VM.

### Status

The VM's operational status.

!!! tip
    Additional statuses may be defined by setting `VirtualMachine.status` under the [`FIELD_CHOICES`](../../configuration/data-validation.md#field_choices) configuration parameter.

### Site & Cluster

The [site](../dcim/site.md) and/or [cluster](./cluster.md) to which the VM is assigned.

### Device

The physical host [device](../dcim/device.md) within the assigned site/cluster on which this VM resides.

### Platform

A VM may be associated with a particular [platform](../dcim/platform.md) to indicate its operating system.

### Primary IPv4 & IPv6 Addresses

Each VM may designate one primary IPv4 address and/or one primary IPv6 address for management purposes.

!!! tip
    NetBox will prefer IPv6 addresses over IPv4 addresses by default. This can be changed by setting the `PREFER_IPV4` configuration parameter.

### vCPUs

The number of virtual CPUs provisioned. A VM may be allocated a partial vCPU count (e.g. 1.5 vCPU).

### Memory

The amount of running memory provisioned, in megabytes.

### Disk

The amount of disk storage provisioned, in gigabytes.
