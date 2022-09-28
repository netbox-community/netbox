# Search

If you want your plugin models to appear in search results, you will need to create a search index for the models.  Search indexes must be in defined in a search_indexes.py file.

As an example, lets define a search_index for the MyModel object defined before:

```python
# search_indexes.py
from .filters import MyFilterSet
from .tables import MyModelTable
from .models import MyModel
from search.models import SearchMixin


class MyModelIndex(SearchMixin):
    model = MyModel
    queryset = MyModel.objects.all()
    filterset = MyModelFilterSet
    table = MyModelTable
    url = 'plugins:netbox_mymodel:mymodel_list'
    choice_header = 'MyModel'
```

All the fields must be defined as follows:

* `model` - The model that will be searched (see: [Models](./models.md)).
* `queryset` - The queryset on the model that will be passed to the filterset.
* `filterset` - The filterset for the model that contains the search method (see: [Filters & Filter Sets](./filtersets.md)).
* `table` - Table that is used in the list view (see:  (see: [Tables](./tables.md)).
* `url` - URL to the list view to show search results.
* `choice_header` - The header that will appear in the search drop-down to group menu items together.
