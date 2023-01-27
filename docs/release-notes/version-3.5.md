# NetBox v3.5

## v3.5.0 (FUTURE)

### Enhancements

* [#11517](https://github.com/netbox-community/netbox/issues/11517) - Standardize the inclusion of related objects across the entire UI
* [#11584](https://github.com/netbox-community/netbox/issues/11584) - Add a list view for contact assignments
* [#11254](https://github.com/netbox-community/netbox/issues/11254) - Introduce the `X-Request-ID` HTTP header to annotate the unique ID of each request for change logging
* [#11440](https://github.com/netbox-community/netbox/issues/11440) - Add an `enabled` field for device type interfaces

### Other Changes

* [#10604](https://github.com/netbox-community/netbox/issues/10604) - Remove unused `extra_tabs` block from `object.html` generic template
* [#10923](https://github.com/netbox-community/netbox/issues/10923) - Remove unused `NetBoxModelCSVForm` class (replaced by `NetBoxModelImportForm`)
* [#11611](https://github.com/netbox-community/netbox/issues/11611) - Refactor API viewset classes and introduce NetBoxReadOnlyModelViewSet
