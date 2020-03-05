# Platforms

A platform defines the type of software running on a device or virtual machine. This can be helpful when it is necessary to distinguish between, for instance, different feature sets. Note that two devices of the same type may be assigned different platforms: for example, one Juniper MX240 running Junos 14 and another running Junos 15.

The platform model is also used to indicate which [NAPALM](https://napalm-automation.net/) driver NetBox should use when connecting to a remote device. The name of the driver along with optional parameters are stored with the platform.

The assignment of platforms to devices is an optional feature, and may be disregarded if not desired.
