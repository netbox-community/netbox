# Application Services

An application service represents a layer seven application available on a device or virtual machine. For example, a service might be created in NetBox to represent an HTTP server running on TCP/8000. Each service may optionally be further bound to one or more specific interfaces assigned to the selected device or virtual machine.

To aid in the efficient creation of application services, users may opt to first create an [application service template](./servicetemplate.md) from which service definitions can be quickly replicated.

!!! note "Naming"
    Application services are referred to simply as "services" in the name of the model and throughout NetBox's programmatic APIs. Only the UI uses the longer name, which better reflects their intended use.

## Fields

### Parent

The parent object to which the application service is assigned. This must be one of [Device](../dcim/device.md),
[VirtualMachine](../virtualization/virtualmachine.md), or [FHRP Group](./fhrpgroup.md).

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

    At the ORM level (custom scripts and plugins), `protocol` and `ports` are now **read-only** properties derived from `port_mappings`. Assign `port_mappings` directly — e.g. `Service(parent=device, name='http', port_mappings=['tcp/80'])` — since passing `protocol=`/`ports=` to the model raises `TypeError` and setting `service.ports = [...]` raises `AttributeError`.

### Filtering by Port Mapping, Protocol, and Port

`port_mappings`, `protocol`, and `port` are all filtered against the `port_mappings` array. Each accepts multiple values (matching any of them), and `port` supports the usual numeric lookups:

| Parameter | Matches services having a mapping… |
|---|---|
| `?port_mappings=tcp/80` | that is exactly `tcp/80` |
| `?port_mappings__n=tcp/80` | *(negated)* that is exactly `tcp/80` |
| `?protocol=tcp` | whose protocol is TCP |
| `?protocol__n=tcp` | *(negated)* whose protocol is TCP |
| `?port=80` | whose port is 80 |
| `?port__n=80` | *(negated)* whose port is 80 |
| `?port__gt=` / `?port__gte=` / `?port__lt=` / `?port__lte=` | whose port is above/below the given value |

`port_mappings` is the most direct way to ask "which services expose this exact protocol and port?" — `?port_mappings=tcp/80` will not match a service that exposes only `udp/80`. Protocols may be given in any case, and leading zeros are ignored, so `?port_mappings=TCP/080` finds `tcp/80`. A value naming an unknown protocol or a malformed pair simply matches nothing rather than returning an error.

When `protocol` and one or more `port` lookups are combined, they must all be satisfied by a **single** mapping. So `?protocol=tcp&port__gt=1000` does not match a service whose only TCP mapping is `tcp/80` (even if it also exposes `udp/9999`), and `?port__gte=1000&port__lte=2000` does not match a service exposing only ports 500 and 5000. Each `port_mappings` value already names one complete pair, so it needs no such correlation and is simply combined with the other parameters.

All of these parameters are available as GraphQL filters too, under the same names — `port_mappings`, `protocol`, `port`, `port__gt`, `port__gte`, `port__lt`, `port__lte` — each accepting a list of values. For example, `filters: {port_mappings: ["tcp/80"]}` or `filters: {protocol: [TCP], port__gt: [1000]}`. The single-mapping correlation rule described above applies identically.

!!! warning "GraphQL filter change in NetBox v4.7"

    The GraphQL filters for `Service` and `ServiceTemplate` have changed shape. The former `protocol` lookup and `ports` integer lookup (which nested their comparisons, e.g. `ports: {gt: 1000}`) are replaced by the flat `protocol`, `port`, `port__gt`, `port__gte`, `port__lt`, `port__lte`, and `port_mappings` parameters, each accepting a list of values and spelled the same way as the corresponding REST query parameter. Rewrite `ports: {gt: 1000}` as `port__gt: [1000]`, and `ports: {exact: 80}` as `port: [80]`. The `range` and `i_exact` lookups previously offered by the integer lookup have no direct equivalent; express a range as `port__gte`/`port__lte`, which — unlike the old lookup — requires a single mapping to satisfy both bounds.

    The members of the `ServiceProtocolEnum` used by the `protocol` filter have also been renamed to drop a spurious `ROLE_` prefix: `ROLE_TCP`, `ROLE_UDP`, and `ROLE_SCTP` are now `TCP`, `UDP`, and `SCTP`.

!!! warning "REST filter change in NetBox v4.7"

    Because `protocol` is now filtered against the `port_mappings` array rather than a dedicated model field, the character-based lookup variants previously auto-generated for it — `protocol__ic`, `protocol__nic`, `protocol__isw`, `protocol__empty`, etc. — are no longer available; `protocol` and `protocol__n` remain. The `port__empty` lookup is likewise gone, as a service always has at least one port mapping. As with any unrecognized query parameter, the REST API silently ignores a removed lookup rather than raising an error, so update any saved filters or scripts that relied on them.

### IP Addresses

The [IP address(es)](./ipaddress.md) to which this service is bound. If no IP addresses are bound, the service is assumed to be reachable via any assigned IP address.

## Bulk Import (CSV)

When importing application services or [application service templates](./servicetemplate.md) via CSV, all port mappings for a row are given in a single `port_mappings` column as a comma-separated list of `protocol/port` pairs enclosed in double quotes. For example, `"tcp/80,tcp/443,udp/53"`. A pair's port may be given as a hyphen range, for example `"tcp/8000-8010"`. Protocols may be entered in uppercase or lowercase.
