# Search

## Global Search

NetBox includes a powerful global search engine, providing a single convenient interface to search across its complex data model. Relevant fields on each model are indexed according to their precedence, so that the most relevant results are returned first. When objects are created or modified, the search index is updated immediately, ensuring real-time accuracy.

When entering a search query, the user can choose a specific lookup type: exact match, partial match, etc. When a partial match is found, the matching portion of the applicable field value is included with each result so that the user can easily determine its relevance.

Custom fields defined by NetBox administrators are also included in search results if configured with a search weight. Additionally, NetBox plugins can register their own custom models for inclusion alongside core models.

!!! note
    NetBox does not index any static choice field's (including custom fields of type "Selection" or "Multiple selection").

## Saved Filters

Each type of object in NetBox is accompanied by an extensive set of filters, each tied to a specific attribute, which enable the creation of complex queries. Often you'll find that certain queries are used routinely to apply some set of prescribed conditions to a query. Once a set of filters has been applied, NetBox offers the option to save it for future use.

For example, suppose you often need to locate all planned devices of a certain type within a region. The applicable filters can be applied and then saved as custom named filter for reuse, such that

```
?status=planned&device_type_id=78&region_id=12
```

becomes

```
?filter=my-custom-filter
```

These saved filters can be used both within the UI and for API queries.
