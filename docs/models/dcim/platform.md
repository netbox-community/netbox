# Platforms

A platform defines the type of software running on a device or virtual machine. This can be helpful to model when it is necessary to distinguish between different versions or feature sets. Note that two devices of the same type may be assigned different platforms: For example, one Juniper MX240 might run Junos 14 while another runs Junos 15.

Platforms may optionally be limited by manufacturer: If a platform is assigned to a particular manufacturer, it can only be assigned to devices with a type belonging to that manufacturer.

The platform model is also used to indicate which [NAPALM](../../additional-features/napalm.md) driver and any associated arguments NetBox should use when connecting to a remote device. The name of the driver along with optional parameters are stored with the platform.

The assignment of platforms to devices is an optional feature, and may be disregarded if not desired.
