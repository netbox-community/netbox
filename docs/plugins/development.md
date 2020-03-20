# Plugin Development

This documentation covers the development of custom plugins for NetBox. Plugins are essentially self-contained [Django apps](https://docs.djangoproject.com/en/stable/) which integrate with NetBox to provide custom functionality. Since the development of Django apps is already very well-documented, we'll only be covering the aspects that are specific to NetBox.

## Initial Setup

### Plugin Structure

Although the specific structure of a plugin is largely left to the discretion of its authors, a typical NetBox plugin might look like this:

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
  - setup.py
```

The top level is the project root, which is typically synonymous with the git repository. A file named `setup.py` must exist at the top level to register the plugin within NetBox and to define meta data. You might also find miscellaneous other files within the project root, such as `.gitignore`.

The second level directory houses the actual plugin code, arranged in a set of Python files. These are arbitrary, however the plugin _must_ include a `__init__.py` file which provides an AppConfig subclass.

### Create setup.py

The first step is to write our Python [setup script](https://docs.python.org/3.6/distutils/setupscript.html), which facilitates the installation of the plugin. This is standard practice for Python applications, with the only really noteworthy bit being the declared `entry_points`: The plugin must define an entry point for `netbox.plugin` pointing to the NetBoxPluginMeta class.

```python
from setuptools import setup, find_packages

setup(
    name='netbox-animal-sounds',
    version='0.1',
    description='Show animals and the sounds they make',
    url='https://github.com/organization/animal-sounds',
    author='Author Name',
    author_email='author@example.com',
    license='Apache 2.0',

    install_requires=[],
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    entry_points={
        'netbox.plugin': 'netbox_animal_sounds=netbox_animal_sounds:NetBoxPluginMeta'
    }
)

```

### Define an AppConfig


