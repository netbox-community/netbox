# Application Service Templates

Application service templates can be used to instantiate [application services](./service.md) on [devices](../dcim/device.md) and [virtual machines](../virtualization/virtualmachine.md).

!!! note "Naming"

    Application service templates are referred to simply as "service templates" in the name of the model and throughout NetBox's programmatic APIs. Only the UI uses the longer name, which better reflects their intended use.

## Fields

### Name

A service or protocol name.

### Port Mappings

The protocols and ports on which the service runs. See [Port Mappings](./service.md#port-mappings) on the application service model for details.

## Bulk Import (CSV)

Application service templates are imported via CSV using the same `port_mappings` column format as application services. See [Bulk Import (CSV)](./service.md#bulk-import-csv) on the application service model for details.
