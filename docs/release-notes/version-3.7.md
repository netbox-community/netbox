# NetBox v3.7

## v3.7.5 (FUTURE)

### Bug Fixes

* [#14799](https://github.com/netbox-community/netbox/issues/14799) - Avoid caching modified reports & scripts
* [#15029](https://github.com/netbox-community/netbox/issues/15029) - Raise a clean validation error when attempting to make duplicate FHRP group assignments
* [#15102](https://github.com/netbox-community/netbox/issues/15102) - Fix usage of selector widget for form fields referencing users/groups
* [#15435](https://github.com/netbox-community/netbox/issues/15435) - Correct permissions name to allow adding a module bay to a device via the UI
* [#15502](https://github.com/netbox-community/netbox/issues/15502) - Fix KeyError exception when modifying an IP address assigned to a virtual machine
* [#15597](https://github.com/netbox-community/netbox/issues/15597) - Restore help modal for `button_class` field on custom link bulk import form

---

## v3.7.4 (2024-03-13)

### Enhancements

* [#14206](https://github.com/netbox-community/netbox/issues/14206) - Add additional FibreChannel SFP+ interface types
* [#14366](https://github.com/netbox-community/netbox/issues/14366) - Enable custom links for config contexts & templates
* [#15291](https://github.com/netbox-community/netbox/issues/15291) - Add tunnel termination buttons to VM interfaces table
* [#15297](https://github.com/netbox-community/netbox/issues/15297) - Linkify platform column in device & virtual machine tables

### Bug Fixes

* [#13722](https://github.com/netbox-community/netbox/issues/13722) - Fix range expansion for comma-separated numerical values
* [#14832](https://github.com/netbox-community/netbox/issues/14832) - Enable querying IP addresses for an FHRP group via GraphQL
* [#15220](https://github.com/netbox-community/netbox/issues/15220) - Fix validation check when bulk editing the mask length of IP addresses
* [#15232](https://github.com/netbox-community/netbox/issues/15232) - Permit user with sufficient permissions to assign an inventory item to a device type
* [#15241](https://github.com/netbox-community/netbox/issues/15241) - Restore missing `display` field on VirtualDisk serialization in REST API
* [#15243](https://github.com/netbox-community/netbox/issues/15243) - Correct representation of installed module when listing module bays using REST API brief mode
* [#15316](https://github.com/netbox-community/netbox/issues/15316) - Fix selection of 3DES encryption for IKE & IPSec proposals
* [#15322](https://github.com/netbox-community/netbox/issues/15322) - Add description field to YAML export for device & module types
* [#15336](https://github.com/netbox-community/netbox/issues/15336) - Correct label for recurring scheduled jobs
* [#15347](https://github.com/netbox-community/netbox/issues/15347) - Fix querying virtual machine contacts via GraphQL
* [#15356](https://github.com/netbox-community/netbox/issues/15356) - Fix assignment of front & rear images to device types via REST API

---

## v3.7.3 (2024-02-21)

### Enhancements

* [#14587](https://github.com/netbox-community/netbox/issues/14587) - Display a human-friendly name for the OpenID Connect remote auth backend
* [#14946](https://github.com/netbox-community/netbox/issues/14946) - Remove `associate_by_email()` from default social auth pipeline
* [#14966](https://github.com/netbox-community/netbox/issues/14966) - Add PostgreSQL index for object type & ID on CachedValue table to improve performance
* [#15177](https://github.com/netbox-community/netbox/issues/15177) - Add "last login" time to user display & REST API serializer

### Bug Fixes

* [#14058](https://github.com/netbox-community/netbox/issues/14058) - Limit platform options by manufacturer when editing a device or device type
* [#14064](https://github.com/netbox-community/netbox/issues/14064) - Resolving parent location should consider assigned site when bulk importing locations
* [#14079](https://github.com/netbox-community/netbox/issues/14079) - Ensure changes are logged on related objects when deleting an object referenced via a many-to-many relationship (e.g. tags)
* [#14405](https://github.com/netbox-community/netbox/issues/14405) - Clean up formatting of link peers in bulk CSV export of cable termination objects
* [#14689](https://github.com/netbox-community/netbox/issues/14689) - Preserve "empty" default values for JSON custom fields
* [#14952](https://github.com/netbox-community/netbox/issues/14952) - Update existing AutoSyncRecord when changing the data file of an auto-synced object
* [#15059](https://github.com/netbox-community/netbox/issues/15059) - Correct IP address count link in VM interfaces table
* [#15067](https://github.com/netbox-community/netbox/issues/15067) - Fix uncaught exception when attempting invalid device bay import
* [#15070](https://github.com/netbox-community/netbox/issues/15070) - Fix inclusion of `config_template` field on REST API serializer for virtual machines
* [#15084](https://github.com/netbox-community/netbox/issues/15084) - Fix "add export template" link under "export" button on object list views
* [#15090](https://github.com/netbox-community/netbox/issues/15090) - Ensure protection rules are evaluated prior to enqueueing events when deleting an object
* [#15091](https://github.com/netbox-community/netbox/issues/15091) - Fix designation of the active tab for assigned object when modifying an L2VPN termination
* [#15101](https://github.com/netbox-community/netbox/issues/15101) - Correct OpenAPI schema for rack elevation REST API endpoint
* [#15115](https://github.com/netbox-community/netbox/issues/15115) - Fix unhandled exception with invalid permission constraints
* [#15126](https://github.com/netbox-community/netbox/issues/15126) - `group` field should be optional when creating VPN tunnel via REST API
* [#15127](https://github.com/netbox-community/netbox/issues/15127) - Add missing group column to VPN tunnels table
* [#15133](https://github.com/netbox-community/netbox/issues/15133) - Fix FHRP group representation on assignments REST API endpoint using brief mode
* [#15174](https://github.com/netbox-community/netbox/issues/15174) - Warn that permission constraints are not supported for reports or scripts
* [#15184](https://github.com/netbox-community/netbox/issues/15184) - Correct REST API schema definition for `front_image` & `rear_image` on DeviceType
* [#15185](https://github.com/netbox-community/netbox/issues/15185) - Ensure error messages pertaining to related objects are displayed on the bulk import form
* [#15192](https://github.com/netbox-community/netbox/issues/15192) - Fix exception when viewing current config when no history is present

---

## v3.7.2 (2024-02-05)

### Enhancements

* [#13729](https://github.com/netbox-community/netbox/issues/13729) - Omit sensitive data source parameters from change log data
* [#14645](https://github.com/netbox-community/netbox/issues/14645) - Limit the number of assigned IP addresses displayed under interfaces list

### Bug Fixes

* [#14500](https://github.com/netbox-community/netbox/issues/14500) - Optimize calculation of available child prefixes & ranges when viewing a prefix
* [#14511](https://github.com/netbox-community/netbox/issues/14511) - Fix GraphQL support for interfaces connected to provider networks
* [#14572](https://github.com/netbox-community/netbox/issues/14572) - Correct the number of jobs listed for individual report & script modules
* [#14703](https://github.com/netbox-community/netbox/issues/14703) - Revert to the default layout when encountering a misconfigured dashboard
* [#14755](https://github.com/netbox-community/netbox/issues/14755) - Fix validation of choice values & labels when creating a custom field choice set via the REST API
* [#14838](https://github.com/netbox-community/netbox/issues/14838) - Avoid corrupting JSON data when changing the action type while editing an event rule
* [#14839](https://github.com/netbox-community/netbox/issues/14839) - Fix form validation error when attempting to terminate a tunnel to a virtual machine interface
* [#14840](https://github.com/netbox-community/netbox/issues/14840) - Fix `NoReverseMatch` exception when rendering a custom field which references a user
* [#14847](https://github.com/netbox-community/netbox/issues/14847) - IKE policy mode may be set inly when IKEv1 is selected
* [#14851](https://github.com/netbox-community/netbox/issues/14851) - Automatically remove any associated bookmarks when deleting a user
* [#14879](https://github.com/netbox-community/netbox/issues/14879) - Include custom fields in REST API representation of data sources
* [#14885](https://github.com/netbox-community/netbox/issues/14885) - Add missing "group" field to VPN tunnel creation form
* [#14892](https://github.com/netbox-community/netbox/issues/14892) - Fix exception when running report/script via command line due to missing username
* [#14920](https://github.com/netbox-community/netbox/issues/14920) - Include button to display available status choices when bulk importing virtual device contexts
* [#14945](https://github.com/netbox-community/netbox/issues/14945) - Fix "select all" button for device type components
* [#14947](https://github.com/netbox-community/netbox/issues/14947) - Ensure that application & removal of tags is always recorded in an object's change log
* [#14962](https://github.com/netbox-community/netbox/issues/14962) - Fix config context rendering for VMs assigned directly to a site (rather than via a cluster)
* [#14999](https://github.com/netbox-community/netbox/issues/14999) - Fix "create & add another" link for interface FHRP group assignment
* [#15015](https://github.com/netbox-community/netbox/issues/15015) - Pre-populate assigned tenant when allocating next available IP address under prefix view
* [#15020](https://github.com/netbox-community/netbox/issues/15020) - Automatically update all VMs when changing a cluster's assigned site
* [#15025](https://github.com/netbox-community/netbox/issues/15025) - The `can_add()` template filter should accept a model (not an instance)

---

## v3.7.1 (2024-01-17)

### Bug Fixes

* [#13844](https://github.com/netbox-community/netbox/issues/13844) - Use `available_at_site` filter when filtering VLANs under prefix form
* [#14663](https://github.com/netbox-community/netbox/issues/14663) - Fix tunnel creation when setting initial termination to a VM interface
* [#14706](https://github.com/netbox-community/netbox/issues/14706) - Relax one-to-one mapping of tunnel termination to IP address
* [#14709](https://github.com/netbox-community/netbox/issues/14709) - Fix typo in tunnel termination type choice name
* [#14749](https://github.com/netbox-community/netbox/issues/14749) - Remove errant translation wrapper from `installed_device` on DeviceBay
* [#14778](https://github.com/netbox-community/netbox/issues/14778) - Custom field API serializer should accept null values for all optional fields
* [#14791](https://github.com/netbox-community/netbox/issues/14791) - Hide available prefixes when searching within a parent prefix
* [#14793](https://github.com/netbox-community/netbox/issues/14793) - Add missing Diffie-Hellman group 15
* [#14816](https://github.com/netbox-community/netbox/issues/14816) - Ensure default contact assignment ordering is consistent
* [#14817](https://github.com/netbox-community/netbox/issues/14817) - Relax required fields for IKE & IPSec models on bulk import
* [#14827](https://github.com/netbox-community/netbox/issues/14827) - Ensure all matching event rules are processed in response to an event

---

## v3.7.0 (2023-12-29)

### Breaking Changes

* The following fields have been removed from the Webhook model: `content_types`, `type_create`, `type_update`, `type_delete`, `type_job_start`, `type_job_end`, `enabled`, and `conditions`. Webhooks are now tied to events via [event rules](../features/event-rules.md). New event rules will be created for any existing webhooks automatically upon upgrade.
* The `ui_visibility` field on the [custom field model](../models/extras/customfield.md) has been replaced with two new fields: `ui_visible` and `ui_editable`. These new fields will have their values mapped from the original field automatically upon upgrade.
* The `FeatureQuery` class used internally for querying content types by model feature has been removed. It has been replaced by the new `with_feature()` manager method on NetBox's proxy model for ContentType (`core.models.ContentType`).
* The internal ConfigRevision model has moved from `extras` to `core`. Configuration history will be retained throughout the upgrade process.
* The [L2VPN](../models/vpn/l2vpn.md) and [L2VPNTermination](../models/vpn/l2vpntermination.md) models have moved from the `ipam` app to the new `vpn` app. All object data will be retained, however please note that the relevant API endpoints have likewise moved to `/api/vpn/`.
* The `CustomFieldsMixin`, `SavedFiltersMixin`, and `TagsMixin` classes have moved from the `extras.forms.mixins` module to `netbox.forms.mixins`.
* The `netbox.models.features.WebhooksMixin` class has been renamed to `EventRulesMixin`.

### New Features

#### VPN Tunnels ([#9816](https://github.com/netbox-community/netbox/issues/9816))

Several new models have been introduced to enable [VPN tunnel management](../features/vpn-tunnels.md). Users can now define tunnels with two or more terminations to represent peer-to-peer or hub-and-spoke topologies. Each termination is made to a virtual interface on a device or virtual machine. Additionally, users can define IKE and IPSec proposals and policies, which can be applied to tunnels to document encryption and authentication strategies.

#### Event Rules ([#14132](https://github.com/netbox-community/netbox/issues/14132))

This release introduces [event rules](../features/event-rules.md), which can be used to send webhooks or execute custom scripts automatically in response to events that occur in NetBox. For example, it's now possible to run a custom script whenever a new site is created with a particular status or tag.

Event rules replace and extend functionality that was previously built into the webhook model. New event rules will be created for any existing webhooks automatically upon upgrade.

#### Virtual Machine Disks ([#8356](https://github.com/netbox-community/netbox/issues/8356))

A new [VirtualDisk](../models/virtualization/virtualdisk.md) model has been introduced to enable tracking the assignment of discrete virtual disks to virtual machines. The `size` field has been retained on the VirtualMachine model, and will be populated automatically with the aggregate size of all assigned virtual disks. (Users who opt to eschew the new model may continue using the VirtualMachine `size` attribute independently as in previous releases.)

#### Object Protection Rules ([#10244](https://github.com/netbox-community/netbox/issues/10244))

A new [`PROTECTION_RULES`](../configuration/data-validation.md#protection_rules) configuration parameter has been introduced. Similar to how [custom validation rules](../customization/custom-validation.md) can be used to enforce certain values for object attributes, protection rules guard against the deletion of objects which do not meet specified criteria. This enables an administrator to prevent, for example, the deletion of a site which has a status of "active."

#### Improved Custom Field Visibility Controls ([#13299](https://github.com/netbox-community/netbox/issues/13299))

The `ui_visible` field on [the custom field model](../models/extras/customfield.md) has been superseded by two new fields, `ui_visible` and `ui_editable`, which control how and whether a custom field is displayed when view and editing an object, respectively. Separating these two functions into discrete fields allows more control over how each custom field is presented to users. The values of these fields will be appropriately set automatically during the upgrade process from the value of the original field.

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
* [#13334](https://github.com/netbox-community/netbox/issues/13334) - Add an `error` field to the Job model to record any errors associated with its execution
* [#13427](https://github.com/netbox-community/netbox/issues/13427) - Introduce a mechanism for excluding models from general-purpose lists of object types
* [#13690](https://github.com/netbox-community/netbox/issues/13690) - Display any dependent objects to be deleted prior to deleting an object via the web UI
* [#13794](https://github.com/netbox-community/netbox/issues/13794) - Any models with a relationship to Tenant are now included automatically in the list of related objects under the tenant view
* [#13808](https://github.com/netbox-community/netbox/issues/13808) - Add a `/render-config` REST API endpoint for virtual machines
* [#14035](https://github.com/netbox-community/netbox/issues/14035) - Order objects of equivalent weight by value in global search results to improve readability
* [#14147](https://github.com/netbox-community/netbox/issues/14147) - Avoid recording empty changelog entries via the new `CHANGELOG_SKIP_EMPTY_CHANGES` config parameter
* [#14156](https://github.com/netbox-community/netbox/issues/14156) - Enable custom fields for contact assignments
* [#14240](https://github.com/netbox-community/netbox/issues/14240) - Increase maximum values for custom field minimum & maximum numeric validators
* [#14361](https://github.com/netbox-community/netbox/issues/14361) - Add a `description` field for webhooks
* [#14365](https://github.com/netbox-community/netbox/issues/14365) - Introduce `job_start` and `job_end` signals to allow automated plugin actions
* [#14434](https://github.com/netbox-community/netbox/issues/14434) - Add model-specific termination object filters for cables (e.g. `interface_id` and `consoleport_id`)
* [#14436](https://github.com/netbox-community/netbox/issues/14436) - Add PostgreSQL indexes for all GenericForeignKey fields
* [#14579](https://github.com/netbox-community/netbox/issues/14579) - Allow users to specify a preferred language for UI translations

### Translations

* [#14075](https://github.com/netbox-community/netbox/issues/14075) - Add Spanish translation
* [#14096](https://github.com/netbox-community/netbox/issues/14096) - Add French translation
* [#14145](https://github.com/netbox-community/netbox/issues/14145) - Add Portuguese translation
* [#14266](https://github.com/netbox-community/netbox/issues/14266) - Add Russian translation

### Bug Fixes

* [#14432](https://github.com/netbox-community/netbox/issues/14432) - Fix hyperlinks for global search result attributes
* [#14472](https://github.com/netbox-community/netbox/issues/14472) - Fix display of hidden custom fields in object edit forms
* [#14499](https://github.com/netbox-community/netbox/issues/14499) - Relax requirements for encryption/auth algorithms on IKE & IPSec proposals
* [#14550](https://github.com/netbox-community/netbox/issues/14550) - Fix changing action type of existing event rule

### Other Changes

* [#13550](https://github.com/netbox-community/netbox/issues/13550) - Optimize the format for declaring view actions under `ActionsMixin` (backward compatibility has been retained)
* [#13645](https://github.com/netbox-community/netbox/issues/13645) - Installation of the `sentry-sdk` Python library is now required only if Sentry reporting is enabled
* [#14036](https://github.com/netbox-community/netbox/issues/14036) - Move plugin resources from the `extras` app into `netbox` (backward compatibility has been retained)
* [#14153](https://github.com/netbox-community/netbox/issues/14153) - Replace `FeatureQuery` with new `with_feature()` method on proxy ContentType manager
* [#14311](https://github.com/netbox-community/netbox/issues/14311) - Move the L2VPN models from the `ipam` app to the new `vpn` app
* [#14312](https://github.com/netbox-community/netbox/issues/14312) - Move the ConfigRevision model from the `extras` app to `core`
* [#14326](https://github.com/netbox-community/netbox/issues/14326) - Form feature mixin classes have been moved from the `extras` app to `netbox`
* [#14395](https://github.com/netbox-community/netbox/issues/14395) - Move `extras.webhooks_worker.process_webhook()` to `extras.webhooks.send_webhook()` (backward compatibility has been retained)
* [#14424](https://github.com/netbox-community/netbox/issues/14424) - Remove change logging functionality from StagedChange
* [#14458](https://github.com/netbox-community/netbox/issues/14458) - Remove the obsolete `clearcache` management command
* [#14536](https://github.com/netbox-community/netbox/issues/14536) - Enforce uniqueness by default for non-VRF prefixes & IP addresses (`ENFORCE_GLOBAL_UNIQUE` now defaults to true)

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
    * Removed the following fields (these have been moved to the new `EventRule` model):
        * `content_types`
        * `type_create`
        * `type_update`
        * `type_delete`
        * `type_job_start`
        * `type_job_end`
        * `enabled`
        * `conditions`
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
