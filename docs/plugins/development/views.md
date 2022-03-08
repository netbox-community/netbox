# Views

## Writing Views

If your plugin will provide its own page or pages within the NetBox web UI, you'll need to define views. A view is a piece of business logic which performs an action and/or renders a page when a request is made to a particular URL. HTML content is rendered using a [template](./templates.md). Views are typically defined in `views.py`, and URL patterns in `urls.py`.

As an example, let's write a view which displays a random animal and the sound it makes. We'll use Django's generic `View` class to minimize the amount of boilerplate code needed.

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

This view retrieves a random Animal instance from the database and passes it as a context variable when rendering a template named `animal.html`. HTTP `GET` requests are handled by the view's `get()` method, and `POST` requests are handled by its `post()` method.

Our example above is extremely simple, but views can do just about anything. They are generally where the core of your plugin's functionality will reside. Views also are not limited to returning HTML content: A view could return a CSV file or image, for instance. For more information on views, see the [Django documentation](https://docs.djangoproject.com/en/stable/topics/class-based-views/).

### URL Registration

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

### View Classes

NetBox provides several generic view classes (documented below) to facilitate common operations, such as creating, viewing, modifying, and deleting objects. Plugins can subclass these views for their own use.

| View Class         | Description                    |
|--------------------|--------------------------------|
| `ObjectView`       | View a single object           |
| `ObjectEditView`   | Create or edit a single object |
| `ObjectDeleteView` | Delete a single object         |
| `ObjectListView`   | View a list of objects         |
| `BulkImportView`   | Import a set of new objects    |
| `BulkEditView`     | Edit multiple objects          |
| `BulkDeleteView`   | Delete multiple objects        |

!!! warning
    Please note that only the classes which appear in this documentation are currently supported. Although other classes may be present within the `views.generic` module, they are not yet supported for use by plugins.

#### Example Usage

```python
# views.py
from netbox.views.generic import ObjectEditView
from .models import Thing

class ThingEditView(ObjectEditView):
    queryset = Thing.objects.all()
    template_name = 'myplugin/thing.html'
    ...
```
## Object Views

Below are the class definitions for NetBox's object views. These views handle CRUD actions for individual objects. The view, add/edit, and delete views each inherit from `BaseObjectView`, which is not intended to be used directly.

::: netbox.views.generic.base.BaseObjectView

::: netbox.views.generic.ObjectView
    selection:
      members:
        - get_object
        - get_template_name

::: netbox.views.generic.ObjectEditView
    selection:
      members:
        - get_object
        - alter_object

::: netbox.views.generic.ObjectDeleteView
    selection:
      members:
        - get_object

## Multi-Object Views

Below are the class definitions for NetBox's multi-object views. These views handle simultaneous actions for sets objects. The list, import, edit, and delete views each inherit from `BaseMultiObjectView`, which is not intended to be used directly.

::: netbox.views.generic.base.BaseMultiObjectView

::: netbox.views.generic.ObjectListView
    selection:
      members:
        - get_table
        - export_table
        - export_template

::: netbox.views.generic.BulkImportView
    selection:
      members: false

::: netbox.views.generic.BulkEditView
    selection:
      members: false

::: netbox.views.generic.BulkDeleteView
    selection:
      members:
        - get_form

## Feature Views

These views are provided to enable or enhance certain NetBox model features, such as change logging or journaling. These typically do not need to be subclassed: They can be used directly e.g. in a URL path.

::: netbox.views.generic.ObjectChangeLogView
    selection:
      members:
        - get_form

::: netbox.views.generic.ObjectJournalView
    selection:
      members:
        - get_form

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
