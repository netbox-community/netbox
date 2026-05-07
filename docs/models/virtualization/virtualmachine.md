# Virtual Machines

A virtual machine (VM) represents a virtual compute instance hosted within a cluster or directly on a device. Each VM must be assigned to at least one of: a [site](../dcim/site.md), a [cluster](./cluster.md), or a [device](../dcim/device.md).

Virtual machines may have virtual [interfaces](./vminterface.md) assigned to them, but do not support any physical component. When a VM has one or more interfaces with IP addresses assigned, a primary IP for the VM can be designated, for both IPv4 and IPv6.

## Fields

### Name

The virtual machine's configured name. Must be unique within its scoping context:

- If assigned to a **cluster**: unique within the cluster and tenant.
- If assigned to a **device** (no cluster): unique within the device and tenant.

### Type

The [virtual machine type](./virtualmachinetype.md) assigned to the VM. A type classifies a virtual machine and can provide default values for platform, vCPUs, and memory when the VM is created.

Changes made to a virtual machine type do **not** apply retroactively to existing virtual machines.

### Role

The functional role assigned to the VM.

### Status

The VM's operational status.

!!! tip
    Additional statuses may be defined by setting `VirtualMachine.status` under the [`FIELD_CHOICES`](../../configuration/data-validation.md#field_choices) configuration parameter.

### Start on Boot

The start on boot setting from the hypervisor.

!!! tip
    Additional statuses may be defined by setting `VirtualMachine.start_on_boot` under the [`FIELD_CHOICES`](../../configuration/data-validation.md#field_choices) configuration parameter.

### Site / Cluster / Device

The location or host for this VM. At least one must be specified:

- **Site only**: The VM exists at a site but is not assigned to a specific cluster or device.
- **Cluster only**: The VM belongs to a virtualization cluster. The site is automatically inferred from the cluster's scope.
- **Device only**: The VM runs directly on a physical host device without a cluster (e.g. containers). The site is automatically inferred from the device's site.
- **Cluster + Device**: The VM belongs to a cluster and is pinned to a specific host device within that cluster. The device must be a registered host of the assigned cluster.

!!! info "New in NetBox v4.6"
    Virtual machines can now be assigned directly to a device without requiring a cluster. This is particularly useful for modeling VMs running on standalone hosts outside of a cluster.

### Platform

A VM may be associated with a particular [platform](../dcim/platform.md) to indicate its operating system. If a virtual machine type defines a default platform, it will be applied when the VM is created unless an explicit platform is specified.

### Primary IPv4 & IPv6 Addresses

Each VM may designate one primary IPv4 address and/or one primary IPv6 address for management purposes.

!!! tip
    NetBox will prefer IPv6 addresses over IPv4 addresses by default. This can be changed by setting the `PREFER_IPV4` configuration parameter.

### vCPUs

The number of virtual CPUs provisioned. A VM may be allocated a partial vCPU count (e.g. 1.5 vCPU). If a virtual machine type defines a default vCPU allocation, it will be applied when the VM is created unless an explicit value is specified.

### Memory

The amount of running memory provisioned, in megabytes. If a virtual machine type defines a default memory allocation, it will be applied when the VM is created unless an explicit value is specified.

### Disk

The amount of disk storage provisioned, in megabytes.

!!! warning
    This field may be directly modified only on virtual machines which do not define discrete [virtual disks](./virtualdisk.md). Otherwise, it will report the sum of all attached disks.

### Serial Number

Optional serial number assigned to this virtual machine.

!!! info
    Unlike devices, uniqueness is not enforced for virtual machine serial numbers.
