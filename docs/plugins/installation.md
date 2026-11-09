# Installing a Plugin

!!! warning
    The instructions below detail the general process for installing and configuring a NetBox plugin. However, each plugin is different and may require additional tasks or modifications to the steps below. Always consult the documentation for a specific plugin **before** attempting to install it.

## Install the Python Package

Download and install the plugin's Python package per its installation instructions. Plugins published via PyPI are typically installed using the [`pip`](https://packaging.python.org/en/latest/tutorials/installing-packages/) command line utility. Be sure to install the plugin within NetBox's virtual environment.

The recommended method is to add the package to `/opt/netbox/local_requirements.txt` and then install that file into NetBox's virtual environment. This records the plugin alongside NetBox's other local requirements, so that it can be reinstalled when NetBox is upgraded or the virtual environment is rebuilt.

```no-highlight
$ sudo sh -c "echo '<package>' >> /opt/netbox/local_requirements.txt"
$ sudo /opt/netbox/venv/bin/python -m pip install -r /opt/netbox/local_requirements.txt
```

!!! note "Release archive and Git installations"
    For a NetBox installation created from a release archive or Git checkout, add the package to `/opt/netbox/local_requirements.txt`, enable and configure the plugin as described below, then run `sudo /opt/netbox/upgrade.sh` and [restart the services](#restart-wsgi-service). The upgrade script installs the package, applies database migrations, and collects static files.

Installing packages into NetBox's virtual environment requires write permissions to that directory. For installations under `/opt/netbox`, a regular user typically does not have write permissions. Activating the virtual environment does not change file permissions, so a direct `pip install` command may result in a `Permission denied` error.

If you must install a package manually, use one of the following methods. You can switch to a root shell before activating the virtual environment:

```no-highlight
$ sudo -i
# source /opt/netbox/venv/bin/activate
(venv) # pip install <package>
```

Or, run `pip` by invoking the Python executable within NetBox's virtual environment:

```no-highlight
$ sudo /opt/netbox/venv/bin/python3 -m pip install <package>
```

In the examples above, `$` indicates a regular user shell and `#` indicates a root shell.

Packages that are not published to PyPI may need to be installed from a local source tree. From the package directory, use one of the methods above to run `pip install .`; for editable development installs, run `pip install --editable .` instead.

## Enable the Plugin

In `configuration.py`, add the plugin's name to the `PLUGINS` list:

```python
PLUGINS = [
    # ...
    'plugin_name',
]
```

## Configure the Plugin

If the plugin requires any configuration, define it in `configuration.py` under the `PLUGINS_CONFIG` parameter. The available configuration parameters should be detailed in the plugin's `README` file or other documentation.

```no-highlight
PLUGINS_CONFIG = {
    'plugin_name': {
        'foo': 'bar',
        'buzz': 'bazz'
    }
}
```

## Run Database Migrations

If the plugin introduces new database models, run the provided schema migrations:

```no-highlight
$ sudo -u netbox /opt/netbox/venv/bin/netbox migrate
```

!!! tip
    It's okay to run the `migrate` management command even if the plugin does not include any migration files.

## Collect Static Files

Plugins may package static resources like images or scripts to be served directly by the HTTP front end. Ensure that these are copied to the static root directory with the `collectstatic` management command:

```no-highlight
$ sudo -u netbox /opt/netbox/venv/bin/netbox collectstatic --no-input
```

!!! tip
    The `netbox upgrade` command performs both of the steps above, along with NetBox's other routine maintenance tasks, and may be run instead.

## Restart WSGI Service

Finally, restart the WSGI service and RQ workers to load the new plugin:

```no-highlight
$ sudo systemctl restart netbox netbox-rq
```
