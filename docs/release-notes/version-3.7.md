## v3.7-beta1 (2023-12-05)

### Breaking Changes

* The following fields have been removed from the Webhook model: `content_types`, `type_create`, `type_update`, `type_delete`, `type_job_start`, `type_job_end`, `enabled`, and `conditions`. Webhooks are now tied to events via [event rules](../features/event-rules.md). Existing webhooks will have event rules created automatically upon upgrade.
* The `ui_visibility` field on the [custom field model](../models/extras/customfield.md) has been replaced with two new fields: `ui_visible` and `ui_editable`. Existing values will be migrated automatically upon upgrade.
* The `FeatureQuery` class for querying content types by model feature has been removed. Plugins should now use the new `with_feature()` manager method on NetBox's proxy model for ContentType.
* The ConfigRevision model has been moved from `extras` to `core`. Configuration history will be retained throughout the upgrade process.
* The L2VPN and L2VPNTermination models have been moved from the `ipam` app to the new `vpn` app. All object data will be retained, however please note that the relevant API endpoints have moved to `/api/vpn/`.
* The `CustomFieldsMixin`, `SavedFiltersMixin`, and `TagsMixin` classes have moved from the `extras.forms.mixins` module to `netbox.forms.mixins`.

### New Features

#### VPN Tunnels ([#9816](https://github.com/netbox-community/netbox/issues/9816))

Several new models have been introduced to enable [VPN tunnel management](../features/vpn-tunnels.md). Users can now define tunnels with two or more terminations to replicate peer-to-peer or hub-and-spoke topologies. Each termination is made to a virtual interface on a device or VM. Additionally, users can define IKE and IPSec policies which can be applied to tunnels to document encryption and authentication strategies.

#### Event Rules ([#14132](https://github.com/netbox-community/netbox/issues/14132))

This release introduces [event rules](../features/event-rules.md), which can be used to send webhooks or execute custom scripts automatically in response to NetBox events. For example, it's now possible to run a custom script whenever a new site is created with a particular status or tag.

Event rules replace and extend functionality that was previously built into the webhook model. Event rules will be created for any existing webhooks upon upgrade.

#### Virtual Machine Disks ([#8356](https://github.com/netbox-community/netbox/issues/8356))

A new [VirtualDisk](../models/virtualization/virtualdisk.md) model has been introduced to enable tracking the assignment of discrete virtual disks to virtual machines. The original `size` field has been retained on the VirtualMachine model, and will be automatically updated with the aggregate size of all assigned virtual disks. (Users who opt to eschew the new model may continue using the VirtualMachine `size` attribute as before.)

#### Object Protection Rules ([#10244](https://github.com/netbox-community/netbox/issues/10244))

A new [`PROTECTION_RULES`](../configuration/data-validation.md#protection_rules) configuration parameter is now available. Similar to how [custom validation rules](../customization/custom-validation.md) can be used to enforce certain values for object attributes, protection rules guard against the deletion of objects which do not meet specified criteria. This enables an administrator to prevent, for example, the deletion of a site which has a status of "active."

#### Improved Custom Field Visibility Controls ([#13299](https://github.com/netbox-community/netbox/issues/13299))

The old `ui_visible` field on the custom field model](../models/extras/customfield.md) has been replaced by two new fields, `ui_visible` and `ui_editable`, which control how and whether a custom field is displayed when view and editing an object, respectively. Separating these two functions into discrete fields enables more control over how each custom field is presented to users. The values of these fields will be appropriately set automatically during the upgrade process depending on the value of the original field.

#### Improved Global Search Results ([#14134](https://github.com/netbox-community/netbox/issues/14134))

Global search results now include additional context about each object, such as a description, status, and/or related objects. The set of attributes to be displayed is specific to each object type, and is defined by setting `display_attrs` under the object's [SearchIndex class](../plugins/development/search.md#netbox.search.SearchIndex).

#### Table Column Registration for Plugins ([#14173](https://github.com/netbox-community/netbox/issues/14173))

Plugins can now [register their own custom columns](../plugins/development/tables.md#extending-core-tables) for inclusion on core NetBox tables. For example, a plugin can register a new column on SiteTable using the new `register_table_column()` utility function, and it will become available for users to select for display.

#### Data Backend Registration for Plugins ([#13381](https://github.com/netbox-community/netbox/issues/13381))

Plugins can now [register their own data backends](../plugins/development/data-backends.md) for use with [synchronized data sources](../features/synchronized-data.md). This enables plugins to introduce new backends in addition to the git, S3, and local path backends provided natively.

### Enhancements

* [#12135](https://github.com/netbox-community/netbox/issues/12135) - Avoid orphaned interfaces by preventing the deletion of interfaces which have children assigned
* [#12216](https://github.com/netbox-community/netbox/issues/12216) - Add a `color` field for circuit types
* [#13230](https://github.com/netbox-community/netbox/issues/13230) - Allow device types to be excluded from consideration when calculating a rack's utilization
* [#13334](https://github.com/netbox-community/netbox/issues/13334) - Added an `error` field to the Job model to record any errors associated with its execution
* [#13427](https://github.com/netbox-community/netbox/issues/13427) - Introduced a mechanism for omitting models from general-purpose lists of object types
* [#13690](https://github.com/netbox-community/netbox/issues/13690) - Display any dependent objects to be deleted prior to deleting an object via the web UI
* [#13794](https://github.com/netbox-community/netbox/issues/13794) - Any models with a relationship to Tenant are now included automatically in the list of related objects under the tenant view
* [#13808](https://github.com/netbox-community/netbox/issues/13808) - Added a `/render-config` REST API endpoint for virtual machines
* [#14035](https://github.com/netbox-community/netbox/issues/14035) - Order objects of equivalent weight by value in global search results to improve readability
* [#14156](https://github.com/netbox-community/netbox/issues/14156) - Enable custom fields for contact assignments
* [#14361](https://github.com/netbox-community/netbox/issues/14361) - Add a `description` field for webhooks
* [#14365](https://github.com/netbox-community/netbox/issues/14365) - Introduced `job_start` and `job_end` signals

### Other Changes

* [#13550](https://github.com/netbox-community/netbox/issues/13550) - Optimized the format for declaring view actions under `ActionsMixin` (backward compatibility has been retained)
* [#13645](https://github.com/netbox-community/netbox/issues/13645) - Installation of the `sentry-sdk` Python library is now required only if Sentry reporting is enabled
* [#14036](https://github.com/netbox-community/netbox/issues/14036) - Move plugin resources from the `extras` app into `netbox` (backward compatibility has been retained)
* [#14153](https://github.com/netbox-community/netbox/issues/14153) - Replace `FeatureQuery` with new `with_feature()` method on ContentType manager
* [#14311](https://github.com/netbox-community/netbox/issues/14311) - Move the L2VPN models from the `ipam` app to the new `vpn` app
* [#14312](https://github.com/netbox-community/netbox/issues/14312) - Move the ConfigRevision model from the `extras` app to `core`
* [#14326](https://github.com/netbox-community/netbox/issues/14326) - Form feature mixin classes have been moved from the `extras` app to `netbox`
* [#14395](https://github.com/netbox-community/netbox/issues/14395) - Moved `extras.webhooks_worker.process_webhook()` to `extras.webhooks.send_webhook()` (backward compatibility has been retained)

### REST API Changes

* Introduced the following endpoints:
    * `/api/extras/event-rules/`
    * `/api/virtualization/virtual-disks/`
    * `/api/vpn/ike-policies/`
    * `/api/vpn/ike-proposals/`
    * `/api/vpn/ipsec-policies/`
    * `/api/vpn/ipsec-profiles/`
    * `/api/vpn/ipsec-proposals/`
    * `/api/vpn/tunnels/`
    * `/api/vpn/tunnel-terminations/`
* The following endpoints have been moved:
    * `/api/ipam/l2vpns/` -> `/api/vpn/l2vpns/`
    * `/api/ipam/l2vpn-terminations/` -> `/api/vpn/l2vpn-terminations/`
* circuits.CircuitType
    * Added the optional `color` choice field
* core.Job
    * Added the read-only `error` character field
* extras.Webhook
    * Removed the following fields: `content_types`, `type_create`, `type_update`, `type_delete`, `type_job_start`, `type_job_end`, `enabled`, and `conditions` (these have been moved to the new `EventRule` model)
    * Add the optional `description` field
* dcim.DeviceType
    * Added the `exclude_from_utilization` boolean field
* extras.CustomField
    * Removed the `ui_visibility` field
    * Added the `ui_visible` and `ui_editable` choice fields
* tenancy.ContactAssignment
    * Added support for custom fields
* virtualization.VirtualDisk
    * Added the read-only `virtual_disk_count` integer field
* virtualization.VirtualMachine
    * Added the `/render-config` endpoint
