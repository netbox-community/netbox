# Search

Plugins can define and register their own models to extend NetBox's core search functionality. Typically, a plugin will include a file named `search.py`, which holds all search indexes for its models.

```python title="search.py"
# search.py
from netbox.search import SearchIndex, register_search

from .models import MyModel

@register_search
class MyModelIndex(SearchIndex):
    model = MyModel
    fields = (
        ('name', 100),
        ('description', 500),
        ('comments', 5000),
    )
    display_attrs = ('site', 'device', 'status', 'description')
```

Decorate each `SearchIndex` subclass with `@register_search` to register it with NetBox. When using the default `search.py` module, no additional `indexes = [...]` list is required.

Fields listed in `display_attrs` are not cached for matching, but they are displayed alongside the object in global search results to provide additional context.

!!! tip
    The legacy `indexes = [...]` list remains supported via `PluginConfig.search_indexes` for backward compatibility and custom loading patterns.

::: netbox.search.SearchIndex
