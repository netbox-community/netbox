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

### Port Mappings

The protocols and ports on which the service runs. A service may expose the same port on multiple protocols — for example, DNS listening on both `tcp/53` and `udp/53`. In the UI, ports for a given protocol may be entered together using commas and/or hyphens (e.g. `80,8001-8003`).

In the REST and GraphQL APIs, port mappings are represented as a list of `{protocol, ports}` objects — one entry per protocol:

```json
[
  {"protocol": "tcp", "ports": [80, 443]},
  {"protocol": "udp", "ports": [53]}
]
```

!!! note "Changed in NetBox v4.7"

    The single-protocol `protocol` and `ports` fields have been replaced by the unified `port_mappings` field (which supports multiple protocols per service, in the grouped form shown above). For backward compatibility, the REST and GraphQL APIs still expose the legacy `protocol` and `ports` fields, and the REST API still accepts them on write as an alternative to `port_mappings`. They are populated for single-protocol services; a service with multiple protocols cannot be represented in the legacy format and returns `null` for both, while a service with no mappings returns `protocol: null` and `ports: []`. In other words, `ports: null` specifically signals "multiple protocols — read `port_mappings` instead." **These legacy fields are deprecated and will be removed in a future release; use `port_mappings` instead.**

### IP Addresses

The [IP address(es)](./ipaddress.md) to which this service is bound. If no IP addresses are bound, the service is assumed to be reachable via any assigned IP address.
