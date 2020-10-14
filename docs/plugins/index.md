# Plugins

Plugins are packaged [Django](https://docs.djangoproject.com/) apps that can be installed alongside NetBox to provide custom functionality not present in the core application. Plugins can introduce their own models and views, but cannot interfere with existing components. A NetBox user may opt to install plugins provided by the community or build his or her own.

Plugins are supported on NetBox v2.8 and later.

## Capabilities

The NetBox plugin architecture allows for the following:

* **Add new data models.** A plugin can introduce one or more models to hold data. (A model is essentially a table in the SQL database.)
* **Add new URLs and views.** Plugins can register URLs under the `/plugins` root path to provide browsable views for users.
* **Add content to existing model templates.** A template content class can be used to inject custom HTML content within the view of a core NetBox model. This content can appear in the left side, right side, or bottom of the page.
* **Add navigation menu items.** Each plugin can register new links in the navigation menu. Each link may have a set of buttons for specific actions, similar to the built-in navigation items.
* **Add custom middleware.** Custom Django middleware can be registered by each plugin.
* **Declare configuration parameters.** Each plugin can define required, optional, and default configuration parameters within its unique namespace. Plug configuration parameter are defined by the user under `PLUGINS_CONFIG` in `configuration.py`.
* **Limit installation by NetBox version.** A plugin can specify a minimum and/or maximum NetBox version with which it is compatible.

## Limitations

Either by policy or by technical limitation, the interaction of plugins with NetBox core is restricted in certain ways. A plugin may not:

* **Modify core models.** Plugins may not alter, remove, or override core NetBox models in any way. This rule is in place to ensure the integrity of the core data model.
* **Register URLs outside the `/plugins` root.** All plugin URLs are restricted to this path to prevent path collisions with core or other plugins.
* **Override core templates.** Plugins can inject additional content where supported, but may not manipulate or remove core content.
* **Modify core settings.** A configuration registry is provided for plugins, however they cannot alter or delete the core configuration.
* **Disable core components.** Plugins are not permitted to disable or hide core NetBox components.

## Installing Plugins

The instructions below detail the process for installing and enabling a NetBox plugin.

### Install Package

Download and install the plugin package per its installation instructions. Plugins published via PyPI are typically installed using pip. Be sure to install the plugin within NetBox's virtual environment.

```no-highlight
$ source /opt/netbox/venv/bin/activate
(venv) $ pip install <package>
```

Alternatively, you may wish to install the plugin manually by running `python setup.py install`. If you are developing a plugin and want to install it only temporarily, run `python setup.py develop` instead.

### Enable the Plugin

In `configuration.py`, add the plugin's name to the `PLUGINS` list:

```python
PLUGINS = [
    'plugin_name',
]
```

### Configure Plugin

If the plugin requires any configuration, define it in `configuration.py` under the `PLUGINS_CONFIG` parameter. The available configuration parameters should be detailed in the plugin's README file.

```no-highlight
PLUGINS_CONFIG = {
    'plugin_name': {
        'foo': 'bar',
        'buzz': 'bazz'
    }
}
```

### Run Database Migrations

If the plugin introduces new database models, run the provided schema migrations:

```no-highlight
(venv) $ cd /opt/netbox/netbox/
(venv) $ python3 manage.py migrate
```

### Collect Static Files

Plugins may package static files to be served directly by the HTTP front end. Ensure that these are copied to the static root directory with the `collectstatic` management command:

```no-highlight
(venv) $ cd /opt/netbox/netbox/
(venv) $ python3 manage.py collectstatic
```

### Restart WSGI Service

Restart the WSGI service to load the new plugin:

```no-highlight
# sudo systemctl restart netbox
```
