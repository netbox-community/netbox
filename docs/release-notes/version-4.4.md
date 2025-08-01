# NetBox v4.4

## v4.4.0 (FUTURE)

### New Features

#### Background Jobs for Bulk Operations ([#19589](https://github.com/netbox-community/netbox/issues/19589), [#19891](https://github.com/netbox-community/netbox/issues/19891))

Most bulk operations, such as the import, modification, or deletion of objects can now be executed as a background job. This frees the user to continue working in NetBox while the bulk operation is processed. Once completed, the user will be notified of the job's result.

#### Logging Mechanism for Background Jobs ([#19891](https://github.com/netbox-community/netbox/issues/19816))

A dedicated logging mechanism has been implemented for background jobs. Jobs can now easily record log messages by calling e.g. `self.logger.info("Log message")` under the `run()` method. These messages are displayed along with the job's resulting data. Supported log levels include `DEBUG`, `INFO`, `WARNING`, and `ERROR`.

#### Changelog Comments ([#19713](https://github.com/netbox-community/netbox/issues/19713))

When creating, editing, or deleting objects in NetBox, users now have the option of providing a short message explaining the change. This message will be recorded on the resulting changelog records for all affected objects.

### Enhancements

* [#17413](https://github.com/netbox-community/netbox/issues/17413) - Platforms belonging to different manufacturers may now have identical names
* [#18204](https://github.com/netbox-community/netbox/issues/18204) - Improved layout of the image attachments view & tables
* [#18528](https://github.com/netbox-community/netbox/issues/18528) - Introduced the `HOSTNAME` configuration parameter to override the system hostname reported by NetBox
* [#18990](https://github.com/netbox-community/netbox/issues/18990) - Image attachments now include an optional description field
* [#19134](https://github.com/netbox-community/netbox/issues/19134) - Interface transmit power now accepts negative values
* [#19231](https://github.com/netbox-community/netbox/issues/19231) - Bulk renaming support has been implemented in the UI for most object types
* [#19591](https://github.com/netbox-community/netbox/issues/19591) - Thumbnails for all images attached to an object are now displayed under a dedicated tab
* [#19722](https://github.com/netbox-community/netbox/issues/19722) - The REST API endpoint for object types has been extended to include additional details
* [#19739](https://github.com/netbox-community/netbox/issues/19739) - Introduced a user preference for CSV delimiter
* [#19893](https://github.com/netbox-community/netbox/issues/19893) - The `/api/status/` REST API endpoint now includes the system hostname
* [#19920](https://github.com/netbox-community/netbox/issues/19920) - Contacts can now be assigned to ASNs
* [#19945](https://github.com/netbox-community/netbox/issues/19945) - Introduce a new custom script variable to represent decimal values
* [#19965](https://github.com/netbox-community/netbox/issues/19965) - Add REST & GraphQL API request counters to the Prometheus metrics exporter

### Plugins

* [#19735](https://github.com/netbox-community/netbox/issues/19735) - Custom individual and bulk operations can now be registered under individual views using `ObjectAction`

### Other Changes

* [#18349](https://github.com/netbox-community/netbox/issues/18349) - The housekeeping script has been replaced with a system job
* [#18588](https://github.com/netbox-community/netbox/issues/18588) - The "Service" model has been renamed to "Application Service" for clarity (UI change only)
* [#19829](https://github.com/netbox-community/netbox/issues/19829) - The REST API endpoint for object types is now available under `/api/core/`
* [#19924](https://github.com/netbox-community/netbox/issues/19924) - ObjectTypes are now tracked as concrete objects in the database (alongside ContentTypes)
* [#19973](https://github.com/netbox-community/netbox/issues/19973) - Miscellaneous improvements to the `nbhshell` management command

### REST API Changes

* The `/api/status/` endpoint now includes the system hostname.
* The `/api/extras/object-types/` endpoint is now available at `/api/core/object-types/`. (The original endpoint will be removed in NetBox v4.5.)
* The `/api/core/object-types/` endpoint has been expanded to include the following read-only fields:
    * `app_name`
    * `model_name`
    * `model_name_plural`
    * `is_plugin_model`
    * `rest_api_endpoint`
    * `description`
* dcim.Interface
    * The `tx_power` field now accepts negative values
* extras.ImageAttachment
    * Added an optional `description` field
