# Service Templates

Service templates can be used to instantiate [services](./service.md) on [devices](../dcim/device.md) and [virtual machines](../virtualization/virtualmachine.md).

## Fields

### Name

A service or protocol name.

### Protocol

The wire protocol on which the service runs. Choices include UDP, TCP, and SCTP.

### Ports

One or more numeric ports to which the service is bound. Multiple ports can be expressed using commas and/or hyphens. For example, `80,8001-8003` specifies ports 80, 8001, 8002, and 8003.
