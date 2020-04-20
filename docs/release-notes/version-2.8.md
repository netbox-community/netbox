# NetBox v2.8

## v2.8.1 (FUTURE)

### Enhancements

* [#4464](https://github.com/netbox-community/netbox/issues/4464) - Add 21-inch rack width (ETSI)

### Bug Fixes

* [#4361](https://github.com/netbox-community/netbox/issues/4361) - Fix Type of `connection_state` in swagger schema.
* [#4489](https://github.com/netbox-community/netbox/issues/4489) - Fix display of parent/child role on device type view
* [#4496](https://github.com/netbox-community/netbox/issues/4496) - Fix exception when validating certain models via REST API

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
