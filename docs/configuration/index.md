# NetBox Configuration

NetBox's local configuration is stored in `$INSTALL_ROOT/netbox/netbox/configuration.py`. An example configuration is provided as `configuration.example.py`. You may copy or rename the example configuration and make changes as appropriate. NetBox will not run without a configuration file.

While NetBox has many configuration settings, only a few of them must be defined at the time of installation.

## Configuration Parameters

* [Required settings](required-settings.md)
* [Optional settings](optional-settings.md)

## Changing the Configuration

Configuration settings may be changed at any time. However, the WSGI service (e.g. Gunicorn) must be restarted before the changes will take effect:

```no-highlight
$ sudo systemctl restart netbox
```
