# Filters & Filter Sets

Filter sets define the mechanisms available for filtering or searching through a set of objects in NetBox. For instance, sites can be filtered by their parent region or group, status, facility ID, and so on. The same filter set is used consistently for a model whether the request is made via the UI, REST API, or GraphQL API. NetBox employs the [django-filters2](https://django-tables2.readthedocs.io/en/latest/) library to define filter sets.

## FilterSet Classes

To support additional functionality standard to NetBox models, such as tag assignment and custom field support, the `NetBoxModelFilterSet` class is available for use by plugins. This should be used as the base filter set class for plugin models which inherit from `NetBoxModel`. Within this class, individual filters can be declared as directed by the `django-filters` documentation. An example is provided below.

```python
# filtersets.py
import django_filters
from netbox.filtersets import NetBoxModelFilterSet
from .models import MyModel

class MyFilterSet(NetBoxModelFilterSet):
    status = django_filters.MultipleChoiceFilter(
        choices=(
            ('foo', 'Foo'),
            ('bar', 'Bar'),
            ('baz', 'Baz'),
        ),
        null_value=None
    )

    class Meta:
        model = MyModel
        fields = ('some', 'other', 'fields')
```

### Declaring Filter Sets

To utilize a filter set in a subclass of one of NetBox's generic views (such as `ObjectListView` or `BulkEditView`), define the `filterset` attribute on the view class:

```python
# views.py
from netbox.views.generic import ObjectListView
from .filtersets import MyModelFilterSet
from .models import MyModel

class MyModelListView(ObjectListView):
    queryset = MyModel.objects.all()
    filterset = MyModelFilterSet
```

To enable a filter set on a  REST API endpoint, set the `filterset_class` attribute on the API view:

```python
# api/views.py
from myplugin import models, filtersets
from . import serializers

class MyModelViewSet(...):
    queryset = models.MyModel.objects.all()
    serializer_class = serializers.MyModelSerializer
    filterset_class = filtersets.MyModelFilterSet
```

## Filter Classes

### TagFilter

The `TagFilter` class is available for all models which support tag assignment (those which inherit from `NetBoxModel` or `TagsMixin`). This filter subclasses django-filter's `ModelMultipleChoiceFilter` to work with NetBox's `TaggedItem` class.

```python
from django_filters import FilterSet
from extras.filters import TagFilter

class MyModelFilterSet(FilterSet):
    tag = TagFilter()
```
