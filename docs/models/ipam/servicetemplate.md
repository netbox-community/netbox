# Application Service Templates

Application service templates can be used to instantiate [application services](./service.md) on [devices](../dcim/device.md) and [virtual machines](../virtualization/virtualmachine.md).

!!! note "Changed in NetBox v4.4"

    Previously, application service templates were referred to simply as "service templates". The name has been changed in the UI to better reflect their intended use. There is no change to the name of the model or in any programmatic NetBox APIs.

## Fields

### Name

A service or protocol name.

### Protocol

The wire protocol on which the service runs. Choices include UDP, TCP, and SCTP.

### Ports

One or more numeric ports to which the service is bound. Multiple ports can be expressed using commas and/or hyphens. For example, `80,8001-8003` specifies ports 80, 8001, 8002, and 8003.
