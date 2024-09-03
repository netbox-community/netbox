# NetBox Configuration

## Configuration File

NetBox's configuration file contains all the important parameters which control how NetBox functions: database settings, security controls, user preferences, and so on. While the default configuration suffices out of the box for most use cases, there are a few [required parameters](./required-parameters.md) which **must** be defined during installation. 

The configuration file is loaded from `$INSTALL_ROOT/netbox/netbox/configuration.py` by default. An example configuration is provided at `configuration_example.py`, which you may copy to use as your default config. Note that a configuration file must be defined; NetBox will not run without one.

!!! info "Customizing the Configuration Module"
    A custom configuration module may be specified by setting the `NETBOX_CONFIGURATION` environment variable. This must be a dotted path to the desired Python module. For example, a file named `my_config.py` in the same directory as `settings.py` would be referenced as `netbox.my_config`.

    To keep things simple, the NetBox documentation refers to the configuration file simply as `configuration.py`.

Some configuration parameters may alternatively be defined either in `configuration.py` or within the administrative section of the user interface. Settings which are "hard-coded" in the configuration file take precedence over those defined via the UI.

## Dynamic Configuration Parameters

Some configuration parameters are primarily controlled via NetBox's admin interface (under Admin > Extras > Configuration Revisions). These are noted where applicable in the documentation. These settings may also be overridden in `configuration.py` to prevent them from being modified via the UI. A complete list of supported parameters is provided below:

* [`ALLOWED_URL_SCHEMES`](./security.md#allowed_url_schemes)
* [`BANNER_BOTTOM`](./miscellaneous.md#banner_bottom)
* [`BANNER_LOGIN`](./miscellaneous.md#banner_login)
* [`BANNER_TOP`](./miscellaneous.md#banner_top)
* [`CHANGELOG_RETENTION`](./miscellaneous.md#changelog_retention)
* [`CUSTOM_VALIDATORS`](./data-validation.md#custom_validators)
* [`DEFAULT_USER_PREFERENCES`](./default-values.md#default_user_preferences)
* [`ENFORCE_GLOBAL_UNIQUE`](./miscellaneous.md#enforce_global_unique)
* [`GRAPHQL_ENABLED`](./graphql-api.md#graphql_enabled)
* [`JOB_RETENTION`](./miscellaneous.md#job_retention)
* [`MAINTENANCE_MODE`](./miscellaneous.md#maintenance_mode)
* [`MAPS_URL`](./miscellaneous.md#maps_url)
* [`MAX_PAGE_SIZE`](./miscellaneous.md#max_page_size)
* [`PAGINATE_COUNT`](./default-values.md#paginate_count)
* [`POWERFEED_DEFAULT_AMPERAGE`](./default-values.md#powerfeed_default_amperage)
* [`POWERFEED_DEFAULT_MAX_UTILIZATION`](./default-values.md#powerfeed_default_max_utilization)
* [`POWERFEED_DEFAULT_VOLTAGE`](./default-values.md#powerfeed_default_voltage)
* [`PREFER_IPV4`](./miscellaneous.md#prefer_ipv4)
* [`RACK_ELEVATION_DEFAULT_UNIT_HEIGHT`](./default-values.md#rack_elevation_default_unit_height)
* [`RACK_ELEVATION_DEFAULT_UNIT_WIDTH`](./default-values.md#rack_elevation_default_unit_width)

## Modifying the Configuration

The configuration file may be modified at any time. However, the WSGI service (e.g. Gunicorn) must be restarted before these changes will take effect:

```no-highlight
$ sudo systemctl restart netbox
```

Dynamic configuration parameters (those which can be modified via the UI) take effect immediately.
