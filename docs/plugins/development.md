# Plugin Development

This documentation covers the development of custom plugins for NetBox. Plugins are essentially self-contained [Django apps](https://docs.djangoproject.com/en/stable/) which integrate with NetBox to provide custom functionality. Since the development of Django apps is already very well-documented, we'll only be covering the aspects that are specific to NetBox.

## Initial Setup

## Plugin Structure

Although the specific structure of a plugin is largely left to the discretion of its authors, a typical NetBox plugin looks something like this:

```no-highlight
plugin_name/
  - plugin_name/
    - templates/
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

The top level is the project root, which is typically synonymous with the git repository. Within the root should exist several files:

* `setup.py` - This is a standard Python installation script used to install the plugin package within the Python environment.
* `README` - A brief introduction to your plugin, how to install and configure it, where to find help, and any other pertinent information. It is recommended to write README files using a markup language such as Markdown.
* The plugin source directory, with the same name as your plugin.

The plugin source directory contains all of the actual Python code and other resources used by your plugin. Its structure is left to the author's discretion, however it is recommended to follow best practices as outlined in the [Django documentation](https://docs.djangoproject.com/en/stable/intro/reusable-apps/). At a minimum, this directory **must** contain an `__init__.py` file containing an instance of NetBox's `PluginConfig` class.

### Create setup.py

`setup.py` is the [setup script](https://docs.python.org/3.6/distutils/setupscript.html) we'll use to install our plugin once it's finished. This script essentially just calls the setuptools library's `setup()` function to create a Python distribution package. We can pass a number of keyword arguments to information the package creation as well as to provide metadata about the plugin. An example `setup.py` is below:

```python
from setuptools import find_packages, setup

setup(
    name='netbox-animal-sounds',
    version='0.1',
    description='Show animals and the sounds they make',
    url='https://github.com/example-org/animal-sounds',
    author='Author Name',
    author_email='author@example.com',
    license='Apache 2.0',
    install_requires=[],
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'netbox_plugins': 'netbox_animal_sounds=netbox_animal_sounds:AnimalSoundsConfig'
    }
)
```

Many of these are self-explanatory, but for more information, see the [setuptools documentation](https://setuptools.readthedocs.io/en/latest/setuptools.html).

The key requirement for a NetBox plugin is the presence of an entry point for `netbox_plugins` pointing to the `PluginConfig` subclass, which we'll define next.

### Define a PluginConfig

The `PluginConfig` class is a NetBox-specific wrapper around Django's built-in [`AppConfig`](https://docs.djangoproject.com/en/stable/ref/applications/). It is used to declare NetBox plugin functionality within a Python package. Each plugin should provide its own subclass, defining its name, metadata, and default and required configuration parameters. An example is below:

```python
from extras.plugins import PluginConfig

class AnimalSoundsConfig(PluginConfig):
    name = 'netbox_animal_sounds'
    verbose_name = 'Animal Sounds Plugin'
    version = '0.1'
    author = 'Author Name'
    description = 'Show animals and the sounds they make'
    url_slug = 'animal-sounds'
    required_settings = []
    default_settings = {
        'loud': False
    }
```

#### PluginConfig Attributes

* `name` - Raw plugin name; same as the plugin's source directory
* `author_name` - Name of plugin's author
* `verbose_name` - Human-friendly name
* `version` - Plugin version
* `description` - Brief description of the plugin's purpose
* `url_slug` - Base path to use for plugin URLs (optional). If not specified, the project's `name` will be used.
* `required_settings`: A list of configuration parameters that **must** be defined by the user
* `default_settings`: A dictionary of configuration parameter names and their default values
* `middleware`: A list of middleware classes to append after NetBox's build-in middleware.
* `caching_config`: Plugin-specific cache configuration
