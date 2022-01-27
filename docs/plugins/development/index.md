# Plugins Development

!!! info "Help Improve the NetBox Plugins Framework!"
    We're looking for volunteers to help improve NetBox's plugins framework. If you have experience developing plugins, we'd love to hear from you! You can find more information about this initiative [here](https://github.com/netbox-community/netbox/discussions/8338).

This documentation covers the development of custom plugins for NetBox. Plugins are essentially self-contained [Django apps](https://docs.djangoproject.com/en/stable/) which integrate with NetBox to provide custom functionality. Since the development of Django apps is already very well-documented, we'll only be covering the aspects that are specific to NetBox.

Plugins can do a lot, including:

* Create Django models to store data in the database
* Provide their own "pages" (views) in the web user interface
* Inject template content and navigation links
* Establish their own REST API endpoints
* Add custom request/response middleware

However, keep in mind that each piece of functionality is entirely optional. For example, if your plugin merely adds a piece of middleware or an API endpoint for existing data, there's no need to define any new models.

!!! warning
    While very powerful, the NetBox plugins API is necessarily limited in its scope. The plugins API is discussed here in its entirety: Any part of the NetBox code base not documented here is _not_ part of the supported plugins API, and should not be employed by a plugin. Internal elements of NetBox are subject to change at any time and without warning. Plugin authors are **strongly** encouraged to develop plugins using only the officially supported components discussed here and those provided by the underlying Django framework so as to avoid breaking changes in future releases. 

## Initial Setup

### Plugin Structure

Although the specific structure of a plugin is largely left to the discretion of its authors, a typical NetBox plugin looks something like this:

```no-highlight
project-name/
  - plugin_name/
    - templates/
      - plugin_name/
        - *.html
    - __init__.py
    - middleware.py
    - navigation.py
    - signals.py
    - template_content.py
    - urls.py
    - views.py
  - README
  - setup.py
```

The top level is the project root, which can have any name that you like. Immediately within the root should exist several items:

* `setup.py` - This is a standard installation script used to install the plugin package within the Python environment.
* `README` - A brief introduction to your plugin, how to install and configure it, where to find help, and any other pertinent information. It is recommended to write README files using a markup language such as Markdown.
* The plugin source directory, with the same name as your plugin. This must be a valid Python package name (e.g. no spaces or hyphens).

The plugin source directory contains all the actual Python code and other resources used by your plugin. Its structure is left to the author's discretion, however it is recommended to follow best practices as outlined in the [Django documentation](https://docs.djangoproject.com/en/stable/intro/reusable-apps/). At a minimum, this directory **must** contain an `__init__.py` file containing an instance of NetBox's `PluginConfig` class.

### Create setup.py

`setup.py` is the [setup script](https://docs.python.org/3.8/distutils/setupscript.html) we'll use to install our plugin once it's finished. The primary function of this script is to call the setuptools library's `setup()` function to create a Python distribution package. We can pass a number of keyword arguments to inform the package creation as well as to provide metadata about the plugin. An example `setup.py` is below:

```python
from setuptools import find_packages, setup

setup(
    name='netbox-animal-sounds',
    version='0.1',
    description='An example NetBox plugin',
    url='https://github.com/netbox-community/netbox-animal-sounds',
    author='Jeremy Stretch',
    license='Apache 2.0',
    install_requires=[],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
```

Many of these are self-explanatory, but for more information, see the [setuptools documentation](https://setuptools.readthedocs.io/en/latest/setuptools.html).

!!! note
    `zip_safe=False` is **required** as the current plugin iteration is not zip safe due to upstream python issue [issue19699](https://bugs.python.org/issue19699)  

### Define a PluginConfig

The `PluginConfig` class is a NetBox-specific wrapper around Django's built-in [`AppConfig`](https://docs.djangoproject.com/en/stable/ref/applications/) class. It is used to declare NetBox plugin functionality within a Python package. Each plugin should provide its own subclass, defining its name, metadata, and default and required configuration parameters. An example is below:

```python
from extras.plugins import PluginConfig

class AnimalSoundsConfig(PluginConfig):
    name = 'netbox_animal_sounds'
    verbose_name = 'Animal Sounds'
    description = 'An example plugin for development purposes'
    version = '0.1'
    author = 'Jeremy Stretch'
    author_email = 'author@example.com'
    base_url = 'animal-sounds'
    required_settings = []
    default_settings = {
        'loud': False
    }

config = AnimalSoundsConfig
```

NetBox looks for the `config` variable within a plugin's `__init__.py` to load its configuration. Typically, this will be set to the PluginConfig subclass, but you may wish to dynamically generate a PluginConfig class based on environment variables or other factors.

#### PluginConfig Attributes

| Name | Description                                                                                                   |
| ---- |---------------------------------------------------------------------------------------------------------------|
| `name` | Raw plugin name; same as the plugin's source directory                                                        |
| `verbose_name` | Human-friendly name for the plugin                                                                            |
| `version` | Current release ([semantic versioning](https://semver.org/) is encouraged)                                    |
| `description` | Brief description of the plugin's purpose                                                                     |
| `author` | Name of plugin's author                                                                                       |
| `author_email` | Author's public email address                                                                                 |
| `base_url` | Base path to use for plugin URLs (optional). If not specified, the project's `name` will be used.             |
| `required_settings` | A list of any configuration parameters that **must** be defined by the user                                   |
| `default_settings` | A dictionary of configuration parameters and their default values                                             |
| `min_version` | Minimum version of NetBox with which the plugin is compatible                                                 |
| `max_version` | Maximum version of NetBox with which the plugin is compatible                                                 |
| `middleware` | A list of middleware classes to append after NetBox's build-in middleware                                     |
| `template_extensions` | The dotted path to the list of template extension classes (default: `template_content.template_extensions`)   |
| `menu_items` | The dotted path to the list of menu items provided by the plugin (default: `navigation.menu_items`)           |
| `user_preferences` | The dotted path to the dictionary mapping of user preferences defined by the plugin (default: `preferences.preferences`) |

All required settings must be configured by the user. If a configuration parameter is listed in both `required_settings` and `default_settings`, the default setting will be ignored.

### Create a Virtual Environment

It is strongly recommended to create a Python [virtual environment](https://docs.python.org/3/tutorial/venv.html) specific to your plugin. This will afford you complete control over the installed versions of all dependencies and avoid conflicting with any system packages. This environment can live wherever you'd like, however it should be excluded from revision control. (A popular convention is to keep all virtual environments in the user's home directory, e.g. `~/.virtualenvs/`.)

```shell
python3 -m venv /path/to/my/venv
```

You can make NetBox available within this environment by creating a path file pointing to its location. This will add NetBox to the Python path upon activation. (Be sure to adjust the command below to specify your actual virtual environment path, Python version, and NetBox installation.)

```shell
cd $VENV/lib/python3.8/site-packages/
echo /opt/netbox/netbox > netbox.pth
```

### Install the Plugin for Development

To ease development, it is recommended to go ahead and install the plugin at this point using setuptools' `develop` mode. This will create symbolic links within your Python environment to the plugin development directory. Call `setup.py` from the plugin's root directory with the `develop` argument (instead of `install`):

```no-highlight
$ python setup.py develop
```
