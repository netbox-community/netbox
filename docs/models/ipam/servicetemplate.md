# Application Service Templates

Application service templates can be used to instantiate [application services](./service.md) on [devices](../dcim/device.md) and [virtual machines](../virtualization/virtualmachine.md).

!!! note "Changed in NetBox v4.4"

    Previously, application service templates were referred to simply as "service templates". The name has been changed in the UI to better reflect their intended use. There is no change to the name of the model or in any programmatic NetBox APIs.

## Fields

### Name

A service or protocol name.

### Port Mappings

One or more [port mappings](./serviceportmapping.md), each pairing a wire protocol (UDP, TCP, or SCTP) with one or more port numbers. The same port may be exposed on multiple protocols by adding a mapping per protocol. Within a single mapping, multiple ports can be expressed using commas and/or hyphens (e.g. `80,8001-8003`).
