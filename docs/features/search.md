# Search

## Global Search

NetBox includes a powerful global search engine, providing a single convenient interface to search across its complex data model. Relevant fields on each model are indexed according to their precedence, so that the most relevant results are returned first. When objects are created, modified, or deleted, the search index is updated by a background task shortly afterward. As a result, a newly created or changed object may not appear in search results for a brief period. (When no background worker is running, the index is updated immediately as part of the request.)

When entering a search query, the user can choose a specific lookup type: exact match, partial match, etc. When a partial match is found, the matching portion of the applicable field value is included with each result so that the user can easily determine its relevance.

Custom fields defined by NetBox administrators are also included in search results if configured with a search weight. Additionally, NetBox plugins can register their own custom models for inclusion alongside core models.

### Deferred indexing

To avoid enqueuing a separate background job for every change, search index updates are coalesced: changes committed over a short interval are buffered and applied together by a single background job. This settles quickly (on the order of a couple of seconds) when workers are running. A recurring safety-net job also recovers any pending updates whose drain was lost (for example, if a worker was stopped mid-run), so indexing is eventually consistent even after a worker restart. Because a background drain can run longer than its Redis lease, overlapping applies are prevented by a database-level lock, so an object's index entries are never duplicated.

The pending buffer is stored in the tasks Redis database. If that Redis data is lost, some recent index updates may be discarded; run `manage.py reindex` to rebuild the search index from the database.

If a buffered batch repeatedly fails to apply (for example, due to a persistent database error), it is retried by the safety-net job a limited number of times and then discarded, with the failure recorded at error level in the system log. The objects in a discarded batch will not be re-indexed until they are saved again; run `manage.py reindex` to rebuild the search index from the database.

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
