# NetBox Models

## Model Types

A NetBox model represents a discrete object type such as a device or IP address. Each model is defined as a Python class and has its own SQL table. All NetBox data models can be categorized by type.

The Django [content types](https://docs.djangoproject.com/en/stable/ref/contrib/contenttypes/) framework can be used to reference models within the database. A ContentType instance references a model by its `app_label` and `name`: For example, the Site model is referred to as `dcim.site`. The content type combined with an object's primary key form a globally unique identifier for the object (e.g. `dcim.site:123`).

### Features Matrix

* [Change logging](../additional-features/change-logging.md) - Changes to these objects are automatically recorded in the change log
* [Webhooks](../additional-features/webhooks.md) - NetBox is capable of generating outgoing webhooks for these objects
* [Custom fields](../customization/custom-fields.md) - These models support the addition of user-defined fields
* [Export templates](../customization/export-templates.md) - Users can create custom export templates for these models
* [Tagging](../models/extras/tag.md) - The models can be tagged with user-defined tags
* [Journaling](../additional-features/journaling.md) - These models support persistent historical commentary
* Nesting - These models can be nested recursively to create a hierarchy

| Type               | Change Logging   | Webhooks         | Custom Fields    | Export Templates | Tags             | Journaling       | Nesting          |
| ------------------ | ---------------- | ---------------- | ---------------- | ---------------- | ---------------- | ---------------- | ---------------- |
| Primary            | :material-check: | :material-check: | :material-check: | :material-check: | :material-check: | :material-check: |                  |
| Organizational     | :material-check: | :material-check: | :material-check: | :material-check: |                  |                  |                  |
| Nested Group       | :material-check: | :material-check: | :material-check: | :material-check: |                  |                  | :material-check: |
| Component          | :material-check: | :material-check: | :material-check: | :material-check: | :material-check: |                  |                  |
| Component Template | :material-check: | :material-check: | :material-check: |                  |                  |                  |                  |

## Models Index

### Primary Models

* [circuits.Circuit](../models/circuits/circuit.md)
* [circuits.Provider](../models/circuits/provider.md)
* [circuits.ProviderNetwork](../models/circuits/providernetwork.md)
* [dcim.Cable](../models/dcim/cable.md)
* [dcim.Device](../models/dcim/device.md)
* [dcim.DeviceType](../models/dcim/devicetype.md)
* [dcim.PowerFeed](../models/dcim/powerfeed.md)
* [dcim.PowerPanel](../models/dcim/powerpanel.md)
* [dcim.Rack](../models/dcim/rack.md)
* [dcim.RackReservation](../models/dcim/rackreservation.md)
* [dcim.Site](../models/dcim/site.md)
* [dcim.VirtualChassis](../models/dcim/virtualchassis.md)
* [ipam.Aggregate](../models/ipam/aggregate.md)
* [ipam.IPAddress](../models/ipam/ipaddress.md)
* [ipam.Prefix](../models/ipam/prefix.md)
* [ipam.RouteTarget](../models/ipam/routetarget.md)
* [ipam.Service](../models/ipam/service.md)
* [ipam.VLAN](../models/ipam/vlan.md)
* [ipam.VRF](../models/ipam/vrf.md)
* [tenancy.Tenant](../models/tenancy/tenant.md)
* [virtualization.Cluster](../models/virtualization/cluster.md)
* [virtualization.VirtualMachine](../models/virtualization/virtualmachine.md)

### Organizational Models

* [circuits.CircuitType](../models/circuits/circuittype.md)
* [dcim.DeviceRole](../models/dcim/devicerole.md)
* [dcim.Manufacturer](../models/dcim/manufacturer.md)
* [dcim.Platform](../models/dcim/platform.md)
* [dcim.RackRole](../models/dcim/rackrole.md)
* [ipam.RIR](../models/ipam/rir.md)
* [ipam.Role](../models/ipam/role.md)
* [ipam.VLANGroup](../models/ipam/vlangroup.md)
* [virtualization.ClusterGroup](../models/virtualization/clustergroup.md)
* [virtualization.ClusterType](../models/virtualization/clustertype.md)

### Nested Group Models

* [dcim.Location](../models/dcim/location.md) (formerly RackGroup)
* [dcim.Region](../models/dcim/region.md)
* [dcim.SiteGroup](../models/dcim/sitegroup.md)
* [tenancy.TenantGroup](../models/tenancy/tenantgroup.md)

### Component Models

* [dcim.ConsolePort](../models/dcim/consoleport.md)
* [dcim.ConsoleServerPort](../models/dcim/consoleserverport.md)
* [dcim.DeviceBay](../models/dcim/devicebay.md)
* [dcim.FrontPort](../models/dcim/frontport.md)
* [dcim.Interface](../models/dcim/interface.md)
* [dcim.InventoryItem](../models/dcim/inventoryitem.md)
* [dcim.PowerOutlet](../models/dcim/poweroutlet.md)
* [dcim.PowerPort](../models/dcim/powerport.md)
* [dcim.RearPort](../models/dcim/rearport.md)
* [virtualization.VMInterface](../models/virtualization/vminterface.md)

### Component Template Models

* [dcim.ConsolePortTemplate](../models/dcim/consoleporttemplate.md)
* [dcim.ConsoleServerPortTemplate](../models/dcim/consoleserverporttemplate.md)
* [dcim.DeviceBayTemplate](../models/dcim/devicebaytemplate.md)
* [dcim.FrontPortTemplate](../models/dcim/frontporttemplate.md)
* [dcim.InterfaceTemplate](../models/dcim/interfacetemplate.md)
* [dcim.PowerOutletTemplate](../models/dcim/poweroutlettemplate.md)
* [dcim.PowerPortTemplate](../models/dcim/powerporttemplate.md)
* [dcim.RearPortTemplate](../models/dcim/rearporttemplate.md)
