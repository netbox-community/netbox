# Platforms

A platform defines the type of software running on a [device](./device.md) or [virtual machine](../virtualization/virtualmachine.md). This can be helpful to model when it is necessary to distinguish between different versions or feature sets. Note that two devices of the same type may be assigned different platforms: For example, one Juniper MX240 might run Junos 14 while another runs Junos 15.

Platforms may optionally be limited by [manufacturer](./manufacturer.md): If a platform is assigned to a particular manufacturer, it can only be assigned to devices with a type belonging to that manufacturer.

The assignment of platforms to devices is an optional feature, and may be disregarded if not desired.

## Fields

### Name

A unique human-friendly name.

### Slug

A unique URL-friendly identifier. (This value can be used for filtering.)

### Manufacturer

If designated, this platform will be available for use only to devices assigned to this [manufacturer](./manufacturer.md). This can be handy e.g. for limiting network operating systems to use on hardware produced by the relevant vendor. However, it should not be used when defining general-purpose software platforms.

### Configuration Template

The default [configuration template](../extras/configtemplate.md) for devices assigned to this platform.
