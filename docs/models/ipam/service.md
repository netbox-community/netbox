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

In the REST and GraphQL APIs, port mappings are represented as a flat list of `protocol/port` strings — matching how they are stored:

```json
[
  "tcp/80",
  "tcp/443",
  "udp/53"
]
```

!!! note "Changed in NetBox v4.7"

    The single-protocol `protocol` and `ports` fields have been replaced by the unified `port_mappings` field, which supports multiple protocols per service. For backward compatibility, the REST and GraphQL APIs still expose the legacy `protocol` and `ports` fields, and the REST API still accepts them on write as an alternative to `port_mappings`. They are populated for single-protocol services; a service with multiple protocols cannot be represented in the legacy format and returns `null` for both, while a service with no mappings returns `protocol: null` and `ports: []`. In other words, `ports: null` specifically signals "multiple protocols — read `port_mappings` instead." **These legacy fields are deprecated and will be removed in NetBox v5.0; use `port_mappings` instead.**

    On write, `port_mappings` and the legacy `protocol`/`ports` fields may be submitted together only when they agree — as in a full-object round-trip that echoes back a read. A request whose legacy fields contradict `port_mappings` (for example, an edited `port_mappings` sent alongside the stale `protocol`/`ports` from the original read) is rejected as ambiguous; send `port_mappings` alone, or keep the legacy fields consistent with it.

!!! warning "GraphQL filter change in NetBox v4.7"

    The GraphQL filters for `Service` and `ServiceTemplate` have changed shape. The former `protocol` lookup and `ports` integer lookup (which supported `exact`/`gt`/`lt`/`range`/etc.) are replaced by `protocol` and `port`, each accepting a list of values — for example `filters: {protocol: [TCP], port: [80]}`. When both are supplied, a service matches only if a single mapping satisfies both. Existing GraphQL queries using the old `ports` filter or its range/comparison lookups must be updated.

!!! warning "REST filter change in NetBox v4.7"

    Because `protocol` and `port` are now filtered against the `port_mappings` array rather than dedicated model fields, the character-based lookup variants previously auto-generated for the `protocol` field — `protocol__n`, `protocol__ic`, `protocol__nic`, `protocol__empty`, etc. — are no longer available. Filter on `protocol` and `port` directly (both accept multiple values, e.g. `?protocol=tcp&port=80`). As with any unrecognized query parameter, the REST API silently ignores a removed lookup rather than raising an error, so update any saved filters or scripts that relied on them.

### IP Addresses

The [IP address(es)](./ipaddress.md) to which this service is bound. If no IP addresses are bound, the service is assumed to be reachable via any assigned IP address.

## Bulk Import (CSV)

When importing application services or [application service templates](./servicetemplate.md) via CSV, all port mappings for a row are given in a single `port_mappings` column as a comma-separated list of `protocol/port` pairs enclosed in double quotes. For example, `"tcp/80,tcp/443,udp/53"`. Protocols may be specified in any case.
