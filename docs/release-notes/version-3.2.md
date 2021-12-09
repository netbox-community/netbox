# NetBox v3.2

## v3.2.0 (FUTURE)

!!! warning "Python 3.8 or Later Required"
    NetBox v3.2 requires Python 3.8 or later.

### Breaking Changes

* Automatic redirection of legacy slug-based URL paths has been removed.
* The `contact_name`, `contact_phone`, and `contact_email` fields have been removed from the site model. Please use the new contact model introduced in NetBox v3.1 to store contact information for sites.

### Other Changes

* [#7731](https://github.com/netbox-community/netbox/issues/7731) - Require Python 3.8 or later
* [#7748](https://github.com/netbox-community/netbox/issues/7748) - Remove legacy contact fields from site model
* [#8031](https://github.com/netbox-community/netbox/issues/8031) - Remove automatic redirection of legacy slug-based URLs

### REST API Changes

* dcim.Site
    * Removed the `contact_name`, `contact_phone`, and `contact_email` fields
