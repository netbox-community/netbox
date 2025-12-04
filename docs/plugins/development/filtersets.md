# Filters & Filter Sets

Filter sets define the mechanisms available for filtering or searching through a set of objects in NetBox. For instance, sites can be filtered by their parent region or group, status, facility ID, and so on. The same filter set is used consistently for a model whether the request is made via the UI or REST API. (Note that the GraphQL API uses a separate filter class.) NetBox employs the [django-filter](https://django-filter.readthedocs.io/en/stable/) library to define filter sets.

## FilterSet Classes

To support additional functionality standard to NetBox models, such as tag assignment and custom field support, the `NetBoxModelFilterSet` class is available for use by plugins. This should be used as the base filter set class for plugin models which inherit from `NetBoxModel`. Within this class, individual filters can be declared as directed by the `django-filters` documentation. An example is provided below.

!!! info "New in NetBox v4.5: FilterSet Registration"
    NetBox v4.5 introduced the `register_filterset()` utility function. This enables plugins to register their filtersets to receive advanced functionality, such as the automatic attachment of field-specific lookup modifiers on the filter form. Registration is optional: Unregistered filtersets will continue to work as before, but will not receive the enhanced functionality.

```python
# filtersets.py
import django_filters
from netbox.filtersets import NetBoxModelFilterSet
from utilities.filtersets import register_filterset
from .models import MyModel

@register_filterset
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

In addition to the base NetBoxModelFilterSet class, the following filterset classes are also available for subclasses of standard base models.

| Model Class           | FilterSet Class                                  |
|-----------------------|--------------------------------------------------|
| `PrimaryModel`        | `netbox.filtersets.PrimaryModelFilterSet`        |
| `OrganizationalModel` | `netbox.filtersets.OrganizationalModelFilterSet` |
| `NestedGroupModel`    | `netbox.filtersets.NestedGroupModelFilterSet`    |

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

To enable a filter set on a REST API endpoint, set the `filterset_class` attribute on the API view:

```python
# api/views.py
from myplugin import models, filtersets
from . import serializers

class MyModelViewSet(...):
    queryset = models.MyModel.objects.all()
    serializer_class = serializers.MyModelSerializer
    filterset_class = filtersets.MyModelFilterSet
```

### Implementing Quick Search

The `ObjectListView` has a field called Quick Search. For Quick Search to work the corresponding FilterSet has to override the `search` method that is implemented in `NetBoxModelFilterSet`. This function takes a queryset and can perform arbitrary operations on it and return it. A common use-case is to search for the given search value in multiple fields:

```python
from django.db.models import Q
from netbox.filtersets import NetBoxModelFilterSet
from utilities.filtersets import register_filterset

@register_filterset
class MyFilterSet(NetBoxModelFilterSet):
    ...
    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )
```

The `search` method is also used by the `q` filter in `NetBoxModelFilterSet` which in turn is used by the Search field in the filters tab.

## Filter Classes

### TagFilter

The `TagFilter` class is available for all models which support tag assignment (those which inherit from `NetBoxModel` or `TagsMixin`). This filter subclasses django-filter's `ModelMultipleChoiceFilter` to work with NetBox's `TaggedItem` class.

This class filters `tags` using the `slug` field. For example:

`GET /api/dcim/sites/?tag=alpha&tag=bravo`


```python
from django_filters import FilterSet
from extras.filters import TagFilter
from utilities.filtersets import register_filterset

@register_filterset
class MyModelFilterSet(FilterSet):
    tag = TagFilter()
```

### TagIDFilter

The `TagIDFilter` class is available for all models which support tag assignment (those which inherit from `NetBoxModel` or `TagsMixin`). This filter subclasses django-filter's `ModelMultipleChoiceFilter` to work with NetBox's `TaggedItem` class.

This class filters `tags` using the `id` field. For example:

`GET /api/dcim/sites/?tag_id=100&tag_id=200`

```python
from django_filters import FilterSet
from extras.filters import TagIDFilter
from utilities.filtersets import register_filterset

@register_filterset
class MyModelFilterSet(FilterSet):
    tag_id = TagIDFilter()
```
