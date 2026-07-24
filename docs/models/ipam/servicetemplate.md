# Application Service Templates

Application service templates can be used to instantiate [application services](./service.md) on [devices](../dcim/device.md) and [virtual machines](../virtualization/virtualmachine.md).

!!! note "Changed in NetBox v4.4"

    Previously, application service templates were referred to simply as "service templates". The name has been changed in the UI to better reflect their intended use. There is no change to the name of the model or in any programmatic NetBox APIs.

## Fields

### Name

A service or protocol name.

### Port Mappings

The protocols and ports on which the service runs. See [Port Mappings](./service.md#port-mappings) on the application service model for details.

## Bulk Import (CSV)

When importing services or service templates via CSV, all port mappings for a row are given in a single `port_mappings` column, formatted as `protocol:ports` pairs separated by semicolons (ports within a pair use the same comma/hyphen syntax). For example, `tcp:80,443;udp:53`.
