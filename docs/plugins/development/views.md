# Views

If your plugin needs its own page or pages in the NetBox web UI, you'll need to define views. A view is a particular page tied to a URL within NetBox, which renders content using a template. Views are typically defined in `views.py`, and URL patterns in `urls.py`. As an example, let's write a view which displays a random animal and the sound it makes. First, we'll create the view in `views.py`:

```python
from django.shortcuts import render
from django.views.generic import View
from .models import Animal

class RandomAnimalView(View):
    """
    Display a randomly-selected animal.
    """
    def get(self, request):
        animal = Animal.objects.order_by('?').first()
        return render(request, 'netbox_animal_sounds/animal.html', {
            'animal': animal,
        })
```

This view retrieves a random animal from the database and and passes it as a context variable when rendering a template named `animal.html`, which doesn't exist yet. To create this template, first create a directory named `templates/netbox_animal_sounds/` within the plugin source directory. (We use the plugin's name as a subdirectory to guard against naming collisions with other plugins.) Then, create a template named `animal.html` as described below.

## View Classes

NetBox provides several generic view classes (documented below) to facilitate common operations, such as creating, viewing, modifying, and deleting objects. Plugins can subclass these views for their own use.

| View Class | Description |
|------------|-------------|
| `ObjectView` | View a single object |
| `ObjectEditView` | Create or edit a single object |
| `ObjectDeleteView` | Delete a single object |
| `ObjectListView` | View a list of objects |
| `BulkImportView` | Import a set of new objects |
| `BulkEditView` | Edit multiple objects |
| `BulkDeleteView` | Delete multiple objects |

!!! warning
    Please note that only the classes which appear in this documentation are currently supported. Although other classes may be present within the `views.generic` module, they are not yet supported for use by plugins.

### Example Usage

```python
# views.py
from netbox.views.generic import ObjectEditView
from .models import Thing

class ThingEditView(ObjectEditView):
    queryset = Thing.objects.all()
    template_name = 'myplugin/thing.html'
    ...
```

## URL Registration

To make the view accessible to users, we need to register a URL for it. We do this in `urls.py` by defining a `urlpatterns` variable containing a list of paths.

```python
from django.urls import path
from . import views

urlpatterns = [
    path('random/', views.RandomAnimalView.as_view(), name='random_animal'),
]
```

A URL pattern has three components:

* `route` - The unique portion of the URL dedicated to this view
* `view` - The view itself
* `name` - A short name used to identify the URL path internally

This makes our view accessible at the URL `/plugins/animal-sounds/random/`. (Remember, our `AnimalSoundsConfig` class sets our plugin's base URL to `animal-sounds`.) Viewing this URL should show the base NetBox template with our custom content inside it.

## Extending Core Views

Plugins can inject custom content into certain areas of the detail views of applicable models. This is accomplished by subclassing `PluginTemplateExtension`, designating a particular NetBox model, and defining the desired methods to render custom content. Four methods are available:

* `left_page()` - Inject content on the left side of the page
* `right_page()` - Inject content on the right side of the page
* `full_width_page()` - Inject content across the entire bottom of the page
* `buttons()` - Add buttons to the top of the page

Additionally, a `render()` method is available for convenience. This method accepts the name of a template to render, and any additional context data you want to pass. Its use is optional, however.

When a PluginTemplateExtension is instantiated, context data is assigned to `self.context`. Available data include:

* `object` - The object being viewed
* `request` - The current request
* `settings` - Global NetBox settings
* `config` - Plugin-specific configuration parameters

For example, accessing `{{ request.user }}` within a template will return the current user.

Declared subclasses should be gathered into a list or tuple for integration with NetBox. By default, NetBox looks for an iterable named `template_extensions` within a `template_content.py` file. (This can be overridden by setting `template_extensions` to a custom value on the plugin's PluginConfig.) An example is below.

```python
from extras.plugins import PluginTemplateExtension
from .models import Animal

class SiteAnimalCount(PluginTemplateExtension):
    model = 'dcim.site'

    def right_page(self):
        return self.render('netbox_animal_sounds/inc/animal_count.html', extra_context={
            'animal_count': Animal.objects.count(),
        })

template_extensions = [SiteAnimalCount]
```

## Navigation Menu Items

To make its views easily accessible to users, a plugin can inject items in NetBox's navigation menu under the "Plugins" header. Menu items are added by defining a list of PluginMenuItem instances. By default, this should be a variable named `menu_items` in the file `navigation.py`. An example is shown below.

```python
from extras.plugins import PluginMenuButton, PluginMenuItem
from utilities.choices import ButtonColorChoices

menu_items = (
    PluginMenuItem(
        link='plugins:netbox_animal_sounds:random_animal',
        link_text='Random sound',
        buttons=(
            PluginMenuButton('home', 'Button A', 'fa fa-info', ButtonColorChoices.BLUE),
            PluginMenuButton('home', 'Button B', 'fa fa-warning', ButtonColorChoices.GREEN),
        )
    ),
)
```

A `PluginMenuItem` has the following attributes:

* `link` - The name of the URL path to which this menu item links
* `link_text` - The text presented to the user
* `permissions` - A list of permissions required to display this link (optional)
* `buttons` - An iterable of PluginMenuButton instances to display (optional)

A `PluginMenuButton` has the following attributes:

* `link` - The name of the URL path to which this button links
* `title` - The tooltip text (displayed when the mouse hovers over the button)
* `icon_class` - Button icon CSS class (NetBox currently supports [Font Awesome 4.7](https://fontawesome.com/v4.7.0/icons/))
* `color` - One of the choices provided by `ButtonColorChoices` (optional)
* `permissions` - A list of permissions required to display this button (optional)

!!! note
    Any buttons associated within a menu item will be shown only if the user has permission to view the link, regardless of what permissions are set on the buttons.

## Object Views Reference

Below is the class definition for NetBox's BaseObjectView. The attributes and methods defined here are available on all generic views which handle a single object.

::: netbox.views.generic.base.BaseObjectView
    rendering:
      show_source: false

::: netbox.views.generic.ObjectView
    selection:
      members:
        - get_object
        - get_template_name
    rendering:
      show_source: false

::: netbox.views.generic.ObjectEditView
    selection:
      members:
        - get_object
        - alter_object
    rendering:
      show_source: false

::: netbox.views.generic.ObjectDeleteView
    selection:
      members:
        - get_object
    rendering:
      show_source: false

## Multi-Object Views Reference

Below is the class definition for NetBox's BaseMultiObjectView. The attributes and methods defined here are available on all generic views which deal with multiple objects.

::: netbox.views.generic.base.BaseMultiObjectView
    rendering:
      show_source: false

::: netbox.views.generic.ObjectListView
    selection:
      members:
        - get_table
        - export_table
        - export_template
    rendering:
      show_source: false

::: netbox.views.generic.BulkImportView
    selection:
      members: false
    rendering:
      show_source: false

::: netbox.views.generic.BulkEditView
    selection:
      members: false
    rendering:
      show_source: false

::: netbox.views.generic.BulkDeleteView
    selection:
      members:
        - get_form
    rendering:
      show_source: false
