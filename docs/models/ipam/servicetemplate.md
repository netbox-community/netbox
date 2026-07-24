# Application Service Templates

Application service templates can be used to instantiate [application services](./service.md) on [devices](../dcim/device.md) and [virtual machines](../virtualization/virtualmachine.md).

!!! note "Changed in NetBox v4.4"

    Previously, application service templates were referred to simply as "service templates". The name has been changed in the UI to better reflect their intended use. There is no change to the name of the model or in any programmatic NetBox APIs.

## Fields

### Name

A service or protocol name.

### Port Mappings

The protocols and ports on which the service runs. The same port may be exposed on multiple protocols. In the UI, ports for a given protocol may be entered together using commas and/or hyphens (e.g. `80,8001-8003`).

In the REST and GraphQL APIs, port mappings are represented as a list of `{protocol, ports}` objects — one entry per protocol:

```json
[
  {"protocol": "tcp", "ports": [80, 443]},
  {"protocol": "udp", "ports": [53]}
]
```

!!! note "Changed in NetBox v4.7"

    The single-protocol `protocol` and `ports` fields have been replaced by the unified `port_mappings` field (which supports multiple protocols per template, in the grouped form shown above). For backward compatibility, the REST and GraphQL APIs still expose the legacy `protocol` and `ports` fields, and the REST API still accepts them on write as an alternative to `port_mappings`. They are populated for single-protocol templates; a template with multiple protocols cannot be represented in the legacy format and returns `null` for both, while a template with no mappings returns `protocol: null` and `ports: []`. In other words, `ports: null` specifically signals "multiple protocols — read `port_mappings` instead." **These legacy fields are deprecated and will be removed in a future release; use `port_mappings` instead.**

## Bulk Import (CSV)

When importing services or service templates via CSV, all port mappings for a row are given in a single `port_mappings` column, formatted as `protocol:ports` pairs separated by semicolons (ports within a pair use the same comma/hyphen syntax). For example, `tcp:80,443;udp:53`.
