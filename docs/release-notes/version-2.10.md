# NetBox v2.10

## v2.10-beta1 (FUTURE)

**NOTE:** This release completely removes support for embedded graphs.

### Other Changes

* [#4349](https://github.com/netbox-community/netbox/issues/4349) - Dropped support for embedded graphs
* [#4360](https://github.com/netbox-community/netbox/issues/4360) - Remove support for the Django template language from export templates
* [#4941](https://github.com/netbox-community/netbox/issues/4941) - `commit` argument is now required argument in a custom script's `run()` method

### REST API Changes

* extras.ExportTemplate: The `template_language` field has been removed
