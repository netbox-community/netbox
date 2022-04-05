# NetBox Configuration

NetBox's local configuration is stored in `$INSTALL_ROOT/netbox/netbox/configuration.py` by default. An example configuration is provided as `configuration_example.py`. You may copy or rename the example configuration and make changes as appropriate. NetBox will not run without a configuration file.  While NetBox has many configuration settings, only a few of them must be defined at the time of installation: these are defined under "required settings" below.

!!! info "Customizing the Configuration Module"
    A custom configuration module may be specified by setting the `NETBOX_CONFIGURATION` environment variable. This must be a dotted path to the desired Python module. For example, a file named `my_config.py` in the same directory as `settings.py` would be referenced as `netbox.my_config`.

    For the sake of brevity, the NetBox documentation refers to the configuration file simply as `configuration.py`.

Some configuration parameters may alternatively be defined either in `configuration.py` or within the administrative section of the user interface. Settings which are "hard-coded" in the configuration file take precedence over those defined via the UI.

## Configuration Parameters

* [Required settings](required-settings.md)
* [Optional settings](optional-settings.md)
* [Dynamic settings](dynamic-settings.md)
* [Remote authentication settings](remote-authentication.md)

## Changing the Configuration

The configuration file may be modified at any time. However, the WSGI service (e.g. Gunicorn) must be restarted before the changes will take effect:

```no-highlight
$ sudo systemctl restart netbox
```

Configuration parameters which are set via the admin UI (those listed under "dynamic settings") take effect immediately.
