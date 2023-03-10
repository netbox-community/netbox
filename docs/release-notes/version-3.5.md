# NetBox v3.5

## v3.5.0 (FUTURE)

### New Features

#### Customizable Dashboard ([#9416](https://github.com/netbox-community/netbox/issues/9416))

The static home view has been replaced with a fully customizable dashboard. Users can construct and rearrange their own personal dashboard to convey the information most pertinent to them. Supported widgets include object statistics, change log records, notes, and more, and we expect to continue adding new widgets over time. Plugins can also register their own custom widgets.

#### Remote Data Sources ([#11558](https://github.com/netbox-community/netbox/issues/11558))

NetBox now has the ability to synchronize arbitrary data from external sources through the new [DataSource](../models/core/datasource.md) and [DataFile](../models/core/datafile.md) models. Synchronized files are stored in the PostgreSQL database, and may be referenced and consumed by other NetBox models, such as export templates and config contexts. Currently, replication from local filesystem paths and from git repositories is supported, and we expect to add support for additional backends in the near future.

#### Configuration Template Rendering ([#11559](https://github.com/netbox-community/netbox/issues/11559))

This release introduces the ability to render device configurations from Jinja2 templates natively within NetBox, via both the UI and REST API. The new [ConfigTemplate](../models/extras/configtemplate.md) model stores template code (which may be defined locally or sourced from remote data files). The rendering engine passes data gleaned from both config contexts and request parameters to generate complete configurations suitable for direct application to network devices.

#### NAPALM Plugin ([#10520](https://github.com/netbox-community/netbox/issues/10520))

The NAPALM integration feature found in previous NetBox releases has been moved from the core application to a dedicated plugin. This allows greater control over the feature's configuration and will unlock additional potential as a separate project.

#### ASN Ranges ([#8550](https://github.com/netbox-community/netbox/issues/8550))

A new ASN range model has been introduced to facilitate the provisioning of new autonomous system numbers from within a prescribed range. For example, an administrator might define an ASN range of 65000-65099 to be used for internal site identification. This includes a REST API endpoint suitable for automatic provisioning, very similar to the allocation of available prefixes and IP addresses.

### Enhancements

* [#7947](https://github.com/netbox-community/netbox/issues/7947) - Enable marking IP ranges as fully utilized
* [#8272](https://github.com/netbox-community/netbox/issues/8272) - Support bridge relationships among device type interfaces
* [#8958](https://github.com/netbox-community/netbox/issues/8958) - Changes in background job status can trigger webhooks
* [#9073](https://github.com/netbox-community/netbox/issues/9073) - Enable syncing config context data from remote sources
* [#9653](https://github.com/netbox-community/netbox/issues/9653) - Enable setting a default platform for device types
* [#10374](https://github.com/netbox-community/netbox/issues/10374) - Require unique tenant names & slugs per group (not globally)
* [#10729](https://github.com/netbox-community/netbox/issues/10729) - Add date & time custom field type
* [#11254](https://github.com/netbox-community/netbox/issues/11254) - Introduce the `X-Request-ID` HTTP header to annotate the unique ID of each request for change logging
* [#11440](https://github.com/netbox-community/netbox/issues/11440) - Add an `enabled` field for device type interfaces
* [#11517](https://github.com/netbox-community/netbox/issues/11517) - Standardize the inclusion of related objects across the entire UI
* [#11584](https://github.com/netbox-community/netbox/issues/11584) - Add a list view for contact assignments
* [#11625](https://github.com/netbox-community/netbox/issues/11625) - Add HTMX support to ObjectEditView
* [#11693](https://github.com/netbox-community/netbox/issues/11693) - Enable syncing export template content from remote sources

### Other Changes

* [#10604](https://github.com/netbox-community/netbox/issues/10604) - Remove unused `extra_tabs` block from `object.html` generic template
* [#10923](https://github.com/netbox-community/netbox/issues/10923) - Remove unused `NetBoxModelCSVForm` class (replaced by `NetBoxModelImportForm`)
* [#11611](https://github.com/netbox-community/netbox/issues/11611) - Refactor API viewset classes and introduce NetBoxReadOnlyModelViewSet
* [#11694](https://github.com/netbox-community/netbox/issues/11694) - Remove obsolete `SmallTextarea` form widget
* [#11737](https://github.com/netbox-community/netbox/issues/11737) - `ChangeLoggedModel` now inherits `WebhooksMixin`
* [#11765](https://github.com/netbox-community/netbox/issues/11765) - Retire the `StaticSelect` and `StaticSelectMultiple` form widgets
