# NetBox v3.3

## v3.3.0 (FUTURE)

### Enhancements

* [#8495](https://github.com/netbox-community/netbox/issues/8495) - Enable custom field grouping
* [#8995](https://github.com/netbox-community/netbox/issues/8995) - Enable arbitrary ordering of REST API results

### Other Changes

* [#9261](https://github.com/netbox-community/netbox/issues/9261) - `NetBoxTable` no longer automatically clears pre-existing calls to `prefetch_related()` on its queryset

### REST API Changes

* extras.CustomField
    * Added `group_name` field
