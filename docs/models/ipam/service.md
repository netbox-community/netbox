# Application Services

An application service represents a layer seven application available on a device or virtual machine. For example, a service might be created in NetBox to represent an HTTP server running on TCP/8000. Each service may optionally be further bound to one or more specific interfaces assigned to the selected device or virtual machine.

To aid in the efficient creation of application services, users may opt to first create an [application service template](./servicetemplate.md) from which service definitions can be quickly replicated.

!!! note "Changed in NetBox v4.4"

    Previously, application services were referred to simply as "services". The name has been changed in the UI to better reflect their intended use. There is no change to the name of the model or in any programmatic NetBox APIs.

## Fields

### Parent

The parent object to which the application service is assigned. This must be one of [Device](../dcim/device.md),
[VirtualMachine](../virtualization/virtualmachine.md), or [FHRP Group](./fhrpgroup.md).

!!! note "Changed in NetBox v4.3"

    Previously, `parent` was a property that pointed to either a Device or Virtual Machine. With the capability to assign services to FHRP groups, this is a unified in a concrete field.

### Name

A service or protocol name.

### Port Assignments

!!! note "Changed in NetBox v4.7"

    Previously, a service defined a single `protocol` (UDP, TCP, or SCTP) shared by all of its `ports`. A service now defines a list of port assignments, where each assignment pairs an individual protocol with a port number. This allows a single service to combine multiple protocols — for example, a DNS service listening on both TCP/53 and UDP/53.

Each port assignment comprises a wire protocol (UDP, TCP, or SCTP) and a numeric port. In the UI, selecting multiple protocols alongside one or more ports creates an assignment for every protocol/port combination.

The deprecated `protocol` and `ports` fields remain available in the REST and GraphQL APIs for backward compatibility. On read, `protocol` returns the single protocol shared by all assignments, or `null` when a service mixes protocols; `ports` returns the flattened list of port numbers. On write, supplying `protocol` and `ports` is translated into the equivalent port assignments (unless `port_assignments` is provided directly).

### IP Addresses

The [IP address(es)](./ipaddress.md) to which this service is bound. If no IP addresses are bound, the service is assumed to be reachable via any assigned IP address.
