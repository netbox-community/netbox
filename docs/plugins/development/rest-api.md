# REST API

Plugins can declare custom endpoints on NetBox's REST API to retrieve or manipulate models or other data. These behave very similarly to views, except that instead of rendering arbitrary content using a template, data is returned in JSON format using a serializer.

Generally speaking, there aren't many NetBox-specific components to implementing REST API functionality in a plugin. NetBox employs the [Django REST Framework](https://www.django-rest-framework.org/) (DRF) for its REST API, and plugin authors will find that they can largely replicate the same patterns found in NetBox's implementation. Some brief examples are included here for reference.

## Serializers

First, create a serializer for the plugin model, in `api/serializers.py`. Specify its model class and the fields to include within the serializer's `Meta` class.

```python
from rest_framework.serializers import ModelSerializer
from my_plugin.models import MyModel

class MyModelSerializer(ModelSerializer):

    class Meta:
        model = MyModel
        fields = ('id', 'foo', 'bar')
```

## Views

Next, create a generic API view set that allows basic CRUD (create, read, update, and delete) operations for objects. This is defined in `api/views.py`. Specify the `queryset` and `serializer_class` attributes under the view set.

```python
from rest_framework.viewsets import ModelViewSet
from my_plugin.models import MyModel
from .serializers import MyModelSerializer

class MyModelViewSet(ModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MyModelSerializer
```

## URLs

Finally, we'll register a URL for our endpoint in `api/urls.py`. This file **must** define a variable named `urlpatterns`.

```python
from rest_framework import routers
from .views import MyModelViewSet

router = routers.DefaultRouter()
router.register('my-model', MyModelViewSet)
urlpatterns = router.urls
```

With these three components in place, we can request `/api/plugins/my-plugin/my-model/` to retrieve a list of all MyModel instances.

!!! warning
    This example is provided as a minimal reference implementation only. It does not address authentication, performance, or myriad other concerns that plugin authors may need to address.
