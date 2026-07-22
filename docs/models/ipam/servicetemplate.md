# Application Service Templates

Application service templates can be used to instantiate [application services](./service.md) on [devices](../dcim/device.md) and [virtual machines](../virtualization/virtualmachine.md).

!!! note "Changed in NetBox v4.4"

    Previously, application service templates were referred to simply as "service templates". The name has been changed in the UI to better reflect their intended use. There is no change to the name of the model or in any programmatic NetBox APIs.

## Fields

### Name

A service or protocol name.

### Port Mappings

The protocol/port pairs on which the service runs, stored as a list of `protocol/port` values (e.g. `tcp/80`, `tcp/443`, `udp/53`). Each pair uses a wire protocol (UDP, TCP, or SCTP) and a port number. The same port may be exposed on multiple protocols. In the UI, ports for a given protocol may be entered together using commas and/or hyphens (e.g. `80,8001-8003`).

!!! note "Changed in NetBox v4.7"

    The single-protocol `protocol` and `ports` fields have been replaced by the unified `port_mappings` field. For backward compatibility, the REST API continues to accept the legacy `protocol` and `ports` fields on write and to return them for templates that use a single protocol. A template that exposes multiple protocols cannot be represented in the legacy format, so both fields are returned as `null`; a template with no mappings returns `protocol: null` and `ports: []`. In other words, `ports: null` specifically signals "multiple protocols — read `port_mappings` instead." **These legacy fields are deprecated and will be removed in a future release; use `port_mappings` instead.**

## Bulk Import (CSV)

When importing services or service templates via CSV, all port mappings for a row are given in a single `port_mappings` column, formatted as `protocol:ports` pairs separated by semicolons (ports within a pair use the same comma/hyphen syntax). For example, `tcp:80,443;udp:53`.
