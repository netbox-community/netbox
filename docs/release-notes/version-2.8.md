# NetBox v2.8

## v2.8.9 (2020-08-04)

### Enhancements

* [#4898](https://github.com/netbox-community/netbox/issues/4898) - Add MAC address search field to interfaces list
* [#4899](https://github.com/netbox-community/netbox/issues/4899) - Add MAC address column to interfaces table

### Bug Fixes

* [#4455](https://github.com/netbox-community/netbox/issues/4455) - Fix ordering of prefixes beneath aggregate when available space is hidden
* [#4875](https://github.com/netbox-community/netbox/issues/4875) - Fix documentation for image attachments
* [#4876](https://github.com/netbox-community/netbox/issues/4876) - Fix labels for sites in staging or decommissioning status
* [#4880](https://github.com/netbox-community/netbox/issues/4880) - Fix removal of tagged VLANs if not assigned in bulk interface editing
* [#4887](https://github.com/netbox-community/netbox/issues/4887) - Don't disable NAPALM tabs when device has no primary IP
* [#4894](https://github.com/netbox-community/netbox/issues/4894) - Fix display of device/VM counts on platforms list
* [#4895](https://github.com/netbox-community/netbox/issues/4895) - Force UTF-8 encoding when embedding model documentation
* [#4910](https://github.com/netbox-community/netbox/issues/4910) - Unpin redis dependency to fix exception in RQ worker
* [#4926](https://github.com/netbox-community/netbox/issues/4926) - Fix ordering of VM interfaces in REST API endpoint
* [#4927](https://github.com/netbox-community/netbox/issues/4927) - Fix validation error when updating an existing secret
* [#4929](https://github.com/netbox-community/netbox/issues/4929) - Correct log message when creating a new object

---

## v2.8.8 (2020-07-21)

### Enhancements

* [#4805](https://github.com/netbox-community/netbox/issues/4805) - Improve handling of plugin loading errors
* [#4829](https://github.com/netbox-community/netbox/issues/4829) - Add NEMA 15 power port and outlet types
* [#4831](https://github.com/netbox-community/netbox/issues/4831) - Allow NAPALM to resolve device name when primary IP is not set
* [#4854](https://github.com/netbox-community/netbox/issues/4854) - Add staging and decommissioning statuses for sites

### Bug Fixes

* [#3240](https://github.com/netbox-community/netbox/issues/3240) - Correct OpenAPI definition for available-prefixes endpoint
* [#4595](https://github.com/netbox-community/netbox/issues/4595) - Ensure consistent display of non-racked and child devices on rack view
* [#4803](https://github.com/netbox-community/netbox/issues/4803) - Return IP family (4 or 6) as integer rather than string
* [#4821](https://github.com/netbox-community/netbox/issues/4821) - Restrict group options by selected site when bulk editing VLANs
* [#4835](https://github.com/netbox-community/netbox/issues/4835) - Support passing multiple initial values for multiple choice fields
* [#4838](https://github.com/netbox-community/netbox/issues/4838) - Fix rack power utilization display for racks without devices
* [#4851](https://github.com/netbox-community/netbox/issues/4851) - Show locally connected peer on circuit terminations
* [#4856](https://github.com/netbox-community/netbox/issues/4856) - Redirect user back to circuit after connecting a termination
* [#4872](https://github.com/netbox-community/netbox/issues/4872) - Enable filtering virtual machine interfaces by tag

---

## v2.8.7 (2020-07-02)

### Enhancements

* [#4796](https://github.com/netbox-community/netbox/issues/4796) - Introduce configuration parameters for default rack elevation size
* [#4802](https://github.com/netbox-community/netbox/issues/4802) - Allow changing page size when displaying only a single page of results

### Bug Fixes

* [#4695](https://github.com/netbox-community/netbox/issues/4695) - Expose cable termination type choices in OpenAPI spec
* [#4708](https://github.com/netbox-community/netbox/issues/4708) - Relax connection constraints for multi-position rear ports
* [#4766](https://github.com/netbox-community/netbox/issues/4766) - Fix redirect after login when `next` is not specified
* [#4771](https://github.com/netbox-community/netbox/issues/4771) - Fix add/remove tag population when bulk editing objects
* [#4772](https://github.com/netbox-community/netbox/issues/4772) - Fix "brief" format for the secrets REST API endpoint
* [#4774](https://github.com/netbox-community/netbox/issues/4774) - Fix exception when deleting a device with device bays
* [#4775](https://github.com/netbox-community/netbox/issues/4775) - Allow selecting an alternate device type when creating component templates

---

## v2.8.6 (2020-06-15)

### Enhancements

* [#4698](https://github.com/netbox-community/netbox/issues/4698) - Improve display of template code for object in admin UI
* [#4717](https://github.com/netbox-community/netbox/issues/4717) - Introduce `ALLOWED_URL_SCHEMES` configuration parameter to mitigate dangerous hyperlinks
* [#4744](https://github.com/netbox-community/netbox/issues/4744) - Hide "IP addresses" tab when viewing a container prefix
* [#4755](https://github.com/netbox-community/netbox/issues/4755) - Enable creation of rack reservations directly from navigation menu
* [#4761](https://github.com/netbox-community/netbox/issues/4761) - Enable tag assignment during bulk creation of IP addresses

### Bug Fixes

* [#4674](https://github.com/netbox-community/netbox/issues/4674) - Fix API definition for available prefix and IP address endpoints
* [#4702](https://github.com/netbox-community/netbox/issues/4702) - Catch IntegrityError exception when adding a non-unique secret
* [#4707](https://github.com/netbox-community/netbox/issues/4707) - Fix `prefix_count` population on VLAN API serializer
* [#4710](https://github.com/netbox-community/netbox/issues/4710) - Fix merging of form fields among custom scripts
* [#4725](https://github.com/netbox-community/netbox/issues/4725) - Fix "brief" rendering of various REST API endpoints
* [#4736](https://github.com/netbox-community/netbox/issues/4736) - Add cable trace endpoints for pass-through ports
* [#4737](https://github.com/netbox-community/netbox/issues/4737) - Fix display of role labels in virtual machines table
* [#4743](https://github.com/netbox-community/netbox/issues/4743) - Allow users to create "next available" IPs without needing permission to create prefixes
* [#4756](https://github.com/netbox-community/netbox/issues/4756) - Filter parent group by site when creating rack groups
* [#4760](https://github.com/netbox-community/netbox/issues/4760) - Enable power port template assignment when bulk editing power outlet templates

---

## v2.8.5 (2020-05-26)

**Note:** The minimum required version of PostgreSQL is now 9.6.

### Enhancements

* [#4650](https://github.com/netbox-community/netbox/issues/4650) - Expose `INTERNAL_IPS` configuration parameter
* [#4651](https://github.com/netbox-community/netbox/issues/4651) - Add `csrf_token` context for plugin templates
* [#4652](https://github.com/netbox-community/netbox/issues/4652) - Add permissions context for plugin templates
* [#4665](https://github.com/netbox-community/netbox/issues/4665) - Add NEMA L14 and L21 power port/outlet types
* [#4672](https://github.com/netbox-community/netbox/issues/4672) - Set default color for rack and devices roles

### Bug Fixes

* [#3304](https://github.com/netbox-community/netbox/issues/3304) - Fix caching invalidation issue related to device/virtual machine primary IP addresses
* [#4525](https://github.com/netbox-community/netbox/issues/4525) - Allow passing initial data to custom script MultiObjectVar
* [#4644](https://github.com/netbox-community/netbox/issues/4644) - Fix ordering of services table by parent
* [#4646](https://github.com/netbox-community/netbox/issues/4646) - Correct UI link for reports with custom name
* [#4647](https://github.com/netbox-community/netbox/issues/4647) - Fix caching invalidation issue related to assigning new IP addresses to interfaces
* [#4648](https://github.com/netbox-community/netbox/issues/4648) - Fix bulk CSV import of child devices
* [#4649](https://github.com/netbox-community/netbox/issues/4649) - Fix interface assignment for bulk-imported IP addresses
* [#4676](https://github.com/netbox-community/netbox/issues/4676) - Set default value of `REMOTE_AUTH_AUTO_CREATE_USER` as `False` in docs
* [#4684](https://github.com/netbox-community/netbox/issues/4684) - Respect `comments` field when importing device type in YAML/JSON format

---

## v2.8.4 (2020-05-13)

### Enhancements

* [#4632](https://github.com/netbox-community/netbox/issues/4632) - Extend email configuration parameters to support SSL/TLS

### Bug Fixes

* [#4598](https://github.com/netbox-community/netbox/issues/4598) - Display error message when invalid cable length is specified
* [#4604](https://github.com/netbox-community/netbox/issues/4604) - Multi-position rear ports may only be connected to other rear ports
* [#4607](https://github.com/netbox-community/netbox/issues/4607) - Missing Contextual help for API Tokens
* [#4613](https://github.com/netbox-community/netbox/issues/4613) - Fix tag assignment on config contexts (regression from #4527)
* [#4617](https://github.com/netbox-community/netbox/issues/4617) - Restore IP prefix depth notation in list view
* [#4629](https://github.com/netbox-community/netbox/issues/4629) - Replicate assigned interface when cloning IP addresses
* [#4633](https://github.com/netbox-community/netbox/issues/4633) - Bump django-rq to v2.3.2 to fix ImportError with rq 1.4.0
* [#4634](https://github.com/netbox-community/netbox/issues/4634) - Inventory Item List view exception caused by incorrect accessor definition 

---

## v2.8.3 (2020-05-06)

### Bug Fixes

* [#4593](https://github.com/netbox-community/netbox/issues/4593) - Fix AttributeError exception when viewing object lists as a non-authenticated user

---

## v2.8.2 (2020-05-06)

### Enhancements

* [#492](https://github.com/netbox-community/netbox/issues/492) - Enable toggling and rearranging table columns
* [#3147](https://github.com/netbox-community/netbox/issues/3147) - Allow specifying related objects by arbitrary attribute during CSV import
* [#3064](https://github.com/netbox-community/netbox/issues/3064) - Include tags in object lists as a toggleable table column
* [#3294](https://github.com/netbox-community/netbox/issues/3294) - Implement mechanism for storing user preferences
* [#4421](https://github.com/netbox-community/netbox/issues/4421) - Retain user's preference for config context format
* [#4502](https://github.com/netbox-community/netbox/issues/4502) - Enable configuration of proxies for outbound HTTP requests
* [#4531](https://github.com/netbox-community/netbox/issues/4531) - Retain user's preference for page length
* [#4554](https://github.com/netbox-community/netbox/issues/4554) - Add ServerTech's HDOT Cx power outlet type

### Bug Fixes

* [#4527](https://github.com/netbox-community/netbox/issues/4527) - Fix assignment of certain tags to config contexts
* [#4545](https://github.com/netbox-community/netbox/issues/4545) - Removed all squashed schema migrations to allow direct upgrades from very old releases
* [#4548](https://github.com/netbox-community/netbox/issues/4548) - Fix tracing cables through a single RearPort
* [#4549](https://github.com/netbox-community/netbox/issues/4549) - Fix encoding unicode webhook body data
* [#4556](https://github.com/netbox-community/netbox/issues/4556) - Update form for adding devices to clusters
* [#4578](https://github.com/netbox-community/netbox/issues/4578) - Prevent setting 0U height on device type with racked instances
* [#4584](https://github.com/netbox-community/netbox/issues/4584) - Ensure consistent support for filtering objects by `id` across all REST API endpoints
* [#4588](https://github.com/netbox-community/netbox/issues/4588) - Restore ability to add/remove tags on services, virtual chassis in bulk

---

## v2.8.1 (2020-04-23)

### Notes

In accordance with the fix in [#4459](https://github.com/netbox-community/netbox/issues/4459), users that are experiencing invalid nested data with
regions, rack groups, or tenant groups can perform a one-time operation using the NetBox shell to rebuild the correct nested relationships after upgrading:

```text
$ python netbox/manage.py nbshell
### NetBox interactive shell (localhost)
### Python 3.6.4 | Django 3.0.5 | NetBox 2.8.1
### lsmodels() will show available models. Use help(<model>) for more info.
>>> Region.objects.rebuild()
>>> RackGroup.objects.rebuild()
>>> TenantGroup.objects.rebuild()
```

### Enhancements

* [#4464](https://github.com/netbox-community/netbox/issues/4464) - Add 21-inch rack width (ETSI)

### Bug Fixes

* [#2994](https://github.com/netbox-community/netbox/issues/2994) - Prevent modifying termination points of existing cable to ensure end-to-end path integrity
* [#3356](https://github.com/netbox-community/netbox/issues/3356) - Correct Swagger schema specification for the available prefixes/IPs API endpoints
* [#4139](https://github.com/netbox-community/netbox/issues/4139) - Enable assigning all relevant attributes during bulk device/VM component creation
* [#4336](https://github.com/netbox-community/netbox/issues/4336) - Ensure interfaces without a subinterface ID are ordered before subinterface zero
* [#4361](https://github.com/netbox-community/netbox/issues/4361) - Fix Type of `connection_state` in Swagger schema
* [#4388](https://github.com/netbox-community/netbox/issues/4388) - Fix detection of connected endpoints when connecting rear ports
* [#4459](https://github.com/netbox-community/netbox/issues/4459) - Fix caching issue resulting in erroneous nested data for regions, rack groups, and tenant groups
* [#4489](https://github.com/netbox-community/netbox/issues/4489) - Fix display of parent/child role on device type view
* [#4496](https://github.com/netbox-community/netbox/issues/4496) - Fix exception when validating certain models via REST API
* [#4510](https://github.com/netbox-community/netbox/issues/4510) - Enforce address family for device primary IPv4/v6 addresses

---

## v2.8.0 (2020-04-13)

**NOTE:** Beginning with release 2.8.0, NetBox requires Python 3.6 or later.

### New Features (Beta)

This releases introduces two new features in beta status. While they are expected to be functional, their precise implementation is subject to change during the v2.8 release cycle. It is recommended to wait until NetBox v2.9 to deploy them in production.

#### Remote Authentication Support ([#2328](https://github.com/netbox-community/netbox/issues/2328))

Several new configuration parameters provide support for authenticating an incoming request based on the value of a specific HTTP header. This can be leveraged to employ remote authentication via an nginx or Apache plugin, directing NetBox to create and configure a local user account as needed. The configuration parameters are:

* `REMOTE_AUTH_ENABLED` - Enables remote authentication (disabled by default)
* `REMOTE_AUTH_HEADER` - The name of the HTTP header which conveys the username
* `REMOTE_AUTH_AUTO_CREATE_USER` - Enables the automatic creation of new users (disabled by default)
* `REMOTE_AUTH_DEFAULT_GROUPS` - A list of groups to assign newly created users
* `REMOTE_AUTH_DEFAULT_PERMISSIONS` - A list of permissions to assign newly created users

If further customization of remote authentication is desired (for instance, if you want to pass group/permission information via HTTP headers as well), NetBox allows you to inject a custom [Django authentication backend](https://docs.djangoproject.com/en/stable/topics/auth/customizing/) to retain full control over the authentication and configuration of remote users.

#### Plugins ([#3351](https://github.com/netbox-community/netbox/issues/3351))

This release introduces support for custom plugins, which can be used to extend NetBox's functionality beyond what the core product provides. For example, plugins can be used to:

* Add new Django models
* Provide new views with custom templates
* Inject custom template into object views
* Introduce new API endpoints
* Add custom request/response middleware

For NetBox plugins to be recognized, they must be installed and added by name to the `PLUGINS` configuration parameter. (Plugin support is disabled by default.) Plugins can be configured under the `PLUGINS_CONFIG` parameter. More information can be found the in the [plugins documentation](https://netbox.readthedocs.io/en/stable/plugins/).

### Enhancements

* [#1754](https://github.com/netbox-community/netbox/issues/1754) - Added support for nested rack groups
* [#3939](https://github.com/netbox-community/netbox/issues/3939) - Added support for nested tenant groups
* [#4078](https://github.com/netbox-community/netbox/issues/4078) - Standardized description fields across all models
* [#4195](https://github.com/netbox-community/netbox/issues/4195) - Enabled application logging (see [logging configuration](https://netbox.readthedocs.io/en/stable/configuration/optional-settings/#logging))

### Bug Fixes

* [#4474](https://github.com/netbox-community/netbox/issues/4474) - Fix population of device types when bulk editing devices
* [#4476](https://github.com/netbox-community/netbox/issues/4476) - Correct typo in slugs for Infiniband interface types

### API Changes

* The `_choices` API endpoints have been removed. Instead, use an `OPTIONS` request to a model's endpoint to view the available values for all fields. ([#3416](https://github.com/netbox-community/netbox/issues/3416))
* The `id__in` filter has been removed from all models ([#4313](https://github.com/netbox-community/netbox/issues/4313)). Use the format `?id=1&id=2` instead.
* dcim.Manufacturer: Added a `description` field
* dcim.Platform: Added a `description` field
* dcim.Rack: The `/api/dcim/racks/<pk>/units/` endpoint has been replaced with `/api/dcim/racks/<pk>/elevation/`.
* dcim.RackGroup: Added a `description` field
* dcim.Region: Added a `description` field
* extras.Tag: Renamed `comments` to `description`; truncated length to 200 characters; removed Markdown rendering
* ipam.RIR: Added a `description` field
* ipam.VLANGroup: Added a `description` field
* tenancy.TenantGroup: Added a `description` field
* virtualization.ClusterGroup: Added a `description` field
* virtualization.ClusterType: Added a `description` field

### Other Changes

* [#4081](https://github.com/netbox-community/netbox/issues/4081) - The `family` field has been removed from the Aggregate, Prefix, and IPAddress models. The field remains available in the API representations of these models, however the column has been removed from the database table.
