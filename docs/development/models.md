# NetBox Models

## Model Types

A NetBox model represents a discrete object type such as a device or IP address. Per [Django convention](https://docs.djangoproject.com/en/stable/topics/db/models/), each model is defined as a Python class and has its own table in the PostgreSQL database. All NetBox data models can be categorized by type.

The Django [content types](https://docs.djangoproject.com/en/stable/ref/contrib/contenttypes/) framework is used to map Django models to database tables. A ContentType instance references a model by its `app_label` and `name`: For example, the Site model within the DCIM app is referred to as `dcim.site`. The content type combined with an object's primary key form a globally unique identifier for the object (e.g. `dcim.site:123`).

### Features Matrix

Depending on its classification, each NetBox model may support various features which enhance its operation. Each feature is enabled by inheriting from its designated mixin class, and some features also make use of the [application registry](./application-registry.md#model_features).

| Feature                                                    | Feature Mixin           | Registry Key       | Description                                                                             |
|------------------------------------------------------------|-------------------------|--------------------|-----------------------------------------------------------------------------------------|
| [Change logging](../features/change-logging.md)            | `ChangeLoggingMixin`    | -                  | Changes to these objects are automatically recorded in the change log                   |
| Cloning                                                    | `CloningMixin`          | -                  | Provides the `clone()` method to prepare a copy                                         |
| [Custom fields](../customization/custom-fields.md)         | `CustomFieldsMixin`     | `custom_fields`    | These models support the addition of user-defined fields                                |
| [Custom links](../customization/custom-links.md)           | `CustomLinksMixin`      | `custom_links`     | These models support the assignment of custom links                                     |
| [Custom validation](../customization/custom-validation.md) | `CustomValidationMixin` | -                  | Supports the enforcement of custom validation rules                                     |
| [Export templates](../customization/export-templates.md)   | `ExportTemplatesMixin`  | `export_templates` | Users can create custom export templates for these models                               |
| [Job results](../features/background-jobs.md)              | `JobsMixin`             | `jobs`             | Background jobs can be scheduled for these models                                       |
| [Journaling](../features/journaling.md)                    | `JournalingMixin`       | `journaling`       | These models support persistent historical commentary                                   |
| [Synchronized data](../integrations/synchronized-data.md)  | `SyncedDataMixin`       | `synced_data`      | Certain model data can be automatically synchronized from a remote data source          |
| [Tagging](../models/extras/tag.md)                         | `TagsMixin`             | `tags`             | The models can be tagged with user-defined tags                                         |
| [Event rules](../features/event-rules.md)                  | `EventRulesMixin`       | `event_rules`      | Event rules can send webhooks or run custom scripts automatically in response to events |

## Models Index

### Primary Models

These are considered the "core" application models which are used to model network infrastructure.

* [circuits.Circuit](../models/circuits/circuit.md)
* [circuits.Provider](../models/circuits/provider.md)
* [circuits.ProviderAccount](../models/circuits/provideraccount.md)
* [circuits.ProviderNetwork](../models/circuits/providernetwork.md)
* [core.DataSource](../models/core/datasource.md)
* [dcim.Cable](../models/dcim/cable.md)
* [dcim.Device](../models/dcim/device.md)
* [dcim.DeviceType](../models/dcim/devicetype.md)
* [dcim.Module](../models/dcim/module.md)
* [dcim.ModuleType](../models/dcim/moduletype.md)
* [dcim.PowerFeed](../models/dcim/powerfeed.md)
* [dcim.PowerPanel](../models/dcim/powerpanel.md)
* [dcim.Rack](../models/dcim/rack.md)
* [dcim.RackReservation](../models/dcim/rackreservation.md)
* [dcim.Site](../models/dcim/site.md)
* [dcim.VirtualChassis](../models/dcim/virtualchassis.md)
* [dcim.VirtualDeviceContext](../models/dcim/virtualdevicecontext.md)
* [ipam.Aggregate](../models/ipam/aggregate.md)
* [ipam.ASN](../models/ipam/asn.md)
* [ipam.FHRPGroup](../models/ipam/fhrpgroup.md)
* [ipam.IPAddress](../models/ipam/ipaddress.md)
* [ipam.IPRange](../models/ipam/iprange.md)
* [ipam.Prefix](../models/ipam/prefix.md)
* [ipam.RouteTarget](../models/ipam/routetarget.md)
* [ipam.Service](../models/ipam/service.md)
* [ipam.ServiceTemplate](../models/ipam/servicetemplate.md)
* [ipam.VLAN](../models/ipam/vlan.md)
* [ipam.VRF](../models/ipam/vrf.md)
* [tenancy.Contact](../models/tenancy/contact.md)
* [tenancy.Tenant](../models/tenancy/tenant.md)
* [virtualization.Cluster](../models/virtualization/cluster.md)
* [virtualization.VirtualMachine](../models/virtualization/virtualmachine.md)
* [vpn.IKEPolicy](../models/vpn/ikepolicy.md)
* [vpn.IKEProposal](../models/vpn/ikeproposal.md)
* [vpn.IPSecPolicy](../models/vpn/ipsecpolicy.md)
* [vpn.IPSecProfile](../models/vpn/ipsecprofile.md)
* [vpn.IPSecProposal](../models/vpn/ipsecproposal.md)
* [vpn.L2VPN](../models/vpn/l2vpn.md)
* [vpn.Tunnel](../models/vpn/tunnel.md)
* [wireless.WirelessLAN](../models/wireless/wirelesslan.md)
* [wireless.WirelessLink](../models/wireless/wirelesslink.md)

### Organizational Models

Organization models are used to organize and classify primary models.

* [circuits.CircuitType](../models/circuits/circuittype.md)
* [dcim.DeviceRole](../models/dcim/devicerole.md)
* [dcim.Manufacturer](../models/dcim/manufacturer.md)
* [dcim.Platform](../models/dcim/platform.md)
* [dcim.RackRole](../models/dcim/rackrole.md)
* [ipam.ASNRange](../models/ipam/asnrange.md)
* [ipam.RIR](../models/ipam/rir.md)
* [ipam.Role](../models/ipam/role.md)
* [ipam.VLANGroup](../models/ipam/vlangroup.md)
* [tenancy.ContactRole](../models/tenancy/contactrole.md)
* [virtualization.ClusterGroup](../models/virtualization/clustergroup.md)
* [virtualization.ClusterType](../models/virtualization/clustertype.md)

### Nested Group Models

Nested group models behave like organizational model, but self-nest within a recursive hierarchy. For example, the Region model can be used to represent a hierarchy of countries, states, and cities.

* [dcim.Location](../models/dcim/location.md) (formerly RackGroup)
* [dcim.Region](../models/dcim/region.md)
* [dcim.SiteGroup](../models/dcim/sitegroup.md)
* [tenancy.ContactGroup](../models/tenancy/contactgroup.md)
* [tenancy.TenantGroup](../models/tenancy/tenantgroup.md)
* [wireless.WirelessLANGroup](../models/wireless/wirelesslangroup.md)

### Component Models

Component models represent individual physical or virtual components belonging to a device or virtual machine.

* [dcim.ConsolePort](../models/dcim/consoleport.md)
* [dcim.ConsoleServerPort](../models/dcim/consoleserverport.md)
* [dcim.DeviceBay](../models/dcim/devicebay.md)
* [dcim.FrontPort](../models/dcim/frontport.md)
* [dcim.Interface](../models/dcim/interface.md)
* [dcim.InventoryItem](../models/dcim/inventoryitem.md)
* [dcim.ModuleBay](../models/dcim/modulebay.md)
* [dcim.PowerOutlet](../models/dcim/poweroutlet.md)
* [dcim.PowerPort](../models/dcim/powerport.md)
* [dcim.RearPort](../models/dcim/rearport.md)
* [virtualization.VirtualDisk](../models/virtualization/virtualdisk.md)
* [virtualization.VMInterface](../models/virtualization/vminterface.md)

### Component Template Models

These function as templates to effect the replication of device and virtual machine components. Component template models support a limited feature set, including change logging, custom validation, and event rules.

* [dcim.ConsolePortTemplate](../models/dcim/consoleporttemplate.md)
* [dcim.ConsoleServerPortTemplate](../models/dcim/consoleserverporttemplate.md)
* [dcim.DeviceBayTemplate](../models/dcim/devicebaytemplate.md)
* [dcim.FrontPortTemplate](../models/dcim/frontporttemplate.md)
* [dcim.InterfaceTemplate](../models/dcim/interfacetemplate.md)
* [dcim.InventoryItemTemplate](../models/dcim/inventoryitemtemplate.md)
* [dcim.ModuleBayTemplate](../models/dcim/modulebaytemplate.md)
* [dcim.PowerOutletTemplate](../models/dcim/poweroutlettemplate.md)
* [dcim.PowerPortTemplate](../models/dcim/powerporttemplate.md)
* [dcim.RearPortTemplate](../models/dcim/rearporttemplate.md)
