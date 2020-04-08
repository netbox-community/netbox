# NetBox v2.7 Release Notes

## v2.7.12 (2020-04-08)

### Enhancements

* [#3676](https://github.com/netbox-community/netbox/issues/3676) - Reference VRF by name rather than RD during IP/prefix import
* [#4147](https://github.com/netbox-community/netbox/issues/4147) - Use absolute URLs in rack elevation SVG renderings
* [#4448](https://github.com/netbox-community/netbox/issues/4448) - Allow connecting cables between two circuit terminations
* [#4460](https://github.com/netbox-community/netbox/issues/4460) - Add the `webhook_receiver` management command to assist in troubleshooting outgoing webhooks

### Bug Fixes

* [#4395](https://github.com/netbox-community/netbox/issues/4395) - Fix typing of count_ipaddresses on interface serializer
* [#4418](https://github.com/netbox-community/netbox/issues/4418) - Fail cleanly when trying to import multiple device types simultaneously
* [#4438](https://github.com/netbox-community/netbox/issues/4438) - Fix exception when disconnecting a cable from a power feed
* [#4439](https://github.com/netbox-community/netbox/issues/4439) - Tweak display of unset custom integer fields
* [#4449](https://github.com/netbox-community/netbox/issues/4449) - Fix reservation edit/delete button URLs on rack view

---

## v2.7.11 (2020-03-27)

### Enhancements

* [#738](https://github.com/netbox-community/netbox/issues/738) - Add ability to automatically check for new releases (must be enabled by setting `RELEASE_CHECK_URL`)
* [#4255](https://github.com/netbox-community/netbox/issues/4255) - Custom script object variables now utilize dynamic form widgets
* [#4309](https://github.com/netbox-community/netbox/issues/4309) - Add descriptive tooltip to custom fields on object views
* [#4369](https://github.com/netbox-community/netbox/issues/4369) - Add a dedicated view for rack reservations
* [#4380](https://github.com/netbox-community/netbox/issues/4380) - Enable webhooks for rack reservations
* [#4381](https://github.com/netbox-community/netbox/issues/4381) - Enable export templates for rack reservations
* [#4382](https://github.com/netbox-community/netbox/issues/4382) - Enable custom links for rack reservations
* [#4386](https://github.com/netbox-community/netbox/issues/4386) - Update admin links for Django RQ to reflect multiple queues
* [#4389](https://github.com/netbox-community/netbox/issues/4389) - Add a bulk edit view for device bays
* [#4404](https://github.com/netbox-community/netbox/issues/4404) - Add cable trace button for circuit terminations

### Bug Fixes

* [#2769](https://github.com/netbox-community/netbox/issues/2769) - Improve `prefix_length` validation on available-prefixes API
* [#3193](https://github.com/netbox-community/netbox/issues/3193) - Fix cable tracing across multiple rear ports
* [#4340](https://github.com/netbox-community/netbox/issues/4340) - Enforce unique constraints for device and virtual machine names in the API
* [#4343](https://github.com/netbox-community/netbox/issues/4343) - Fix Markdown support for tables
* [#4365](https://github.com/netbox-community/netbox/issues/4365) - Fix exception raised on IP address bulk add view
* [#4415](https://github.com/netbox-community/netbox/issues/4415) - Fix duplicate name validation on device model

---

## v2.7.10 (2020-03-10)

**Note:** If your deployment requires any non-core Python packages (such as `napalm`, `django-storages`, or `django-auth-ldap`), list them in a file named `local_requirements.txt` in the NetBox root directory (alongside `requirements.txt`). This will ensure they are detected and re-installed by the upgrade script when the Python virtual environment is rebuilt.

### Enhancements

* [#4217](https://github.com/netbox-community/netbox/issues/4217) - Embed model documentation within web UI
* [#4323](https://github.com/netbox-community/netbox/issues/4323) - Add bulk edit view for power panels
* [#4324](https://github.com/netbox-community/netbox/issues/4324) - Add CSV import view for services
* [#4325](https://github.com/netbox-community/netbox/issues/4324) - Add CSV import view for rack reservations
* [#4332](https://github.com/netbox-community/netbox/issues/4332) - Redirect to a user-friendly error page when CSS/JS resources fail to load

### Bug Fixes

* [#4326](https://github.com/netbox-community/netbox/issues/4326) - Exclude Python modules without Script classes from scripts list
* [#4337](https://github.com/netbox-community/netbox/issues/4337) - Allow bulk editing/deletion of all device components matching a query
* [#4338](https://github.com/netbox-community/netbox/issues/4338) - Catch `AddrFormatError` exception when filtering aggregates/prefixes by an invalid prefix

---

## v2.7.9 (2020-03-06)

**Note:** This release will deploy a Python virtual environment on upgrade in the `venv/` directory. This will require modifying the paths to your Python and gunicorn executables in the systemd service files. For more detail, please see the [upgrade instructions](https://netbox.readthedocs.io/en/stable/installation/upgrading/).

### Enhancements

* [#3949](https://github.com/netbox-community/netbox/issues/3949) - Revised the installation docs and upgrade script to employ a Python virtual environment
* [#4062](https://github.com/netbox-community/netbox/issues/4062) - Enumerate ChoiceField type and value in API
* [#4119](https://github.com/netbox-community/netbox/issues/4119) - Extend upgrade script to clear expired user sessions
* [#4121](https://github.com/netbox-community/netbox/issues/4121) - Add dynamic lookup expressions for all filters
* [#4218](https://github.com/netbox-community/netbox/issues/4218) - Allow negative voltage for DC power feeds
* [#4281](https://github.com/netbox-community/netbox/issues/4281) - Allow filtering device component list views by type
* [#4284](https://github.com/netbox-community/netbox/issues/4284) - Add MRJ21 port and cable types
* [#4290](https://github.com/netbox-community/netbox/issues/4290) - Include device name in tooltip on rack elevations
* [#4305](https://github.com/netbox-community/netbox/issues/4305) - Add 10-inch option for rack width

### Bug Fixes

* [#4274](https://github.com/netbox-community/netbox/issues/4274) - Fix incorrect schema definition of `int` type choicefields
* [#4277](https://github.com/netbox-community/netbox/issues/4277) - Fix filtering of clusters by tenant
* [#4282](https://github.com/netbox-community/netbox/issues/4282) - Fix label on export button for device types
* [#4285](https://github.com/netbox-community/netbox/issues/4285) - Include A/Z termination sites in provider circuits table
* [#4295](https://github.com/netbox-community/netbox/issues/4295) - Fix assignment of parent LAG during interface bulk edit
* [#4298](https://github.com/netbox-community/netbox/issues/4298) - Fix bulk creation of objects with custom fields via REST API
* [#4300](https://github.com/netbox-community/netbox/issues/4300) - Pass "commit" argument when executing scripts via REST API
* [#4301](https://github.com/netbox-community/netbox/issues/4301) - Fix exception when deleting device type with components
* [#4306](https://github.com/netbox-community/netbox/issues/4306) - Fix toggling of device images for all racks in elevations view

---

## v2.7.8 (2020-02-25)

### Enhancements

* [#3145](https://github.com/netbox-community/netbox/issues/3145) - Add a "decommissioning" cable status
* [#4173](https://github.com/netbox-community/netbox/issues/4173) - Return graceful error message when webhook queuing fails
* [#4227](https://github.com/netbox-community/netbox/issues/4227) - Omit internal fields from the change log data
* [#4237](https://github.com/netbox-community/netbox/issues/4237) - Support Jinja2 templating for webhook payload and headers
* [#4262](https://github.com/netbox-community/netbox/issues/4262) - Extend custom scripts to pass the `commit` value via `run()`
* [#4267](https://github.com/netbox-community/netbox/issues/4267) - Denote rack role on rack elevations list

### Bug Fixes

* [#4221](https://github.com/netbox-community/netbox/issues/4221) - Fix exception when deleting a device with interface connections when an interfaces webhook is defined
* [#4222](https://github.com/netbox-community/netbox/issues/4222) - Escape double quotes on encapsulated values during CSV export
* [#4224](https://github.com/netbox-community/netbox/issues/4224) - Fix display of rear device image if front image is not defined
* [#4228](https://github.com/netbox-community/netbox/issues/4228) - Improve fit of device images in rack elevations
* [#4230](https://github.com/netbox-community/netbox/issues/4230) - Fix rack units filtering on elevation endpoint
* [#4232](https://github.com/netbox-community/netbox/issues/4232) - Enforce consistent background striping in rack elevations
* [#4235](https://github.com/netbox-community/netbox/issues/4235) - Fix API representation of `content_type` for export templates
* [#4239](https://github.com/netbox-community/netbox/issues/4239) - Fix exception when selecting all filtered objects during bulk edit
* [#4240](https://github.com/netbox-community/netbox/issues/4240) - Fix exception when filtering foreign keys by NULL
* [#4241](https://github.com/netbox-community/netbox/issues/4241) - Correct IP address hyperlinks on interface view
* [#4246](https://github.com/netbox-community/netbox/issues/4246) - Fix duplication of field attributes when multiple IPNetworkVars are present in a script
* [#4252](https://github.com/netbox-community/netbox/issues/4252) - Fix power port assignment for power outlet templates created via REST API
* [#4272](https://github.com/netbox-community/netbox/issues/4272) - Interface type should be required by API serializer

---

## v2.7.7 (2020-02-20)

**Note:** This release fixes a bug affecting the natural ordering of interfaces. If any interfaces appear unordered in
NetBox, run the following management command to recalculate their naturalized values after upgrading:

```
python3 manage.py renaturalize dcim.Interface
```

### Enhancements

* [#1529](https://github.com/netbox-community/netbox/issues/1529) - Enable display of device images in rack elevations
* [#2511](https://github.com/netbox-community/netbox/issues/2511) - Compare object change to the previous change
* [#3810](https://github.com/netbox-community/netbox/issues/3810) - Preserve slug value when editing existing objects
* [#3840](https://github.com/netbox-community/netbox/issues/3840) - Enhance search function when selecting VLANs for interface assignment
* [#4170](https://github.com/netbox-community/netbox/issues/4170) - Improve color contrast in rack elevation drawings
* [#4206](https://github.com/netbox-community/netbox/issues/4206) - Add RJ-11 console port type
* [#4209](https://github.com/netbox-community/netbox/issues/4209) - Enable filtering interfaces list view by enabled

### Bug Fixes

* [#2519](https://github.com/netbox-community/netbox/issues/2519) - Avoid race condition when provisioning "next available" IPs/prefixes via the API
* [#3967](https://github.com/netbox-community/netbox/issues/3967) - Fix missing migration for interface templates of type "other"
* [#4168](https://github.com/netbox-community/netbox/issues/4168) - Role is not required when creating a virtual machine
* [#4175](https://github.com/netbox-community/netbox/issues/4175) - Fix potential exception when bulk editing objects from a filtered list
* [#4179](https://github.com/netbox-community/netbox/issues/4179) - Site is required when creating a rack group or power panel
* [#4183](https://github.com/netbox-community/netbox/issues/4183) - Fix representation of NaturalOrderingField values in change log
* [#4194](https://github.com/netbox-community/netbox/issues/4194) - Role field should not be required when searching/filtering secrets
* [#4196](https://github.com/netbox-community/netbox/issues/4196) - Fix exception when viewing LLDP neighbors page
* [#4202](https://github.com/netbox-community/netbox/issues/4202) - Prevent reassignment to master device when bulk editing VC member interfaces
* [#4204](https://github.com/netbox-community/netbox/issues/4204) - Fix assignment of mask length when bulk editing prefixes
* [#4211](https://github.com/netbox-community/netbox/issues/4211) - Include trailing text when naturalizing interface names
* [#4213](https://github.com/netbox-community/netbox/issues/4213) - Restore display of tags and custom fields on power feed view

---

## v2.7.6 (2020-02-13)

### Bug Fixes

* [#4166](https://github.com/netbox-community/netbox/issues/4166) - Fix schema migrations to enforce maximum character length for naturalized fields

---

## v2.7.5 (2020-02-13)

**Note:** This release includes several database schema migrations that calculate and store copies of names for certain objects to improve natural ordering performance (see [#3799](https://github.com/netbox-community/netbox/issues/3799)). These migrations may take a few minutes to run if you have a very large number of objects defined in NetBox.

### Enhancements

* [#3766](https://github.com/netbox-community/netbox/issues/3766) - Allow custom script authors to specify the form widget for each variable
* [#3799](https://github.com/netbox-community/netbox/issues/3799) - Greatly improve performance when ordering device components
* [#3984](https://github.com/netbox-community/netbox/issues/3984) - Add support for Redis Sentinel
* [#3986](https://github.com/netbox-community/netbox/issues/3986) - Include position numbers in SVG image when rendering rack elevations
* [#4093](https://github.com/netbox-community/netbox/issues/4093) - Add more status choices for virtual machines
* [#4100](https://github.com/netbox-community/netbox/issues/4100) - Add device filter to component list views
* [#4113](https://github.com/netbox-community/netbox/issues/4113) - Add bulk edit functionality for device type components
* [#4116](https://github.com/netbox-community/netbox/issues/4116) - Enable bulk edit and delete functions for device component list views
* [#4129](https://github.com/netbox-community/netbox/issues/4129) - Add buttons to delete individual device type components

### Bug Fixes

* [#3507](https://github.com/netbox-community/netbox/issues/3507) - Fix filtering IP addresses by multiple devices
* [#3995](https://github.com/netbox-community/netbox/issues/3995) - Make dropdown menus in the navigation bar scrollable on small screens
* [#4083](https://github.com/netbox-community/netbox/issues/4083) - Permit nullifying applicable choice fields via API requests
* [#4089](https://github.com/netbox-community/netbox/issues/4089) - Selection of power outlet type during bulk update is optional
* [#4090](https://github.com/netbox-community/netbox/issues/4090) - Render URL custom fields as links under object view
* [#4091](https://github.com/netbox-community/netbox/issues/4091) - Fix filtering of objects by custom fields using UI search form
* [#4099](https://github.com/netbox-community/netbox/issues/4099) - Linkify interfaces on global interfaces list
* [#4108](https://github.com/netbox-community/netbox/issues/4108) - Avoid extraneous database queries when rendering search forms
* [#4134](https://github.com/netbox-community/netbox/issues/4134) - Device power ports and outlets should inherit type from the parent device type
* [#4137](https://github.com/netbox-community/netbox/issues/4137) - Disable occupied terminations when connecting a cable to a circuit
* [#4138](https://github.com/netbox-community/netbox/issues/4138) - Restore device bay counts in rack elevation diagrams
* [#4146](https://github.com/netbox-community/netbox/issues/4146) - Fix enforcement of secret role assignment for secret decryption
* [#4150](https://github.com/netbox-community/netbox/issues/4150) - Correct YAML rendering of config contexts
* [#4159](https://github.com/netbox-community/netbox/issues/4159) - Fix implementation of Redis caching configuration

---

## v2.7.4 (2020-02-04)

### Enhancements

* [#568](https://github.com/netbox-community/netbox/issues/568) - Allow custom fields to be imported and exported using CSV
* [#2921](https://github.com/netbox-community/netbox/issues/2921) - Replace tags filter with Select2 widget
* [#3313](https://github.com/netbox-community/netbox/issues/3313) - Toggle config context display between JSON and YAML
* [#3886](https://github.com/netbox-community/netbox/issues/3886) - Enable assigning config contexts by cluster and cluster group
* [#4051](https://github.com/netbox-community/netbox/issues/4051) - Disable the `makemigrations` management command

### Bug Fixes

* [#4030](https://github.com/netbox-community/netbox/issues/4030) - Fix exception when bulk editing interfaces (revised)
* [#4043](https://github.com/netbox-community/netbox/issues/4043) - Fix toggling of required fields in custom scripts
* [#4049](https://github.com/netbox-community/netbox/issues/4049) - Restore missing `tags` field in IPAM service serializer
* [#4052](https://github.com/netbox-community/netbox/issues/4052) - Fix error when bulk importing interfaces to virtual machines
* [#4056](https://github.com/netbox-community/netbox/issues/4056) - Repair schema migration for Rack.outer_unit (from #3569)
* [#4067](https://github.com/netbox-community/netbox/issues/4067) - Correct permission checked when creating a rack (vs. editing)
* [#4071](https://github.com/netbox-community/netbox/issues/4071) - Enforce "view tag" permission on individual tag view
* [#4079](https://github.com/netbox-community/netbox/issues/4079) - Fix assignment of power panel when bulk editing power feeds
* [#4084](https://github.com/netbox-community/netbox/issues/4084) - Fix exception when creating an interface with tagged VLANs

---

## v2.7.3 (2020-01-28)

### Enhancements

* [#3310](https://github.com/netbox-community/netbox/issues/3310) - Pre-select site/rack for B side when creating a new cable
* [#3338](https://github.com/netbox-community/netbox/issues/3338) - Include circuit terminations in API representation of circuits
* [#3509](https://github.com/netbox-community/netbox/issues/3509) - Add IP address variables for custom scripts
* [#3978](https://github.com/netbox-community/netbox/issues/3978) - Add VRF filtering to search NAT IP
* [#4005](https://github.com/netbox-community/netbox/issues/4005) - Include timezone context in webhook timestamps

### Bug Fixes

* [#3950](https://github.com/netbox-community/netbox/issues/3950) - Automatically select parent manufacturer when specifying initial device type during device creation
* [#3982](https://github.com/netbox-community/netbox/issues/3982) - Restore tooltip for reservations on rack elevations
* [#3983](https://github.com/netbox-community/netbox/issues/3983) - Permit the creation of multiple unnamed devices
* [#3989](https://github.com/netbox-community/netbox/issues/3989) - Correct HTTP content type assignment for webhooks
* [#3999](https://github.com/netbox-community/netbox/issues/3999) - Do not filter child results by null if non-required parent fields are blank
* [#4008](https://github.com/netbox-community/netbox/issues/4008) - Toggle rack elevation face using front/rear strings
* [#4017](https://github.com/netbox-community/netbox/issues/4017) - Remove redundant tenant field from cluster form
* [#4019](https://github.com/netbox-community/netbox/issues/4019) - Restore border around background devices in rack elevations
* [#4022](https://github.com/netbox-community/netbox/issues/4022) - Fix display of assigned IPs when filtering device interfaces
* [#4025](https://github.com/netbox-community/netbox/issues/4025) - Correct display of cable status (various places)
* [#4027](https://github.com/netbox-community/netbox/issues/4027) - Repair schema migration for #3569 to convert IP addresses with DHCP status
* [#4028](https://github.com/netbox-community/netbox/issues/4028) - Correct URL patterns to match Unicode characters in tag slugs
* [#4030](https://github.com/netbox-community/netbox/issues/4030) - Fix exception when setting interfaces to tagged mode in bulk
* [#4033](https://github.com/netbox-community/netbox/issues/4033) - Restore missing comments field label of various bulk edit forms

---

## v2.7.2 (2020-01-21)

### Enhancements

* [#3135](https://github.com/netbox-community/netbox/issues/3135) - Documented power modelling
* [#3842](https://github.com/netbox-community/netbox/issues/3842) - Add 802.11ax interface type
* [#3954](https://github.com/netbox-community/netbox/issues/3954) - Add `device_bays` filter for devices and device types

### Bug Fixes

* [#3721](https://github.com/netbox-community/netbox/issues/3721) - Allow Unicode characters in tag slugs
* [#3923](https://github.com/netbox-community/netbox/issues/3923) - Indicate validation failure when using SSH-style RSA keys
* [#3951](https://github.com/netbox-community/netbox/issues/3951) - Fix exception in webhook worker due to missing constant
* [#3953](https://github.com/netbox-community/netbox/issues/3953) - Fix validation error when creating child devices
* [#3960](https://github.com/netbox-community/netbox/issues/3960) - Fix legacy device status choice
* [#3962](https://github.com/netbox-community/netbox/issues/3962) - Fix display of unnamed devices in rack elevations
* [#3963](https://github.com/netbox-community/netbox/issues/3963) - Restore tooltip for devices in rack elevations
* [#3964](https://github.com/netbox-community/netbox/issues/3964) - Show borders around devices in rack elevations
* [#3965](https://github.com/netbox-community/netbox/issues/3965) - Indicate the presence of "background" devices in rack elevations
* [#3966](https://github.com/netbox-community/netbox/issues/3966) - Fix filtering of device components by region/site
* [#3967](https://github.com/netbox-community/netbox/issues/3967) - Resolve migration of "other" interface type

---

## v2.7.1 (2020-01-16)

### Bug Fixes

* [#3941](https://github.com/netbox-community/netbox/issues/3941) - Fixed exception when attempting to assign IP to interface
* [#3943](https://github.com/netbox-community/netbox/issues/3943) - Prevent rack elevation links from opening new tabs/windows
* [#3944](https://github.com/netbox-community/netbox/issues/3944) - Fix AttributeError exception when viewing prefixes list

---

## v2.7.0 (2020-01-16)

**Note:** This release completely removes the topology map feature ([#2745](https://github.com/netbox-community/netbox/issues/2745)).

**Note:** NetBox v2.7 is the last major release that will support Python 3.5. Beginning with NetBox v2.8, Python 3.6 or
higher will be required.

### New Features

#### Enhanced Device Type Import ([#451](https://github.com/netbox-community/netbox/issues/451))

NetBox now supports the import of device types and related component templates using definitions written in YAML or
JSON. For example, the following will create a new device type with four network interfaces, two power ports, and a
console port:

```yaml
manufacturer: Acme
model: Packet Shooter 9000
slug: packet-shooter-9000
u_height: 1
interfaces:
  - name: ge-0/0/0
    type: 1000base-t
  - name: ge-0/0/1
    type: 1000base-t
  - name: ge-0/0/2
    type: 1000base-t
  - name: ge-0/0/3
    type: 1000base-t
power-ports:
  - name: PSU0
  - name: PSU1
console-ports:
  - name: Console
```

This new functionality replaces the old CSV-based import form, which did not allow for bulk import of component
templates.

#### Bulk Import of Device Components ([#822](https://github.com/netbox-community/netbox/issues/822))

Device components such as console ports, power ports, and interfaces can now be imported in bulk to multiple devices in
CSV format. Here's an example showing the bulk import of interfaces to several devices:

```
device,name,type
Switch1,Vlan100,Virtual
Switch1,Vlan200,Virtual
Switch2,Vlan100,Virtual
Switch2,Vlan200,Virtual
```

The import form for each type of device component is available under the "Devices" item in the navigation menu.

#### External File Storage ([#1814](https://github.com/netbox-community/netbox/issues/1814))

In prior releases, the only option for storing uploaded files (e.g. image attachments) was to save them to the local
filesystem on the NetBox server. This release introduces support for several remote storage backends provided by the
[`django-storages`](https://django-storages.readthedocs.io/en/stable/) library. These include:

* Amazon S3
* ApacheLibcloud
* Azure Storage
* netbox-community Spaces
* Dropbox
* FTP
* Google Cloud Storage
* SFTP

To enable remote file storage, first install the `django-storages` package:

```
pip install django-storages
```

Then, set the appropriate storage backend and its configuration in `configuration.py`. Here's an example using Amazon
S3:

```python
STORAGE_BACKEND = 'storages.backends.s3boto3.S3Boto3Storage'
STORAGE_CONFIG = {
    'AWS_ACCESS_KEY_ID': '<Key>',
    'AWS_SECRET_ACCESS_KEY': '<Secret>',
    'AWS_STORAGE_BUCKET_NAME': 'netbox',
    'AWS_S3_REGION_NAME': 'eu-west-1',
}
```

Thanks to [@steffann](https://github.com/steffann) for contributing this work!

#### Rack Elevations Rendered via SVG ([#2248](https://github.com/netbox-community/netbox/issues/2248))

NetBox v2.7 introduces a new method of rendering rack elevations as an
[SVG image](https://en.wikipedia.org/wiki/Scalable_Vector_Graphics) via a REST API endpoint. This replaces the prior
method of rendering elevations using pure HTML and CSS, which was cumbersome and had several shortcomings. Rendering
rack elevations as SVG images via the REST API allows users to retrieve and make use of the drawings in their own
tooling. This also opens the door to other feature requests related to rack elevations in the NetBox backlog.

This feature implements a new REST API endpoint:

```
/api/dcim/racks/<id>/elevation/
```

By default, this endpoint returns a paginated JSON response representing each rack unit in the given elevation. This is
the same response returned by the existing rack units detail endpoint at `/api/dcim/racks/<id>/units/`, which will be
removed in v2.8 (see [#3753](https://github.com/netbox-community/netbox/issues/3753)).

To render the elevation as an SVG image, include the `render=svg` query parameter in the request. You may also control
the width and height of the elevation drawing (in pixels) by passing the `unit_width` and `unit_height` parameters. (The
default values for these parameters are 230 and 20, respectively.) Additionally, the `face` parameter may be used to
request either the `front` or `rear` of the elevation. Below is in example request:

```
/api/dcim/racks/<id>/elevation/?render=svg&face=rear&unit_width=300&unit_height=35
```

Thanks to [@hellerve](https://github.com/hellerve) for doing the heavy lifting on this!

### Changes

#### Topology Maps Removed ([#2745](https://github.com/netbox-community/netbox/issues/2745))

The topology maps feature has been removed to help focus NetBox development efforts. Please replicate any required data
to another source before upgrading NetBox to v2.7, as any existing topology maps will be deleted.

#### Supervisor Replaced with systemd ([#2902](https://github.com/netbox-community/netbox/issues/2902))

The NetBox [installation documentation](https://netbox.readthedocs.io/en/stable/installation/) has been updated to
provide instructions for managing the WSGI and RQ services using systemd instead of supervisor. This removes the need to
install supervisor and simplifies administration of the processes.

#### Redis Configuration ([#3282](https://github.com/netbox-community/netbox/issues/3282))

NetBox v2.6 introduced request caching and added the `CACHE_DATABASE` option to the existing `REDIS` database
configuration parameter. This did not, however, allow for using two different Redis connections for the separate caching
and webhook queuing functions. This release modifies the `REDIS` parameter to accept two discrete subsections named
`webhooks` and `caching`. This requires modification of the `REDIS` parameter in `configuration.py` as follows:

Old Redis configuration:

```python
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

New Redis configuration:

```python
REDIS = {
    'webhooks': {
        'HOST': 'redis.example.com',
        'PORT': 1234,
        'PASSWORD': 'foobar',
        'DATABASE': 0,
        'DEFAULT_TIMEOUT': 300,
        'SSL': False,
    },
    'caching': {
        'HOST': 'localhost',
        'PORT': 6379,
        'PASSWORD': '',
        'DATABASE': 1,
        'DEFAULT_TIMEOUT': 300,
        'SSL': False,
    }
}
```

Note that the `CACHE_DATABASE` parameter has been removed and the connection settings have been duplicated for both
`webhooks` and `caching`. This allows the user to make use of separate Redis instances if desired. It is fine to use the
same Redis service for both functions, although the database identifiers should be different.

#### WEBHOOKS_ENABLED Configuration Setting Removed ([#3408](https://github.com/netbox-community/netbox/issues/3408))

As `django-rq` is now a required library, NetBox assumes that the RQ worker process is running. The installation and
upgrade documentation has been updated to reflect this, and the `WEBHOOKS_ENABLED` configuration parameter is no longer
used. Please ensure that both the NetBox WSGI service and the RQ worker process are running on all production
installations.

#### API Choice Fields Now Use String Values ([#3569](https://github.com/netbox-community/netbox/issues/3569))

NetBox's REST API presents fields which reference a particular choice as a dictionary with two keys: `value` and
`label`. In previous versions, `value` was an integer which represented a particular choice in the database. This has
been changed to a more human-friendly "slug" string, which is essentially a simplified version of the choice's `label`.

For example, The site model's `status` field was previously represented as:

```json
"status": {
    "value": 1,
    "label": "Active"
},
```

In NetBox v2.7, it now looks like this:

```json
"status": {
    "value": "active",
    "label": "Active",
    "id": 1
},
```

This change allows for much more intuitive representation and manipulation of values, and removes the need for API
consumers to maintain local mappings of static integer values.

Note that that all v2.7 releases will continue to accept the legacy integer values in write requests (`POST`, `PUT`, and
`PATCH`) to maintain backward compatibility. Additionally, the legacy numeric identifier is conveyed in the `id` field
for convenient reference as consumers adopt to the new string values. This behavior will be discontinued in NetBox v2.8.

### Enhancements

* [#33](https://github.com/netbox-community/netbox/issues/33) - Add ability to clone objects (pre-populate form fields)
* [#648](https://github.com/netbox-community/netbox/issues/648) - Pre-populate form fields when selecting "create and
  add another"
* [#792](https://github.com/netbox-community/netbox/issues/792) - Add power port and power outlet types
* [#1865](https://github.com/netbox-community/netbox/issues/1865) - Add console port and console server port types
* [#2669](https://github.com/netbox-community/netbox/issues/2669) - Relax uniqueness constraint on device and VM names
* [#2902](https://github.com/netbox-community/netbox/issues/2902) - Replace `supervisord` with `systemd`
* [#3455](https://github.com/netbox-community/netbox/issues/3455) - Add tenant assignment to virtual machine clusters
* [#3520](https://github.com/netbox-community/netbox/issues/3520) - Add Jinja2 template support for graphs
* [#3525](https://github.com/netbox-community/netbox/issues/3525) - Enable IP address filtering using multiple address
  parameters
* [#3564](https://github.com/netbox-community/netbox/issues/3564) - Add list views for all device components
* [#3538](https://github.com/netbox-community/netbox/issues/3538) - Introduce a REST API endpoint for executing custom
  scripts
* [#3655](https://github.com/netbox-community/netbox/issues/3655) - Add `description` field to organizational models
* [#3664](https://github.com/netbox-community/netbox/issues/3664) - Enable applying configuration contexts by tags
* [#3706](https://github.com/netbox-community/netbox/issues/3706) - Increase `available_power` maximum value on
  PowerFeed
* [#3731](https://github.com/netbox-community/netbox/issues/3731) - Change Graph.type to a ContentType foreign key field
* [#3801](https://github.com/netbox-community/netbox/issues/3801) - Use YAML for export of device types

### Bug Fixes

* [#3830](https://github.com/netbox-community/netbox/issues/3830) - Ensure deterministic ordering for all models
* [#3900](https://github.com/netbox-community/netbox/issues/3900) - Fix exception when deleting device types
* [#3914](https://github.com/netbox-community/netbox/issues/3914) - Fix interface filter field when unauthenticated
* [#3919](https://github.com/netbox-community/netbox/issues/3919) - Fix utilization graph extending out of bounds when
  utilization > 100%
* [#3927](https://github.com/netbox-community/netbox/issues/3927) - Fix exception when deleting devices with secrets
  assigned
* [#3930](https://github.com/netbox-community/netbox/issues/3930) - Fix API rendering of the `family` field for
  aggregates

### Bug Fixes (From Beta)

* [#3868](https://github.com/netbox-community/netbox/issues/3868) - Fix creation of interfaces for virtual machines
* [#3878](https://github.com/netbox-community/netbox/issues/3878) - Fix database migration for cable status field

### API Changes

* Choice fields now use human-friendly strings for their values instead of integers (see
  [#3569](https://github.com/netbox-community/netbox/issues/3569)).
* Introduced the `/api/extras/scripts/` endpoint for retrieving and executing custom scripts
* circuits.CircuitType: Added field `description`
* dcim.ConsolePort: Added field `type`
* dcim.ConsolePortTemplate: Added field `type`
* dcim.ConsoleServerPort: Added field `type`
* dcim.ConsoleServerPortTemplate: Added field `type`
* dcim.DeviceRole: Added field `description`
* dcim.PowerPort: Added field `type`
* dcim.PowerPortTemplate: Added field `type`
* dcim.PowerOutlet: Added field `type`
* dcim.PowerOutletTemplate: Added field `type`
* dcim.RackRole: Added field `description`
* extras.Graph: Added field `template_language` (to indicate `django` or `jinja2`)
* extras.Graph: The `type` field has been changed to a content type foreign key. Models are specified as
  `<app>.<model>`; e.g. `dcim.site`.
* ipam.Role: Added field `description`
* secrets.SecretRole: Added field `description`
* virtualization.Cluster: Added field `tenant`
