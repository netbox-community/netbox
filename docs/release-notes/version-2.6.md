# NetBox v2.6 Release Notes

## v2.6.12 (2020-01-13)

### Enhancements

* [#1982](https://github.com/netbox-community/netbox/issues/1982) - Improved NAPALM method documentation in Swagger (OpenAPI)
* [#2050](https://github.com/netbox-community/netbox/issues/2050) - Preview image attachments when hovering over the link
* [#2113](https://github.com/netbox-community/netbox/issues/2113) - Allow NAPALM driver settings to be changed with request headers
* [#2598](https://github.com/netbox-community/netbox/issues/2598) - Toggle the display of child prefixes/IP addresses
* [#3009](https://github.com/netbox-community/netbox/issues/3009) - Search by description when assigning IP address to interfaces
* [#3021](https://github.com/netbox-community/netbox/issues/3021) - Add `tenant` filter field for cables
* [#3090](https://github.com/netbox-community/netbox/issues/3090) - Enable filtering of interfaces by name on the device view
* [#3187](https://github.com/netbox-community/netbox/issues/3187) - Add rack selection field to rack elevations view
* [#3393](https://github.com/netbox-community/netbox/issues/3393) - Paginate assigned circuits at the provider details view
* [#3440](https://github.com/netbox-community/netbox/issues/3440) - Add total path length to cable trace
* [#3491](https://github.com/netbox-community/netbox/issues/3491) - Include content of response on webhook error
* [#3623](https://github.com/netbox-community/netbox/issues/3623) - Enable word expansion during interface creation
* [#3668](https://github.com/netbox-community/netbox/issues/3668) - Enable searching by DNS name when assigning IP address
* [#3851](https://github.com/netbox-community/netbox/issues/3851) - Allow passing initial data to custom script forms
* [#3891](https://github.com/netbox-community/netbox/issues/3891) - Add `local_context_data` filter for virtual machines

### Bug Fixes

* [#3589](https://github.com/netbox-community/netbox/issues/3589) - Fix validation on tagged VLANs of an interface
* [#3849](https://github.com/netbox-community/netbox/issues/3849) - Fix ordering of models when dumping data to JSON
* [#3853](https://github.com/netbox-community/netbox/issues/3853) - Fix device role link on config context view
* [#3856](https://github.com/netbox-community/netbox/issues/3856) - Allow filtering VM interfaces by multiple MAC addresses
* [#3857](https://github.com/netbox-community/netbox/issues/3857) - Fix rendering of grouped custom links
* [#3862](https://github.com/netbox-community/netbox/issues/3862) - Allow filtering device components by multiple device names
* [#3864](https://github.com/netbox-community/netbox/issues/3864) - Disallow /0 masks for prefixes and IP addresses
* [#3872](https://github.com/netbox-community/netbox/issues/3872) - Paginate related IPs on the IP address view
* [#3876](https://github.com/netbox-community/netbox/issues/3876) - Fix minimum/maximum value rendering for site ASN field
* [#3882](https://github.com/netbox-community/netbox/issues/3882) - Fix filtering of devices by rack group
* [#3898](https://github.com/netbox-community/netbox/issues/3898) - Fix references to deleted cables without a label
* [#3905](https://github.com/netbox-community/netbox/issues/3905) - Fix divide-by-zero on power feeds with low power values

---

## v2.6.11 (2020-01-03)

### Bug Fixes

* [#3831](https://github.com/netbox-community/netbox/issues/3831) - Fix API-driven filter field rendering (#3812 regression)
* [#3833](https://github.com/netbox-community/netbox/issues/3833) - Add missing region filters for multiple objects

---

## v2.6.10 (2020-01-02)

### Enhancements

* [#2233](https://github.com/netbox-community/netbox/issues/2233) - Add ability to move inventory items between devices
* [#2892](https://github.com/netbox-community/netbox/issues/2892) - Extend admin UI to allow deleting old report results
* [#3062](https://github.com/netbox-community/netbox/issues/3062) - Add `assigned_to_interface` filter for IP addresses
* [#3461](https://github.com/netbox-community/netbox/issues/3461) - Fail gracefully on custom link rendering exception
* [#3705](https://github.com/netbox-community/netbox/issues/3705) - Provide request context when executing custom scripts
* [#3762](https://github.com/netbox-community/netbox/issues/3762) - Add date/time picker widgets
* [#3788](https://github.com/netbox-community/netbox/issues/3788) - Enable partial search for inventory items
* [#3812](https://github.com/netbox-community/netbox/issues/3812) - Optimize size of pages containing a dynamic selection field
* [#3827](https://github.com/netbox-community/netbox/issues/3827) - Allow filtering console/power/interface connections by device ID

### Bug Fixes

* [#3106](https://github.com/netbox-community/netbox/issues/3106) - Restrict queryset of chained fields when form validation fails
* [#3695](https://github.com/netbox-community/netbox/issues/3695) - Include A/Z termination sites for circuits in global search
* [#3712](https://github.com/netbox-community/netbox/issues/3712) - Scrolling to target (hash) did not account for the header size
* [#3780](https://github.com/netbox-community/netbox/issues/3780) - Fix AttributeError exception in API docs
* [#3809](https://github.com/netbox-community/netbox/issues/3809) - Filter platform by manufacturer when editing devices
* [#3811](https://github.com/netbox-community/netbox/issues/3811) - Fix filtering of racks by group on device list
* [#3822](https://github.com/netbox-community/netbox/issues/3822) - Fix exception when editing a device bay (regression from #3596)

---

## v2.6.9 (2019-12-16)

### Enhancements

* [#3152](https://github.com/netbox-community/netbox/issues/3152) - Include direct link to rack elevations on site view
* [#3441](https://github.com/netbox-community/netbox/issues/3441) - Move virtual machine results near devices in global search
* [#3761](https://github.com/netbox-community/netbox/issues/3761) - Added copy button for API tokens

### Bug Fixes

* [#2170](https://github.com/netbox-community/netbox/issues/2170) - Prevent the deletion of a virtual chassis when a cross-member LAG is present
* [#2358](https://github.com/netbox-community/netbox/issues/2358) - Respect custom field default values when creating objects via the REST API
* [#3749](https://github.com/netbox-community/netbox/issues/3749) - Fix exception on password change page for local users
* [#3757](https://github.com/netbox-community/netbox/issues/3757) - Fix unable to assign IP to interface

---

## v2.6.8 (2019-12-10)

### Enhancements

* [#3139](https://github.com/netbox-community/netbox/issues/3139) - Disable password change form for LDAP-authenticated users
* [#3457](https://github.com/netbox-community/netbox/issues/3457) - Display cable colors on device view
* [#3329](https://github.com/netbox-community/netbox/issues/3329) - Remove obsolete P3P policy header
* [#3663](https://github.com/netbox-community/netbox/issues/3663) - Add query filters for `created` and `last_updated` fields
* [#3722](https://github.com/netbox-community/netbox/issues/3722) - Allow the underscore character in IPAddress DNS names

### Bug Fixes

* [#3312](https://github.com/netbox-community/netbox/issues/3312) - Fix validation error when editing power cables in bulk
* [#3644](https://github.com/netbox-community/netbox/issues/3644) - Fix exception when connecting a cable to a RearPort with no corresponding FrontPort
* [#3669](https://github.com/netbox-community/netbox/issues/3669) - Include `weight` field in prefix/VLAN role form
* [#3674](https://github.com/netbox-community/netbox/issues/3674) - Include comments on PowerFeed view
* [#3679](https://github.com/netbox-community/netbox/issues/3679) - Fix link for assigned ipaddress in interface page
* [#3709](https://github.com/netbox-community/netbox/issues/3709) - Prevent exception when importing an invalid cable definition
* [#3720](https://github.com/netbox-community/netbox/issues/3720) - Correctly indicate power feed terminations on cable list
* [#3724](https://github.com/netbox-community/netbox/issues/3724) - Fix API filtering of interfaces by more than one device name
* [#3725](https://github.com/netbox-community/netbox/issues/3725) - Enforce client validation for minimum service port number

---

## v2.6.7 (2019-11-01)

### Enhancements

* [#3445](https://github.com/netbox-community/netbox/issues/3445) - Add support for additional user defined headers to be added to webhook requests
* [#3499](https://github.com/netbox-community/netbox/issues/3499) - Add `ca_file_path` to Webhook model to support user supplied CA certificate verification of webhook requests
* [#3594](https://github.com/netbox-community/netbox/issues/3594) - Add ChoiceVar for custom scripts
* [#3619](https://github.com/netbox-community/netbox/issues/3619) - Add 400GE OSFP interface type
* [#3659](https://github.com/netbox-community/netbox/issues/3659) - Add filtering for objects in admin UI

### Bug Fixes

* [#3309](https://github.com/netbox-community/netbox/issues/3309) - Rewrite change logging middleware to resolve sporadic testing failures
* [#3340](https://github.com/netbox-community/netbox/issues/3340) - Add missing options to connect front ports to console ports
* [#3357](https://github.com/netbox-community/netbox/issues/3357) - Enable filter sites/devices/VMs by null region
* [#3460](https://github.com/netbox-community/netbox/issues/3460) - Extend upgrade script to validate Python dependencies
* [#3596](https://github.com/netbox-community/netbox/issues/3596) - Prevent server error when reassigning a device to a new device bay
* [#3629](https://github.com/netbox-community/netbox/issues/3629) - Use `get_lldp_neighors_detail` to validation LLDP neighbors
* [#3635](https://github.com/netbox-community/netbox/issues/3635) - Add missing cache support for the circuits app
* [#3636](https://github.com/netbox-community/netbox/issues/3636) - Add missing `rack_group` field to PowerFeed CSV export
* [#3652](https://github.com/netbox-community/netbox/issues/3652) - Limit next/previous rack by assigned rack group

---

## v2.6.6 (2019-10-10)

### Notes

* This release includes a migration which automatically updates all existing cables to enable filtering by site/rack (see [#3259](https://github.com/netbox-community/netbox/issues/3259)). This migration may take several minutes to complete on installations with tens of thousands of cables defined.

### Enhancements

* [#1941](https://github.com/netbox-community/netbox/issues/1941) - Add InfiniBand interface types
* [#3259](https://github.com/netbox-community/netbox/issues/3259) - Add `rack` and `site` filters for cables
* [#3471](https://github.com/netbox-community/netbox/issues/3471) - Disallow raw HTML in Markdown-rendered fields
* [#3545](https://github.com/netbox-community/netbox/issues/3545) - Add `MultiObjectVar` for custom scripts
* [#3563](https://github.com/netbox-community/netbox/issues/3563) - Enable editing of individual DeviceType components
* [#3580](https://github.com/netbox-community/netbox/issues/3580) - Render text and URL fields as textareas in the custom link form
* [#3581](https://github.com/netbox-community/netbox/issues/3581) - Introduce `commit_default` custom script attribute to not commit changes by default

### Bug Fixes

* [#3458](https://github.com/netbox-community/netbox/issues/3458) - Prevent primary IP address for a device/VM from being reassigned
* [#3463](https://github.com/netbox-community/netbox/issues/3463) - Correct CSV headers for exported power feeds
* [#3474](https://github.com/netbox-community/netbox/issues/3474) - Fix device status page loading when NAPALM call fails
* [#3571](https://github.com/netbox-community/netbox/issues/3571) - Prevent erroneous redirects when editing tags
* [#3573](https://github.com/netbox-community/netbox/issues/3573) - Ensure consistent display of changelog retention period
* [#3574](https://github.com/netbox-community/netbox/issues/3574) - Change `device` to `parent` in interface editing VLAN filtering logic
* [#3575](https://github.com/netbox-community/netbox/issues/3575) - Restore label for comments field when bulk editing circuits
* [#3582](https://github.com/netbox-community/netbox/issues/3582) - Enforce view permissions on global search results
* [#3588](https://github.com/netbox-community/netbox/issues/3588) - Enforce object-form JSON for local context data on devices and VMs

---

## v2.6.5 (2019-09-25)

### Enhancements

* [#3297](https://github.com/netbox-community/netbox/issues/3297) - Include reserved units when calculating rack utilization
* [#3347](https://github.com/netbox-community/netbox/issues/3347) - Extend upgrade script to automatically remove stale content types
* [#3352](https://github.com/netbox-community/netbox/issues/3352) - Enable filtering changelog API by `changed_object_id`
* [#3515](https://github.com/netbox-community/netbox/issues/3515) - Enable export templates for inventory items
* [#3524](https://github.com/netbox-community/netbox/issues/3524) - Enable bulk editing of power outlet/power port associations
* [#3529](https://github.com/netbox-community/netbox/issues/3529) - Enable filtering circuits list by region

### Bug Fixes

* [#3435](https://github.com/netbox-community/netbox/issues/3435) - Change IP/prefix CSV export to reference VRF name instead of RD
* [#3464](https://github.com/netbox-community/netbox/issues/3464) - Fix foreground text color on color picker fields
* [#3519](https://github.com/netbox-community/netbox/issues/3519) - Prevent cables from being terminated to virtual/wireless interfaces via API
* [#3521](https://github.com/netbox-community/netbox/issues/3521) - Fix error in `parseURL` related to variables in API URL
* [#3531](https://github.com/netbox-community/netbox/issues/3531) - Fixed rack role foreground color
* [#3534](https://github.com/netbox-community/netbox/issues/3534) - Added blank option for untagged VLANs
* [#3540](https://github.com/netbox-community/netbox/issues/3540) - Fixed virtual machine interface edit with new inline vlan edit fields
* [#3543](https://github.com/netbox-community/netbox/issues/3543) - Added inline VLAN editing to virtual machine interfaces

---

## v2.6.4 (2019-09-19)

### Enhancements

* [#2160](https://github.com/netbox-community/netbox/issues/2160) - Add bulk editing for interface VLAN assignment
* [#3027](https://github.com/netbox-community/netbox/issues/3028) - Add `local_context_data` boolean filter for devices
* [#3318](https://github.com/netbox-community/netbox/issues/3318) - Increase length of platform name and slug to 100 characters
* [#3341](https://github.com/netbox-community/netbox/issues/3341) - Enable inline VLAN assignment while editing an interface
* [#3485](https://github.com/netbox-community/netbox/issues/3485) - Enable embedded graphs for devices
* [#3510](https://github.com/netbox-community/netbox/issues/3510) - Add minimum/maximum prefix length enforcement for `IPNetworkVar`

### Bug Fixes

* [#3489](https://github.com/netbox-community/netbox/issues/3489) - Prevent exception triggered by webhook upon object deletion
* [#3501](https://github.com/netbox-community/netbox/issues/3501) - Fix rendering of checkboxes on custom script forms
* [#3511](https://github.com/netbox-community/netbox/issues/3511) - Correct API URL for nested device bays
* [#3513](https://github.com/netbox-community/netbox/issues/3513) - Fix assignment of tags when creating front/rear ports
* [#3514](https://github.com/netbox-community/netbox/issues/3514) - Label TextVar fields when rendering custom script forms

---

## v2.6.3 (2019-09-04)

### New Features

#### Custom Scripts ([#3415](https://github.com/netbox-community/netbox/issues/3415))

Custom scripts allow for the execution of arbitrary code via the NetBox UI. They can be used to automatically create, manipulate, or clean up objects or perform other tasks within NetBox. Scripts are defined as Python files which contain one or more subclasses of `extras.scripts.Script`. Variable fields can be defined within scripts, which render as form fields within the web UI to prompt the user for input data. Scripts are executed and information is logged via the web UI. Please see [the docs](https://netbox.readthedocs.io/en/stable/additional-features/custom-scripts/) for more detail.

Note: There are currently no API endpoints for this feature. These are planned for the upcoming v2.7 release.

### Enhancements

* [#3386](https://github.com/netbox-community/netbox/issues/3386) - Add `mac_address` filter for virtual machines
* [#3391](https://github.com/netbox-community/netbox/issues/3391) - Update Bootstrap CSS to v3.4.1
* [#3405](https://github.com/netbox-community/netbox/issues/3405) - Fix population of power port/outlet details on device creation
* [#3422](https://github.com/netbox-community/netbox/issues/3422) - Prevent navigation menu from overlapping page content
* [#3430](https://github.com/netbox-community/netbox/issues/3430) - Linkify platform field on device view
* [#3454](https://github.com/netbox-community/netbox/issues/3454) - Enable filtering circuits by region
* [#3456](https://github.com/netbox-community/netbox/issues/3456) - Enable bulk editing of tag color

### Bug Fixes

* [#3392](https://github.com/netbox-community/netbox/issues/3392) - Add database index for ObjectChange time
* [#3420](https://github.com/netbox-community/netbox/issues/3420) - Serial number filter for racks, devices, and inventory items is now case-insensitive
* [#3428](https://github.com/netbox-community/netbox/issues/3428) - Fixed cache invalidation issues ([#3300](https://github.com/netbox-community/netbox/issues/3300), [#3363](https://github.com/netbox-community/netbox/issues/3363), [#3379](https://github.com/netbox-community/netbox/issues/3379), [#3382](https://github.com/netbox-community/netbox/issues/3382)) by switching to `prefetch_related()` instead of `select_related()` and removing use of `update()`
* [#3421](https://github.com/netbox-community/netbox/issues/3421) - Fix exception when ordering power connections list by PDU
* [#3424](https://github.com/netbox-community/netbox/issues/3424) - Fix tag coloring for non-linked tags
* [#3426](https://github.com/netbox-community/netbox/issues/3426) - Improve API error handling for ChoiceFields

---

## v2.6.2 (2019-08-02)

### Enhancements

* [#984](https://github.com/netbox-community/netbox/issues/984) - Allow ordering circuits by A/Z side
* [#3307](https://github.com/netbox-community/netbox/issues/3307) - Add power panels count to home page
* [#3314](https://github.com/netbox-community/netbox/issues/3314) - Paginate object changelog entries
* [#3367](https://github.com/netbox-community/netbox/issues/3367) - Add BNC port type and coaxial cable type
* [#3368](https://github.com/netbox-community/netbox/issues/3368) - Indicate indefinite changelog retention when applicable
* [#3370](https://github.com/netbox-community/netbox/issues/3370) - Add filter class to VirtualChassis API

### Bug Fixes

* [#3018](https://github.com/netbox-community/netbox/issues/3018) - Components connected via a cable must have an equal number of positions
* [#3289](https://github.com/netbox-community/netbox/issues/3289) - Prevent position from being nullified when moving a device to a new rack
* [#3293](https://github.com/netbox-community/netbox/issues/3293) - Enable filtering device components by multiple device IDs
* [#3315](https://github.com/netbox-community/netbox/issues/3315) - Enable filtering devices/interfaces by multiple MAC addresses
* [#3317](https://github.com/netbox-community/netbox/issues/3317) - Fix permissions for ConfigContextBulkDeleteView
* [#3323](https://github.com/netbox-community/netbox/issues/3323) - Fix permission evaluation for interface connections view
* [#3342](https://github.com/netbox-community/netbox/issues/3342) - Fix cluster delete button
* [#3384](https://github.com/netbox-community/netbox/issues/3384) - Maximum and allocated draw fields should be included on power port template creation form
* [#3385](https://github.com/netbox-community/netbox/issues/3385) - Fix power panels list when bulk editing power feeds

---

## v2.6.1 (2019-06-25)

### Enhancements

* [#3154](https://github.com/netbox-community/netbox/issues/3154) - Add `virtual_chassis_member` device filter
* [#3277](https://github.com/netbox-community/netbox/issues/3277) - Add cable trace buttons for console and power ports
* [#3281](https://github.com/netbox-community/netbox/issues/3281) - Hide custom links which render as empty text

### Bug Fixes

* [#3229](https://github.com/netbox-community/netbox/issues/3229) - Limit rack group selection by parent site on racks list
* [#3269](https://github.com/netbox-community/netbox/issues/3269) - Raise validation error when specifying non-existent cable terminations
* [#3275](https://github.com/netbox-community/netbox/issues/3275) - Fix error when adding power outlets to a device type
* [#3279](https://github.com/netbox-community/netbox/issues/3279) - Reset the PostgreSQL sequence for Tag and TaggedItem IDs
* [#3283](https://github.com/netbox-community/netbox/issues/3283) - Fix rack group assignment on PowerFeed CSV import
* [#3290](https://github.com/netbox-community/netbox/issues/3290) - Fix server error when viewing cascaded PDUs
* [#3292](https://github.com/netbox-community/netbox/issues/3292) - Ignore empty URL query parameters

---

## v2.6.0 (2019-06-20)

### New Features

#### Power Panels and Feeds ([#54](https://github.com/netbox-community/netbox/issues/54))

NetBox now supports power circuit modeling via two new models: power panels and power feeds. Power feeds are terminated
to power panels and are optionally associated with individual racks. Each power feed defines a supply type (AC/DC),
amperage, voltage, and phase. A power port can be connected directly to a power feed, but a power feed may have only one
power port connected to it.

Additionally, the power port model, which represents a device's power input, has been extended to include fields
denoting maximum and allocated draw, in volt-amperes. This allows a device (e.g. a PDU) to calculate its total load
compared to its connected power feed.

#### Caching ([#2647](https://github.com/netbox-community/netbox/issues/2647))

To improve performance, NetBox now supports caching for most object and list views. Caching is implemented using Redis,
which is now a required dependency. (Previously, Redis was required only if webhooks were enabled.)

A new configuration parameter is available to control the cache timeout:

```
## Cache timeout (in seconds)
CACHE_TIMEOUT = 900
```

#### View Permissions ([#323](https://github.com/netbox-community/netbox/issues/323))

Django 2.1 introduced the ability to enforce view-only permissions for different object types. NetBox now enforces
these by default. You can grant view permission to a user or group by assigning the "can view" permission for the
desired object(s).

To exempt certain object types from the enforcement of view permissions, so that any user (including anonymous users)
can view them, add them to the new `EXEMPT_VIEW_PERMISSIONS` setting in `configuration.py`:

```
EXEMPT_VIEW_PERMISSIONS = [
    'dcim.site',
    'ipam.prefix',
]
```

To exclude _all_ objects, effectively disabling view permissions and restoring pre-v2.6 behavior, set:

```
EXEMPT_VIEW_PERMISSIONS = ['*']
```

#### Custom Links ([#969](https://github.com/netbox-community/netbox/issues/969))

Custom links are created under the admin UI and will be displayed on each object of the selected type. Link text and
URLs can be formed from Jinja2 template code, with the viewed object passed as context data. For example, to link to an
external NMS from the device view, you might create a custom link with the following URL:

```
https://nms.example.com/nodes/?name={{ obj.name }}
```

Custom links appear as buttons at the top of the object view. Grouped links will render as a dropdown menu beneath a
single button.

#### Prometheus Metrics ([#3104](https://github.com/netbox-community/netbox/issues/3104))

NetBox now supports exposing native Prometheus metrics from the application. [Prometheus](https://prometheus.io/) is a
popular time series metric platform used for monitoring. Metric exposition can be toggled with the `METRICS_ENABLED`
configuration setting; it is not enabled by default. NetBox exposes metrics at the `/metrics` HTTP endpoint, e.g.
`https://netbox.local/metrics`.

NetBox makes use of the [django-prometheus](https://github.com/korfuri/django-prometheus) library to export a number of
different types of metrics, including:

* Per model insert, update, and delete counters
* Per view request counters
* Per view request latency histograms
* Request body size histograms
* Response body size histograms
* Response code counters
* Database connection, execution, and error counters
* Cache hit, miss, and invalidation counters
* Django middleware latency histograms
* Other Django related metadata metrics

For the exhaustive list of exposed metrics, visit the `/metrics` endpoint on your NetBox instance. See the documentation
for more details on using Prometheus metrics in NetBox.

### Changes

#### New Dependency: Redis

[Redis](https://redis.io/) is an in-memory data store similar to memcached. While Redis has been an optional component
of NetBox since the introduction of webhooks in version 2.4, it is now required to support NetBox's new caching
functionality (as well as other planned features). Redis can be installed via your platform's package manager: for
example, `sudo apt-get install redis-server` on Ubuntu or `sudo yum install redis` on CentOS.

The Redis database is configured using a configuration setting similar to `DATABASE` in `configuration.py`:

```
REDIS = {
    'HOST': 'localhost',
    'PORT': 6379,
    'PASSWORD': '',
    'DATABASE': 0,
    'CACHE_DATABASE': 1,
    'DEFAULT_TIMEOUT': 300,
    'SSL': False,
}
```

Note that if you were using these settings in a prior release with webhooks, the `DATABASE` setting remains the same but
an additional `CACHE_DATABASE` setting has been added with a default value of 1 to support the caching backend. The
`DATABASE` setting will be renamed in a future release of NetBox to better relay the meaning of the setting. It is
highly recommended to keep the webhook and cache databases seperate. Using the same database number for both may result
in webhook processing data being lost during cache flushing events.

#### API Support for Specifying Related Objects by Attributes([#3077](https://github.com/netbox-community/netbox/issues/3077))

Previously, specifying a related object in an API request required knowing the primary key (integer ID) of that object.
For example, when creating a new device, its rack would be specified as an integer:

```
{
    "name": "MyNewDevice",
    "rack": 123,
    ...
}
```

The NetBox API now also supports referencing related objects by a set of sufficiently unique attrbiutes. For example, a
rack can be identified by its name and parent site:

```
{
    "name": "MyNewDevice",
    "rack": {
        "site": {
            "name": "Equinix DC6"
        },
        "name": "R204"
    },
    ...
}
```

There is no limit to the depth of nested references. Note that if the provided parameters do not return exactly one
object, a validation error is raised.

#### API Device/VM Config Context Included by Default ([#2350](https://github.com/netbox-community/netbox/issues/2350))

The rendered config context for devices and VMs is now included by default in all API results (list and detail views).
Previously, the rendered config context was available only in the detail view for individual objects. Users with large
amounts of context data may observe a performance drop when returning multiple objects. To combat this, in cases where
the rendered config context is not needed, the query parameter `?exclude=config_context` may be appended to the request
URL to exclude the config context data from the API response.

#### Changes to Tag Permissions

NetBox now makes use of its own `Tag` model instead of the stock model which ships with django-taggit. This new model
lives in the `extras` app and thus any permissions that you may have configured using "Taggit | Tag" should be changed
to now use "Extras | Tag." Also note that the admin interface for tags has been removed as it was redundant to the
functionality provided by the front end UI.

#### CORS_ORIGIN_WHITELIST Requires URI Scheme

If you have the `CORS_ORIGIN_WHITELIST` configuration parameter defined, note that each origin must now incldue a URI
scheme. This change was introuced in django-cors-headers 3.0.

### Enhancements

* [#166](https://github.com/netbox-community/netbox/issues/166) - Add `dns_name` field to IPAddress
* [#524](https://github.com/netbox-community/netbox/issues/524) - Added power utilization graphs to power feeds, devices, and racks
* [#1792](https://github.com/netbox-community/netbox/issues/1792) - Add CustomFieldChoices API endpoint at `/api/extras/_custom_field_choices/`
* [#1863](https://github.com/netbox-community/netbox/issues/1863) - Add child object counts to API representation of organizational objects
* [#2324](https://github.com/netbox-community/netbox/issues/2324) - Add `color` field for tags
* [#2643](https://github.com/netbox-community/netbox/issues/2643) - Add `description` field to console/power components and device bays
* [#2791](https://github.com/netbox-community/netbox/issues/2791) - Add `comments` field for tags
* [#2920](https://github.com/netbox-community/netbox/issues/2920) - Rename Interface `form_factor` to `type` (backward-compatible until v2.7)
* [#2926](https://github.com/netbox-community/netbox/issues/2926) - Add change logging to the Tag model
* [#3038](https://github.com/netbox-community/netbox/issues/3038) - OR logic now used when multiple values of a query filter are passed
* [#3264](https://github.com/netbox-community/netbox/issues/3264) - Annotate changelog retention time on UI

### Bug Fixes

* [#2968](https://github.com/netbox-community/netbox/issues/2968) - Correct API documentation for SerializerMethodFields
* [#3176](https://github.com/netbox-community/netbox/issues/3176) - Add cable trace button for console server ports and power outlets
* [#3231](https://github.com/netbox-community/netbox/issues/3231) - Fixed cosmetic error indicating a missing schema migration
* [#3239](https://github.com/netbox-community/netbox/issues/3239) - Corrected count of tags reported via API

### Bug Fixes From v2.6-beta1

* [#3123](https://github.com/netbox-community/netbox/issues/3123) - Exempt `/metrics` view from authentication
* [#3125](https://github.com/netbox-community/netbox/issues/3125) - Fix exception when viewing PDUs
* [#3126](https://github.com/netbox-community/netbox/issues/3126) - Incorrect calculation of PowerFeed available power
* [#3130](https://github.com/netbox-community/netbox/issues/3130) - Fix exception when creating a new power outlet
* [#3136](https://github.com/netbox-community/netbox/issues/3136) - Add power draw fields to power port creation form
* [#3137](https://github.com/netbox-community/netbox/issues/3137) - Add `power_port` and `feed_leg` fields to power outlet creation form
* [#3140](https://github.com/netbox-community/netbox/issues/3140) - Add bulk edit capability for power outlets and console server ports
* [#3204](https://github.com/netbox-community/netbox/issues/3204) - Fix interface filtering when connecting cables
* [#3207](https://github.com/netbox-community/netbox/issues/3207) - Fix link for connecting interface to rear port
* [#3258](https://github.com/netbox-community/netbox/issues/3258) - Exception raised when creating/viewing a circuit with a non-connected termination

### API Changes

* New API endpoints for power modeling: `/api/dcim/power-panels/` and `/api/dcim/power-feeds/`
* New API endpoint for custom field choices: `/api/extras/_custom_field_choices/`
* ForeignKey fields now accept either the related object PK or a dictionary of attributes describing the related object.
* Organizational objects now include child object counts. For example, the Role serializer includes `prefix_count` and `vlan_count`.
* The `id__in` filter is now deprecated and will be removed in v2.7. (Begin using the `?id=1&id=2` format instead.)
* Added a `description` field for all device components.
* dcim.Device: The devices list endpoint now includes rendered context data.
* dcim.DeviceType: `instance_count` has been renamed to `device_count`.
* dcim.Interface: `form_factor` has been renamed to `type`. Backward compatibility for `form_factor` will be maintained until NetBox v2.7.
* dcim.Interface: The `type` filter has been renamed to `kind`.
* dcim.Site: The `count_*` read-only fields have been renamed to `*_count` for consistency with other objects.
* dcim.Site: Added the `virtualmachine_count` read-only field.
* extras.Tag: Added `color` and `comments` fields to the Tag serializer.
* virtualization.VirtualMachine: The virtual machines list endpoint now includes rendered context data.
