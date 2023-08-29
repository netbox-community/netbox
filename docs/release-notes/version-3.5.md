# NetBox v3.5

## v3.5.9 (2023-08-28)

### Enhancements

* [#12489](https://github.com/netbox-community/netbox/issues/12489) - Dynamically render location and device lists under site and location views
* [#12825](https://github.com/netbox-community/netbox/issues/12825) - Display assigned values count per obejct type under custom field view
* [#13313](https://github.com/netbox-community/netbox/issues/13313) - Enable filtering IP ranges by containing prefix
* [#13415](https://github.com/netbox-community/netbox/issues/13415) - Include request object in custom link renderer on tables
* [#13536](https://github.com/netbox-community/netbox/issues/13536) - Move child VLANs list to a separate tab under VLAN group view
* [#13542](https://github.com/netbox-community/netbox/issues/13542) - Pass additional HTTP headers through to custom script context
* [#13585](https://github.com/netbox-community/netbox/issues/13585) - Introduce `empty` lookup for numeric value filters

### Bug Fixes

* [#11272](https://github.com/netbox-community/netbox/issues/11272) - Fix localization support for device position field
* [#13358](https://github.com/netbox-community/netbox/issues/13358) - Git backend should send HTTP auth headers only if credentials have been defined
* [#13477](https://github.com/netbox-community/netbox/issues/13477) - Fix filtering of modified objects after bulk import/update
* [#13478](https://github.com/netbox-community/netbox/issues/13478) - Fix filtering of export templates by content type under web UI
* [#13500](https://github.com/netbox-community/netbox/issues/13500) - Fix form validation for bulk update of L2VPN terminations via bulk import form
* [#13503](https://github.com/netbox-community/netbox/issues/13503) - Fix utilization graph proportions when localization is enabled
* [#13507](https://github.com/netbox-community/netbox/issues/13507) - Avoid raising exception for invalid content type during global search
* [#13516](https://github.com/netbox-community/netbox/issues/13516) - Plugin utility functions should be importable from `extras.plugins`
* [#13530](https://github.com/netbox-community/netbox/issues/13530) - Ensure script log messages can be serialized as JSON data
* [#13543](https://github.com/netbox-community/netbox/issues/13543) - Config context tab under device/VM view should not require `extras.view_configcontext` permission
* [#13544](https://github.com/netbox-community/netbox/issues/13544) - Ensure `reindex` command clears all cached values when not in lazy mode
* [#13556](https://github.com/netbox-community/netbox/issues/13556) - Correct REST API representation of VDC status choice
* [#13569](https://github.com/netbox-community/netbox/issues/13569) - Fix selection widgets for related interfaces when bulk editing interfaces under device view

---

## v3.5.8 (2023-08-15)

### Enhancements

* [#10030](https://github.com/netbox-community/netbox/issues/10030) - Ship a validation schema for the device type library with each release
* [#11675](https://github.com/netbox-community/netbox/issues/11675) - Add support for specifying import/export route targets during VRF bulk import
* [#11922](https://github.com/netbox-community/netbox/issues/11922) - Automatically populate any VDC assignments from the parent when adding a child interface via the UI
* [#12889](https://github.com/netbox-community/netbox/issues/12889) - Add 400GE CFP2 interface type
* [#13033](https://github.com/netbox-community/netbox/issues/13033) - Add human-friendly speed column to interfaces table
* [#13151](https://github.com/netbox-community/netbox/issues/13151) - Add "assigned" filter for IP addresses
* [#13368](https://github.com/netbox-community/netbox/issues/13368) - List installed plugins on the server error report page
* [#13442](https://github.com/netbox-community/netbox/issues/13442) - Add 200 and 400 Gbps speeds to dropdown choices on interface form

### Bug Fixes

* [#11578](https://github.com/netbox-community/netbox/issues/11578) - Fix schema definition for available IP & VLAN REST API endpoints
* [#12639](https://github.com/netbox-community/netbox/issues/12639) - Raise validation error for invalid alphanumeric ranges when creating objects
* [#12665](https://github.com/netbox-community/netbox/issues/12665) - Avoid escaping semicolons when rendering custom links
* [#12750](https://github.com/netbox-community/netbox/issues/12750) - Automatically delete an AutoSyncRecord when its object is deleted
* [#13343](https://github.com/netbox-community/netbox/issues/13343) - Fix filtering of circuits under provider network view
* [#13369](https://github.com/netbox-community/netbox/issues/13369) - Fix job termination status for failed reports
* [#13414](https://github.com/netbox-community/netbox/issues/13414) - Fix support for "hide-if-unset" custom fields on bulk import forms
* [#13446](https://github.com/netbox-community/netbox/issues/13446) - Don't disable bulk edit/delete buttons after deselecting "select all" checkbox
* [#13451](https://github.com/netbox-community/netbox/issues/13451) - Disable table ordering for custom link columns

---

## v3.5.7 (2023-07-28)

### Enhancements

* [#11803](https://github.com/netbox-community/netbox/issues/11803) - Move non-rack devices list to a separate tab under the rack view
* [#12625](https://github.com/netbox-community/netbox/issues/12625) - Mask sensitive parameters when viewing a configured data source
* [#13009](https://github.com/netbox-community/netbox/issues/13009) - Add IEC 10609-1 and NBR 14136 power port & outlet types
* [#13097](https://github.com/netbox-community/netbox/issues/13097) - Implement a faster initial poll for report & script results
* [#13234](https://github.com/netbox-community/netbox/issues/13234) - Add 100GBASE-X-DSFP and 100GBASE-X-SFPDD interface types

### Bug Fixes

* [#13051](https://github.com/netbox-community/netbox/issues/13051) - Fix Markdown support for table cell alignment
* [#13167](https://github.com/netbox-community/netbox/issues/13167) - Fix missing script results when fetched via REST API
* [#13233](https://github.com/netbox-community/netbox/issues/13233) - Remove extraneous VLAN group field from bulk edit form for interfaces
* [#13237](https://github.com/netbox-community/netbox/issues/13237) - Permit unauthenticated access to content types REST API endpoint when `LOGIN_REQUIRED` is false
* [#13285](https://github.com/netbox-community/netbox/issues/13285) - Fix exception when importing device type missing rack unit height value

---

## v3.5.6 (2023-07-10)

### Bug Fixes

* [#13061](https://github.com/netbox-community/netbox/issues/13061) - Fix display of last result for scripts & reports with a custom name defined
* [#13096](https://github.com/netbox-community/netbox/issues/13096) - Hide scheduling fields for all scripts with scheduling disabled
* [#13105](https://github.com/netbox-community/netbox/issues/13105) - Fix exception when attempting to allocate next available IP address from prefix marked as utilized
* [#13116](https://github.com/netbox-community/netbox/issues/13116) - Catch ProgrammingError exception when starting NetBox without pre-populated content types

---

## v3.5.5 (2023-07-06)

### Enhancements

* [#11738](https://github.com/netbox-community/netbox/issues/11738) - Annotate VLAN group utilization
* [#12499](https://github.com/netbox-community/netbox/issues/12499) - Add "copy to clipboard" buttons in UI for IP addresses
* [#12945](https://github.com/netbox-community/netbox/issues/12945) - Add 100GE QSFP-DD interface type
* [#12955](https://github.com/netbox-community/netbox/issues/12955) - Include additional contact details on contact assignments table
* [#13065](https://github.com/netbox-community/netbox/issues/13065) - Associate contact assignments with their objects in the change log

### Bug Fixes

* [#11335](https://github.com/netbox-community/netbox/issues/11335) - Exclude stale content types when retrieving changelog records
* [#12533](https://github.com/netbox-community/netbox/issues/12533) - Fix REST API validation of null values for several interface attributes
* [#12579](https://github.com/netbox-community/netbox/issues/12579) - Fix exception when clicking "create and add another" to add a cable
* [#12617](https://github.com/netbox-community/netbox/issues/12617) - Populate prechange snapshot on parent object when assigning/removing primary IP address
* [#12760](https://github.com/netbox-community/netbox/issues/12760) - Avoid rendering partial HTMX responses when restoring browser tabs
* [#12842](https://github.com/netbox-community/netbox/issues/12842) - Improve handling of exceptions when loading reports
* [#12849](https://github.com/netbox-community/netbox/issues/12849) - Fix LDAP group permissions assignment for API clients
* [#12951](https://github.com/netbox-community/netbox/issues/12951) - Display consistent parent information for each termination under cable view
* [#12953](https://github.com/netbox-community/netbox/issues/12953) - Fix designation of primary IP addresses during interface assignment
* [#12960](https://github.com/netbox-community/netbox/issues/12960) - Fix OpenAPI schema for various choice fields
* [#12961](https://github.com/netbox-community/netbox/issues/12961) - Set correct return URL for object contacts tabs
* [#12966](https://github.com/netbox-community/netbox/issues/12966) - Avoid catching database exceptions when maintenance mode is disabled
* [#12975](https://github.com/netbox-community/netbox/issues/12975) - Correct URL for VirtualDeviceContext API serializer
* [#12977](https://github.com/netbox-community/netbox/issues/12977) - Fix URL parameters for object count dashboard widgets
* [#12983](https://github.com/netbox-community/netbox/issues/12983) - Avoid erroneously clearing many-to-many assignments during bulk edit
* [#12989](https://github.com/netbox-community/netbox/issues/12989) - Fix bulk import of tags for device & module types
* [#13011](https://github.com/netbox-community/netbox/issues/13011) - Do not escape commas when rendering custom links
* [#13047](https://github.com/netbox-community/netbox/issues/13047) - Correct ASN count under ASN ranges list
* [#13056](https://github.com/netbox-community/netbox/issues/13056) - Add `config_template` field to device API serializer
* [#13092](https://github.com/netbox-community/netbox/issues/13092) - Allow nullifying power port max & allocated draw values during bulk edit
* [#13100](https://github.com/netbox-community/netbox/issues/13100) - Fix ValueError exception when searching for virtual device context for non-numeric values

---

## v3.5.4 (2023-06-20)

### Enhancements

* [#12828](https://github.com/netbox-community/netbox/issues/12828) - Define colors for staged change action choices
* [#12847](https://github.com/netbox-community/netbox/issues/12847) - Include "add" button on all device & virtual machine component list views
* [#12862](https://github.com/netbox-community/netbox/issues/12862) - Add menu navigation button to add wireless links directly
* [#12865](https://github.com/netbox-community/netbox/issues/12865) - Add "add" buttons for reports & scripts to navigation menu

### Bug Fixes

* [#12474](https://github.com/netbox-community/netbox/issues/12474) - Update cable terminations when assigning a location to a new site
* [#12622](https://github.com/netbox-community/netbox/issues/12622) - Permit the assignment of non-site VLANs to prefixes assigned to a site
* [#12682](https://github.com/netbox-community/netbox/issues/12682) - Correct OpenAPI schema for connected device API endpoint
* [#12687](https://github.com/netbox-community/netbox/issues/12687) - Allow the assignment of all /31 IP addresses to interfaces
* [#12818](https://github.com/netbox-community/netbox/issues/12818) - Fix permissions evaluation when queuing a data sync job
* [#12822](https://github.com/netbox-community/netbox/issues/12822) - Fix encoding of whitespace in custom link URLs
* [#12838](https://github.com/netbox-community/netbox/issues/12838) - Correct rounding of rack power utilization values
* [#12845](https://github.com/netbox-community/netbox/issues/12845) - Fix pagination of objects for related IP addresses table
* [#12850](https://github.com/netbox-community/netbox/issues/12850) - Fix table configuration modal for the contact assignments list
* [#12885](https://github.com/netbox-community/netbox/issues/12885) - Permit mounting of devices in rack unit 100
* [#12914](https://github.com/netbox-community/netbox/issues/12914) - Clear stored ordering from user config when cleared by request

---

## v3.5.3 (2023-06-02)

### Enhancements

* [#9876](https://github.com/netbox-community/netbox/issues/9876) - Improve support for matching tags in conditional rules
* [#12015](https://github.com/netbox-community/netbox/issues/12015) - Add device type & role filters for device components
* [#12470](https://github.com/netbox-community/netbox/issues/12470) - Collapse context data by default when viewing a rendered device configuration
* [#12562](https://github.com/netbox-community/netbox/issues/12562) - Record client IP address when logging authentication failures
* [#12597](https://github.com/netbox-community/netbox/issues/12597) - Add an option to hide custom fields only if unset
* [#12599](https://github.com/netbox-community/netbox/issues/12599) - Apply filter parameters to links in object count dashboard widgets

### Bug Fixes

* [#7503](https://github.com/netbox-community/netbox/issues/7503) - Improve rack space validation when creating multiple devices via REST API
* [#11539](https://github.com/netbox-community/netbox/issues/11539) - Fix exception when applying "empty" filter lookup with invalid value
* [#11934](https://github.com/netbox-community/netbox/issues/11934) - Prevent reassignment of an IP address designated as primary for its parent object
* [#12538](https://github.com/netbox-community/netbox/issues/12538) - Redirect user to originating view after editing/deleting an image attachment
* [#12627](https://github.com/netbox-community/netbox/issues/12627) - Restore hover preview for embedded image attachment tables
* [#12694](https://github.com/netbox-community/netbox/issues/12694) - Strip leading & trailing whitespace from custom link URL & text
* [#12702](https://github.com/netbox-community/netbox/issues/12702) - Fix sizing of rear port selection widget on front port template creation form
* [#12715](https://github.com/netbox-community/netbox/issues/12715) - Use contact assignments table to display the contacts assigned to an object
* [#12730](https://github.com/netbox-community/netbox/issues/12730) - Fix extraneous contacts listed in object contact assignments view
* [#12742](https://github.com/netbox-community/netbox/issues/12742) - Object counts dashboard widget should support URL-compatible query filters
* [#12762](https://github.com/netbox-community/netbox/issues/12762) - Fix GraphiQL UI by reverting graphene-django to earlier version
* [#12745](https://github.com/netbox-community/netbox/issues/12745) - Escape display text in API-backed selection widgets
* [#12779](https://github.com/netbox-community/netbox/issues/12779) - Correct arithmetic for converting inches to meters

---

## v3.5.2 (2023-05-22)

### Enhancements

* [#7671](https://github.com/netbox-community/netbox/issues/7671) - Introduce `REMOTE_AUTH_AUTO_CREATE_GROUPS` config parameter to enable the automatic creation of new groups when remote authentication is in use
* [#9068](https://github.com/netbox-community/netbox/issues/9068) - Disallow the assignment of network/broadcast IP addresses to interfaces
* [#11017](https://github.com/netbox-community/netbox/issues/11017) - Increase the maximum values for allocated and maximum power draws
* [#11233](https://github.com/netbox-community/netbox/issues/11233) - Intercept and cleanly report errors upon attempted database writes when maintenance mode is enabled
* [#11599](https://github.com/netbox-community/netbox/issues/11599) - Move contacts panels to separate tabs under object views
* [#11670](https://github.com/netbox-community/netbox/issues/11670) - Enable setting device type & module type weight via bulk import
* [#11900](https://github.com/netbox-community/netbox/issues/11900) - Add an outline to the reservation markers on rack elevations
* [#12131](https://github.com/netbox-community/netbox/issues/12131) - Show custom field description as an icon tooltip under object views
* [#12223](https://github.com/netbox-community/netbox/issues/12223) - Add columns for parent device bay and position to devices list
* [#12233](https://github.com/netbox-community/netbox/issues/12233) - Move related IP addresses table to a separate tab
* [#12286](https://github.com/netbox-community/netbox/issues/12286) - Show height and total weight under device view
* [#12323](https://github.com/netbox-community/netbox/issues/12323) - Add 100GE CXP interface type
* [#12327](https://github.com/netbox-community/netbox/issues/12327) - Introduce the ability to automatically retry failed background jobs
* [#12498](https://github.com/netbox-community/netbox/issues/12498) - Hide map button if `MAPS_URL` is empty
* [#12548](https://github.com/netbox-community/netbox/issues/12548) - Optimize REST API performance when retrieving interfaces with L2VPN assignments
* [#12554](https://github.com/netbox-community/netbox/issues/12554) - Allow customization or disabling of the maintenance mode banner
* [#12605](https://github.com/netbox-community/netbox/issues/12605) - Add LX.5 port types
* [#12629](https://github.com/netbox-community/netbox/issues/12629) - Add 400GE CDFP and CFP8 interface types
* [#12678](https://github.com/netbox-community/netbox/issues/12678) - Add 200GE QSFP-DD interface type

### Bug Fixes

* [#10686](https://github.com/netbox-community/netbox/issues/10686) - Enable specifying termination object by virtual chassis master when importing cables
* [#11619](https://github.com/netbox-community/netbox/issues/11619) - Enable assigning VLANs without a site to interfaces during bulk edit
* [#12468](https://github.com/netbox-community/netbox/issues/12468) - Custom field names should not permit double underscores
* [#12550](https://github.com/netbox-community/netbox/issues/12550) - Fix rear port selection widget under front port creation form
* [#12570](https://github.com/netbox-community/netbox/issues/12570) - Disable ordering of synchronized object tables by the "synced" attribute
* [#12594](https://github.com/netbox-community/netbox/issues/12594) - Enable selecting config context as object type in object counts dashboard widget
* [#12642](https://github.com/netbox-community/netbox/issues/12642) - Fix bulk tenant assignment via cluster import form

---

## v3.5.1 (2023-05-05)

### Enhancements

* [#10759](https://github.com/netbox-community/netbox/issues/10759) - Support Markdown rendering for custom field descriptions
* [#11190](https://github.com/netbox-community/netbox/issues/11190) - Including systemd service & timer configurations for housekeeping tasks
* [#11422](https://github.com/netbox-community/netbox/issues/11422) - Match on power panel name when searching for power feeds
* [#11504](https://github.com/netbox-community/netbox/issues/11504) - Add filter to select individual racks under rack elevations view
* [#11652](https://github.com/netbox-community/netbox/issues/11652) - Add a module status column to module bay tables
* [#11791](https://github.com/netbox-community/netbox/issues/11791) - Enable configuration of custom database backend via `ENGINE` parameter
* [#11801](https://github.com/netbox-community/netbox/issues/11801) - Include device description within rack elevation tooltip
* [#11932](https://github.com/netbox-community/netbox/issues/11932) - Introduce a list view for image attachments, orderable by date and other attributes
* [#12122](https://github.com/netbox-community/netbox/issues/12122) - Enable bulk import oj journal entries
* [#12245](https://github.com/netbox-community/netbox/issues/12245) - Enable the assignment of wireless LANs to interfaces under bulk edit

### Bug Fixes

* [#10757](https://github.com/netbox-community/netbox/issues/10757) - Simplify IP address interface and NAT IP assignment form fields to avoid confusion
* [#11715](https://github.com/netbox-community/netbox/issues/11715) - Prefix within a VRF should list global prefixes as parents only if they are containers
* [#12363](https://github.com/netbox-community/netbox/issues/12363) - Fix whitespace for paragraph elements in Markdown-rendered table columns
* [#12367](https://github.com/netbox-community/netbox/issues/12367) - Fix `RelatedObjectDoesNotExist` exception under certain conditions (regression from #11550)
* [#12380](https://github.com/netbox-community/netbox/issues/12380) - Allow selecting object change as model under object list widget configuration
* [#12384](https://github.com/netbox-community/netbox/issues/12384) - Add a three-second timeout for RSS reader widget
* [#12395](https://github.com/netbox-community/netbox/issues/12395) - Fix "create & add another" action for objects with custom fields
* [#12396](https://github.com/netbox-community/netbox/issues/12396) - Provider account should not be a required field in REST API serializer
* [#12400](https://github.com/netbox-community/netbox/issues/12400) - Validate default values for object and multi-object custom fields
* [#12401](https://github.com/netbox-community/netbox/issues/12401) - Support the creation of front ports without a pre-populated device ID
* [#12405](https://github.com/netbox-community/netbox/issues/12405) - Fix filtering for VLAN groups displayed under site view
* [#12410](https://github.com/netbox-community/netbox/issues/12410) - Fix base path for OpenAPI schema (fixes Swagger UI requests)
* [#12416](https://github.com/netbox-community/netbox/issues/12416) - Fix `FileNotFoundError` exception when a managed script file is missing from disk
* [#12412](https://github.com/netbox-community/netbox/issues/12412) - Device/VM interface MAC addresses can be nullified via REST API
* [#12415](https://github.com/netbox-community/netbox/issues/12415) - Fix `ImportError` exception when running RQ worker
* [#12433](https://github.com/netbox-community/netbox/issues/12433) - Correct the application of URL query parameters for object list dashboard widgets
* [#12436](https://github.com/netbox-community/netbox/issues/12436) - Remove extraneous "add" button from contact assignments list
* [#12463](https://github.com/netbox-community/netbox/issues/12463) - Fix the association of completed jobs with reports & scripts in the REST API
* [#12464](https://github.com/netbox-community/netbox/issues/12464) - Apply credentials for git data source only when connecting via HTTP/S
* [#12476](https://github.com/netbox-community/netbox/issues/12476) - Fix `TypeError` exception when running the `runscript` management command
* [#12483](https://github.com/netbox-community/netbox/issues/12483) - Fix git remote data syncing when with HTTP proxies defined
* [#12496](https://github.com/netbox-community/netbox/issues/12496) - Remove obsolete account field from provider UI view

---

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
