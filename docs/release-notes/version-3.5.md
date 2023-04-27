# NetBox v3.5

## v3.5.0 (2023-04-27)

### Breaking Changes

* The `account` field has been removed from the provider model. This information is now tracked using the new provider account model. Multiple accounts can be assigned per provider.
* A minimum length of 50 characters is now enforced for the `SECRET_KEY` configuration parameter.
* The JobResult model has been moved from the `extras` app to `core` and renamed to Job. Accordingly, its REST API endpoint has been moved from `/api/extras/job-results/` to `/api/core/jobs/`.
* The `obj_type` field on the Job model (previously JobResult) has been renamed to `object_type` for consistency with other models.
* The `JOBRESULT_RETENTION` configuration parameter has been renamed to `JOB_RETENTION`.
* The `obj` context variable is no longer passed when rendering custom links: Use `object` instead.
* The REST API schema is now generated using the OpenAPI 3.0 spec
* The URLs for the REST API schema documentation have changed:
    * `/api/docs/` is now `/api/schema/swagger-ui/`
    * `/api/redoc/` is now `/api/schema/redoc/`

### New Features

#### Customizable Dashboard ([#9416](https://github.com/netbox-community/netbox/issues/9416))

The static home view has been replaced with a fully customizable dashboard. Users can construct and rearrange their own personal dashboard to convey the information most pertinent to them. Supported widgets include object statistics, configurable object lists, RSS feeds, and notes, and we expect to continue adding new widgets over time.

#### Remote Data Sources ([#11558](https://github.com/netbox-community/netbox/issues/11558))

NetBox now has the ability to synchronize arbitrary data from external sources through the new [DataSource](../models/core/datasource.md) and [DataFile](../models/core/datafile.md) models. Synchronized files are stored in the PostgreSQL database, and may be referenced and consumed by other NetBox models, such as export templates and config contexts. Currently, replication from local filesystem paths, git repositories, and Amazon S3 buckets is supported, and we expect to introduce additional backends in the near future.

#### Configuration Template Rendering ([#11559](https://github.com/netbox-community/netbox/issues/11559))

This release introduces the ability to render device configurations from Jinja2 templates natively within NetBox, via both the UI and REST API. The new [ConfigTemplate](../models/extras/configtemplate.md) model stores template code (which may be defined locally or sourced from remote data files). The rendering engine passes data gleaned from both config contexts and request parameters to generate complete configurations suitable for direct application to network devices.

#### NAPALM Integration Plugin ([#10520](https://github.com/netbox-community/netbox/issues/10520))

The NAPALM integration feature found in previous NetBox releases has been moved from the core application to a [dedicated plugin](https://github.com/netbox-community/netbox-napalm). This allows greater control over the feature's configuration and will unlock additional potential as a separate project.

#### ASN Ranges ([#8550](https://github.com/netbox-community/netbox/issues/8550))

A new ASN range model has been introduced to facilitate the provisioning of new autonomous system numbers from within a prescribed range. For example, an administrator might define an ASN range of 65000-65099 to be used for internal site identification. This includes a REST API endpoint suitable for automatic provisioning, very similar to the allocation of available prefixes and IP addresses.

#### Provider Accounts ([#9047](https://github.com/netbox-community/netbox/issues/9047))

A new model has been introduced to represent individual accounts within a common circuit provider. This replaces the `account` field on the provider model, enabling users to track multiple accounts per provider. New provider account instances will be created automatically during upgrade for all providers which currently have an account assigned. The assignment of individual circuits to a provider account remains optional.

#### Job-Triggered Webhooks ([#8958](https://github.com/netbox-community/netbox/issues/8958))

Two new webhook trigger events have been introduced: `job_start` and `job_end`. These enable users to configure webhook to trigger when a background job starts or ends, respectively. This new functionality can be used, for example, to inform a remote system when a custom script has been executed.

### Enhancements

* [#7947](https://github.com/netbox-community/netbox/issues/7947) - Enable marking IP ranges as fully utilized
* [#8184](https://github.com/netbox-community/netbox/issues/8184) - Employ HTMX to dynamically render tables listing related objects
* [#8272](https://github.com/netbox-community/netbox/issues/8272) - Support bridge relationships among device type interfaces
* [#8749](https://github.com/netbox-community/netbox/issues/8749) - Support replicating custom field values when cloning an object
* [#9073](https://github.com/netbox-community/netbox/issues/9073) - Enable syncing config context data from remote sources
* [#9653](https://github.com/netbox-community/netbox/issues/9653) - Enable setting a default platform for device types
* [#10054](https://github.com/netbox-community/netbox/issues/10054) - Introduce advanced object selector for UI forms
* [#10242](https://github.com/netbox-community/netbox/issues/10242) - Redirect to filtered objects list after bulk import
* [#10374](https://github.com/netbox-community/netbox/issues/10374) - Require unique tenant names & slugs per group
* [#10729](https://github.com/netbox-community/netbox/issues/10729) - Add date & time custom field type
* [#11029](https://github.com/netbox-community/netbox/issues/11029) - Enable change logging for cable terminations
* [#11254](https://github.com/netbox-community/netbox/issues/11254) - Introduce the `X-Request-ID` HTTP header to annotate the unique ID of each request for change logging
* [#11255](https://github.com/netbox-community/netbox/issues/11255) - Introduce the `scheduling_enabled` settings for reports & scripts
* [#11291](https://github.com/netbox-community/netbox/issues/11291) - Optimized GraphQL API request handling
* [#11440](https://github.com/netbox-community/netbox/issues/11440) - Add an `enabled` field for device type interfaces
* [#11494](https://github.com/netbox-community/netbox/issues/11494) - Enable filtering objects by create/update request IDs
* [#11517](https://github.com/netbox-community/netbox/issues/11517) - Standardize the inclusion of related objects across the entire UI
* [#11584](https://github.com/netbox-community/netbox/issues/11584) - Add a list view for contact assignments
* [#11625](https://github.com/netbox-community/netbox/issues/11625) - Add HTMX support to ObjectEditView
* [#11693](https://github.com/netbox-community/netbox/issues/11693) - Enable syncing export template content from remote sources
* [#11780](https://github.com/netbox-community/netbox/issues/11780) - Enable loading import data from remote sources
* [#11790](https://github.com/netbox-community/netbox/issues/11790) - Create database indexes for all generic foreign keys
* [#11968](https://github.com/netbox-community/netbox/issues/11968) - Add navigation menu buttons to create device & VM components
* [#12068](https://github.com/netbox-community/netbox/issues/12068) - Enable generic foreign key relationships from jobs to NetBox objects
* [#12085](https://github.com/netbox-community/netbox/issues/12085) - Add a file source view for reports
* [#12218](https://github.com/netbox-community/netbox/issues/12218) - Provide more relevant API endpoint descriptions in schema
* [#12343](https://github.com/netbox-community/netbox/issues/12343) - Enforce a minimum length for `SECRET_KEY` configuration parameter

### Bug Fixes (From Beta2)

* [#12149](https://github.com/netbox-community/netbox/issues/12149) - Fix OpenAPI schema warnings relating to enum collisions
* [#12195](https://github.com/netbox-community/netbox/issues/12195) - Fix exception when setting IP address role to null via REST API
* [#12256](https://github.com/netbox-community/netbox/issues/12256) - Fix OpenAPI schema warnings relating to nested serializers
* [#12278](https://github.com/netbox-community/netbox/issues/12278) - Fix schema warnings related to IPAddressField
* [#12288](https://github.com/netbox-community/netbox/issues/12288) - Include `servers` definition in OpenAPI spec
* [#12299](https://github.com/netbox-community/netbox/issues/12299) - Fix object list widget support for filtering by multiple values

### Other Changes

* [#9608](https://github.com/netbox-community/netbox/issues/9608) - Upgrade REST API schema to OpenAPI 3.0
* [#10604](https://github.com/netbox-community/netbox/issues/10604) - Remove unused `extra_tabs` block from `object.html` generic template
* [#10923](https://github.com/netbox-community/netbox/issues/10923) - Remove unused `NetBoxModelCSVForm` class (replaced by `NetBoxModelImportForm`)
* [#11489](https://github.com/netbox-community/netbox/issues/11489) - Consolidated several middleware classes
* [#11611](https://github.com/netbox-community/netbox/issues/11611) - Refactor API viewset classes and introduce NetBoxReadOnlyModelViewSet
* [#11694](https://github.com/netbox-community/netbox/issues/11694) - Remove obsolete `SmallTextarea` form widget
* [#11737](https://github.com/netbox-community/netbox/issues/11737) - `ChangeLoggedModel` now inherits `WebhooksMixin`
* [#11765](https://github.com/netbox-community/netbox/issues/11765) - Retire the `StaticSelect` and `StaticSelectMultiple` form widgets
* [#11955](https://github.com/netbox-community/netbox/issues/11955) - Remove the unused `CSVDataField` and `CSVFileField` classes
* [#12067](https://github.com/netbox-community/netbox/issues/12067) - Move & rename `extras.JobResult` to `core.Job`

### REST API Changes

* All API responses now include a `X-Request-ID` HTTP header indicating the request's unique ID
* Introduced new endpoints:
    * `/api/circuits/provider-accounts/`
    * `/api/core/data-files/`
    * `/api/core/data-sources/`
    * `/api/dcim/device/<id>/render-config/`
    * `/api/extras/config-templates/`
    * `/api/ipam/asn-ranges/`
* Removed existing endpoints:
    * `/api/dcim/device/<id>/napalm/`
* circuits.Circuit
    * Added the optional `account` foreign key to ProviderAccount
* circuits.Provider
    * Removed the `account` field
* dcim.CableTermination
    * Added `default_platform` foreign key (optional)
* dcim.DeviceType
    * Added `default_platform` foreign key (optional)
* dcim.InterfaceTemplate
    * Added `enabled` boolean field
    * Added optional `bridge` foreign key (optional)
* extras.ConfigContext
    * Added `data_source`, `data_file`, `data_path`, and `data_synced` fields to enable syncing data from remote sources
* extras.ExportTemplate
    * Added `data_source`, `data_file`, `data_path`, and `data_synced` fields to enable syncing content from remote sources
* extras.Webhook
    * Added `type_job_start` and `type_job_end` boolean fields
* ipam.ASN
    * The `rir` field now fully represents the assigned RIR (if any)
* ipam.IPRange
    * Added the `mark_utilized` boolean field (default: false)
