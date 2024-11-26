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

| View Class           | Description                                            |
|----------------------|--------------------------------------------------------|
| `ObjectView`         | View a single object                                   |
| `ObjectEditView`     | Create or edit a single object                         |
| `ObjectDeleteView`   | Delete a single object                                 |
| `ObjectChildrenView` | A list of child objects within the context of a parent |
| `ObjectListView`     | View a list of objects                                 |
| `BulkImportView`     | Import a set of new objects                            |
| `BulkEditView`       | Edit multiple objects                                  |
| `BulkDeleteView`     | Delete multiple objects                                |

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
    options:
      members:
        - get_queryset
        - get_object
        - get_extra_context

::: netbox.views.generic.ObjectView
    options:
      members:
        - get_template_name

::: netbox.views.generic.ObjectEditView
    options:
      members:
        - alter_object

::: netbox.views.generic.ObjectDeleteView
    options:
      members: false

::: netbox.views.generic.ObjectChildrenView
    options:
      members:
        - get_children
        - prep_table_data

## Multi-Object Views

Below are the class definitions for NetBox's multi-object views. These views handle simultaneous actions for sets objects. The list, import, edit, and delete views each inherit from `BaseMultiObjectView`, which is not intended to be used directly.

::: netbox.views.generic.base.BaseMultiObjectView
    options:
      members:
        - get_queryset
        - get_extra_context

::: netbox.views.generic.ObjectListView
    options:
      members:
        - get_table
        - export_table
        - export_template

::: netbox.views.generic.BulkImportView
    options:
      members:
        - save_object

::: netbox.views.generic.BulkEditView
    options:
      members: false

::: netbox.views.generic.BulkDeleteView
    options:
      members:
        - get_form

## Feature Views

These views are provided to enable or enhance certain NetBox model features, such as change logging or journaling. These typically do not need to be subclassed: They can be used directly e.g. in a URL path.

::: netbox.views.generic.ObjectChangeLogView
    options:
      members:
        - get_form

::: netbox.views.generic.ObjectJournalView
    options:
      members:
        - get_form

## Extending Core Views

### Additional Tabs

Plugins can "attach" a custom view to a core NetBox model by registering it with `register_model_view()`. To include a tab for this view within the NetBox UI, declare a TabView instance named `tab`, and add it to the template context dict:

```python
from dcim.models import Site
from myplugin.models import Stuff
from netbox.views import generic
from utilities.views import ViewTab, register_model_view

@register_model_view(Site, name='myview', path='some-other-stuff')
class MyView(generic.ObjectView):
    ...
    tab = ViewTab(
        label='Other Stuff',
        badge=lambda obj: Stuff.objects.filter(site=obj).count(),
        permission='myplugin.view_stuff'
    )

    def get(self, request, pk):
        ...
        return render(
            request,
            "myplugin/mytabview.html",
            context={
                "tab": self.tab,
            },
        )
```

!!! note "Changed in NetBox v4.2"
    The `register_model_view()` function was extended in NetBox v4.2 to support registration of list views by passing `detail=False`.

::: utilities.views.register_model_view

::: utilities.views.ViewTab

### Extra Template Content

Plugins can inject custom content into certain areas of core NetBox views. This is accomplished by subclassing `PluginTemplateExtension`, optionally designating one or more particular NetBox models, and defining the desired method(s) to render custom content. Five methods are available:

| Method              | View        | Description                                         |
|---------------------|-------------|-----------------------------------------------------|
| `navbar()`          | All         | Inject content inside the top navigation bar        |
| `list_buttons()`    | List view   | Add buttons to the top of the page                  |
| `buttons()`         | Object view | Add buttons to the top of the page                  |
| `alerts()`          | Object view | Inject content at the top of the page               |
| `left_page()`       | Object view | Inject content on the left side of the page         |
| `right_page()`      | Object view | Inject content on the right side of the page        |
| `full_width_page()` | Object view | Inject content across the entire bottom of the page |

Additionally, a `render()` method is available for convenience. This method accepts the name of a template to render, and any additional context data you want to pass. Its use is optional, however.

To control where the custom content is injected, plugin authors can specify an iterable of models by overriding the `models` attribute on the subclass. Extensions which do not specify a set of models will be invoked on every view, where supported.

When a PluginTemplateExtension is instantiated, context data is assigned to `self.context`. Available data includes:

* `object` - The object being viewed (object views only)
* `model` - The model of the list view (list views only)
* `request` - The current request
* `settings` - Global NetBox settings
* `config` - Plugin-specific configuration parameters

For example, accessing `{{ request.user }}` within a template will return the current user.

Declared subclasses should be gathered into a list or tuple for integration with NetBox. By default, NetBox looks for an iterable named `template_extensions` within a `template_content.py` file. (This can be overridden by setting `template_extensions` to a custom value on the plugin's PluginConfig.) An example is below.

```python
from netbox.plugins import PluginTemplateExtension
from .models import Animal

class SiteAnimalCount(PluginTemplateExtension):
    models = ['dcim.site']

    def right_page(self):
        return self.render('netbox_animal_sounds/inc/animal_count.html', extra_context={
            'animal_count': Animal.objects.count(),
        })

template_extensions = [SiteAnimalCount]
```
