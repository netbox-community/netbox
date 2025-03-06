# REST API

Plugins can declare custom endpoints on NetBox's REST API to retrieve or manipulate models or other data. These behave very similarly to views, except that instead of rendering arbitrary content using a template, data is returned in JSON format using a serializer.

Generally speaking, there aren't many NetBox-specific components to implementing REST API functionality in a plugin. NetBox employs the [Django REST Framework](https://www.django-rest-framework.org/) (DRF) for its REST API, and plugin authors will find that they can largely replicate the same patterns found in NetBox's implementation. Some brief examples are included here for reference.

## Code Layout

The recommended approach is to separate API serializers, views, and URLs into separate modules under the `api/` directory to keep things tidy, particularly for larger projects. The file at `api/__init__.py` can import the relevant components from each submodule to allow import all API components directly from elsewhere. However, this is merely a convention and not strictly required.

```no-highlight
project-name/
  - plugin_name/
    - api/
      - __init__.py
      - serializers.py
      - urls.py
      - views.py
    ...
```

## Serializers

### Model Serializers

Serializers are responsible for converting Python objects to JSON data suitable for conveying to consumers, and vice versa. NetBox provides the `NetBoxModelSerializer` class for use by plugins to handle the assignment of tags and custom field data. (These features can also be included ad hoc via the `CustomFieldModelSerializer` and `TaggableModelSerializer` classes.)

The default nested representation of an object is defined by the `brief_fields` attributes under the serializer's `Meta` class. (Older versions of NetBox required the definition of a separate nested serializer.)

#### Example

To create a serializer for a plugin model, subclass `NetBoxModelSerializer` in `api/serializers.py`. Specify the model class and the fields to include within the serializer's `Meta` class.

```python
# api/serializers.py
from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer
from my_plugin.models import MyModel

class MyModelSerializer(NetBoxModelSerializer):
    foo = SiteSerializer(nested=True, allow_null=True)

    class Meta:
        model = MyModel
        fields = ('id', 'foo', 'bar', 'baz')
        brief_fields = ('id', 'url', 'display', 'bar')
```

## Viewsets

Just as in the user interface, a REST API view handles the business logic of displaying and interacting with NetBox objects. NetBox provides the `NetBoxModelViewSet` class, which extends DRF's built-in `ModelViewSet` to handle bulk operations and object validation.

Unlike the user interface, typically only a single view set is required per model: This view set handles all request types (`GET`, `POST`, `DELETE`, etc.).

### Example

To create a viewset for a plugin model, subclass `NetBoxModelViewSet` in `api/views.py`, and define the `queryset` and `serializer_class` attributes.

```python
# api/views.py
from netbox.api.viewsets import NetBoxModelViewSet
from my_plugin.models import MyModel
from .serializers import MyModelSerializer

class MyModelViewSet(NetBoxModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MyModelSerializer
```

## Routers

Routers map URLs to REST API views (endpoints). NetBox does not provide any custom components for this; the [`DefaultRouter`](https://www.django-rest-framework.org/api-guide/routers/#defaultrouter) class provided by DRF should suffice for most use cases.

Routers should be exposed in `api/urls.py`. This file **must** define a variable named `urlpatterns`.

### Example

```python
# api/urls.py
from netbox.api.routers import NetBoxRouter
from .views import MyModelViewSet

router = NetBoxRouter()
router.register('my-model', MyModelViewSet)
urlpatterns = router.urls
```

This will make the plugin's view accessible at `/api/plugins/my-plugin/my-model/`.

!!! warning
    The examples provided here are intended to serve as a minimal reference implementation only. This documentation does not address authentication, performance, or myriad other concerns that plugin authors may need to address.
