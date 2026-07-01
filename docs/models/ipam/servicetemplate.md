# Application Service Templates

Application service templates can be used to instantiate [application services](./service.md) on [devices](../dcim/device.md) and [virtual machines](../virtualization/virtualmachine.md).

!!! note "Changed in NetBox v4.4"

    Previously, application service templates were referred to simply as "service templates". The name has been changed in the UI to better reflect their intended use. There is no change to the name of the model or in any programmatic NetBox APIs.

## Fields

### Name

A service or protocol name.

### Port Assignments

!!! note "Changed in NetBox v4.7"

    Previously, a service template defined a single `protocol` (UDP, TCP, or SCTP) shared by all of its `ports`. A template now defines a list of port assignments, where each assignment pairs an individual protocol with a port number. This allows a single template to combine multiple protocols — for example, both TCP/53 and UDP/53.

Each port assignment comprises a wire protocol (UDP, TCP, or SCTP) and a numeric port. In the UI, selecting multiple protocols alongside one or more ports creates an assignment for every protocol/port combination.

The deprecated `protocol` and `ports` fields remain available in the REST and GraphQL APIs for backward compatibility, as described for [application services](./service.md).
