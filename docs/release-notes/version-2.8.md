# NetBox v2.8

## v2.8.0 (FUTURE)

### New Features

#### Remote Authentication Support ([#2328](https://github.com/netbox-community/netbox/issues/2328))

Several new configuration parameters provide support for authenticating an incoming request based on the value of a specific HTTP header. This can be leveraged to employ remote authentication via an nginx or Apache plugin, directing NetBox to create and configure a local user account as needed. The configuration parameters are:

* `REMOTE_AUTH_ENABLED` - Enables remote authentication (disabled by default)
* `REMOTE_AUTH_HEADER` - The name of the HTTP header which conveys the username
* `REMOTE_AUTH_AUTO_CREATE_USER` - Enables the automatic creation of new users (disabled by default)
* `REMOTE_AUTH_DEFAULT_GROUPS` - A list of groups to assign newly created users
* `REMOTE_AUTH_DEFAULT_PERMISSIONS` - A list of permissions to assign newly created users

If further customization of remote authentication is desired (for instance, if you want to pass group/permission information via HTTP headers as well), NetBox allows you to inject a custom [Django authentication backend](https://docs.djangoproject.com/en/stable/topics/auth/customizing/) to retain full control over the authentication and configuration of remote users.

### Enhancements

* [#1754](https://github.com/netbox-community/netbox/issues/1754) - Added support for nested rack groups
* [#3939](https://github.com/netbox-community/netbox/issues/3939) - Added support for nested tenant groups
* [#4195](https://github.com/netbox-community/netbox/issues/4195) - Enabled application logging (see [logging configuration](../configuration/optional-settings.md#logging))

### API Changes

* The `_choices` API endpoints have been removed. Instead, use an `OPTIONS` request to a model's endpoint to view the available values for all fields. ([#3416](https://github.com/netbox-community/netbox/issues/3416))
* The `id__in` filter has been removed. Use the format `?id=1&id=2` instead. ([#4313](https://github.com/netbox-community/netbox/issues/4313))
* dcim.Rack: The `/api/dcim/racks/<pk>/units/` endpoint has been replaced with `/api/dcim/racks/<pk>/elevation/`.

### Other Changes

* [#4081](https://github.com/netbox-community/netbox/issues/4081) - The `family` field has been removed from the Aggregate, Prefix, and IPAddress models
