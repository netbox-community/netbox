# Devices

Every piece of hardware which is installed within a site or rack exists in NetBox as a device. Devices are measured in rack units (U) and can be half depth or full depth. A device may have a height of 0U: These devices do not consume vertical rack space and cannot be assigned to a particular rack unit. A common example of a 0U device is a vertically-mounted PDU.

When assigning a multi-U device to a rack, it is considered to be mounted in the lowest-numbered rack unit which it occupies. For example, a 3U device which occupies U8 through U10 is said to be mounted in U8. This logic applies to racks with both ascending and descending unit numbering.

A device is said to be full-depth if its installation on one rack face prevents the installation of any other device on the opposite face within the same rack unit(s). This could be either because the device is physically too deep to allow a device behind it, or because the installation of an opposing device would impede airflow.

Each device must be instantiated from a pre-created device type, and its default components (console ports, power ports, interfaces, etc.) will be created automatically. (The device type associated with a device may be changed after its creation, however its components will not be updated retroactively.)

Device names must be unique within a site, unless the device has been assigned to a tenant. Devices may also be unnamed.

When a device has one or more interfaces with IP addresses assigned, a primary IP for the device can be designated, for both IPv4 and IPv6.

## Fields

### Name

The device's configured name. This field is optional; devices can be unnamed. However, if set, the name must be unique to the assigned site and tenant.

### Device Role

The functional [role](./devicerole.md) assigned to this device.

### Device Type

The hardware [device type](./devicetype.md) which defines the device's make & model. Upon creating, all templated components assigned to the device type will be replicated on the new device.

### Airflow

The direction in which air circulates through the device chassis for cooling.

### Serial Number

The unique physical serial number assigned to this device by its manufacturer.

### Asset Tag

A unique, locally-administered label used to identify hardware resources.

### Site

The [site](./site.md) in which this device is located.

### Location

A specific [location](./location.md) where this device resides within the assigned site (optional).

### Rack

The [rack](./rack.md) within which this device is installed (optional).

### Rack Face

If installed in a rack, this field denotes the primary face on which the device is mounted.

### Position

If installed in a rack, this field indicates the base rack unit in which the device is mounted.

!!! tip
    Devices with a height of more than one rack unit should be set to the lowest-numbered rack unit that they occupy.

### Status

The device's operational status.

!!! tip
    Additional statuses may be defined by setting `Device.status` under the [`FIELD_CHOICES`](../../configuration/data-validation.md#field_choices) configuration parameter.

### Platform

A device may be associated with a particular [platform](./platform.md) to indicate its operating system. Note that only platforms assigned to the associated manufacturer (or to no manufacturer) will be available for selection.

### Configuration Template

The [configuration template](../extras/configtemplate.md) from which the configuration for this device can be rendered. If set, this will override any config template referenced by the device's role or platform.

### Primary IPv4 & IPv6 Addresses

Each device may designate one primary IPv4 address and/or one primary IPv6 address for management purposes.

!!! tip
    NetBox will prefer IPv6 addresses over IPv4 addresses by default. This can be changed by setting the `PREFER_IPV4` configuration parameter.

### Cluster

If this device will serve as a host for a virtualization [cluster](../virtualization/cluster.md), it can be assigned here. (Host devices can also be assigned by editing the cluster.)

### Virtual Chassis

The [virtual chassis](./virtualchassis.md) of which this device is a member, if any.

### VC Position

If assigned to a [virtual chassis](./virtualchassis.md), this field indicates the device's member position.

### VC Priority

If assigned to a [virtual chassis](./virtualchassis.md), this field indicates the device's priority for master election.

### Local Config Context Data

Any unique [context data](../../features/context-data.md) to be associated with the device.
