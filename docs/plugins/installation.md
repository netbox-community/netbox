# Installing a Plugin

!!! warning
    The instructions below detail the general process for installing and configuring a NetBox plugin. However, each plugin is different and may require additional tasks or modifications to the steps below. Always consult the documentation for a specific plugin **before** attempting to install it.

## Install the Python Package

Download and install the plugin's Python package per its installation instructions. Plugins published via PyPI are typically installed using the [`pip`](https://packaging.python.org/en/latest/tutorials/installing-packages/) command line utility. Be sure to install the plugin within NetBox's virtual environment.

```no-highlight
$ source /opt/netbox/venv/bin/activate
(venv) $ pip install <package>
```

Alternatively, you may wish to install the plugin manually by running `python setup.py install`. If you are developing a plugin and want to install it only temporarily, run `python setup.py develop` instead.

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
(venv) $ cd /opt/netbox/netbox/
(venv) $ python3 manage.py migrate
```

!!! tip
    It's okay to run the `migrate` management command even if the plugin does not include any migration files.

## Collect Static Files

Plugins may package static resources like images or scripts to be served directly by the HTTP front end. Ensure that these are copied to the static root directory with the `collectstatic` management command:

```no-highlight
(venv) $ cd /opt/netbox/netbox/
(venv) $ python3 manage.py collectstatic
```

### Restart WSGI Service

Finally, restart the WSGI service and RQ workers to load the new plugin:

```no-highlight
# sudo systemctl restart netbox netbox-rq
```
