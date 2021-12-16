# NetBox v3.2

## v3.2.0 (FUTURE)

!!! warning "Python 3.8 or Later Required"
    NetBox v3.2 requires Python 3.8 or later.

### Breaking Changes

* Automatic redirection of legacy slug-based URL paths has been removed.
* The `asn` field has been removed from the site model. Please use the ASN model introduced in NetBox v3.1 to track ASN assignments for sites.
* The `asn` query filter for sites now matches against the AS number of assigned ASNs.
* The `contact_name`, `contact_phone`, and `contact_email` fields have been removed from the site model. Please use the new contact model introduced in NetBox v3.1 to store contact information for sites.

### New Features

#### Custom Status Choices ([#8054](https://github.com/netbox-community/netbox/issues/8054))

Custom choices can be now added to most status fields in NetBox. This is done by defining the `FIELD_CHOICES` configuration parameter to map field identifiers to an iterable of custom choices. These choices are populated automatically when NetBox initializes. For example, the following will add three custom choices for the site status field:

```python
FIELD_CHOICES = {
    'dcim.Site.status': (
        ('foo', 'Foo'),
        ('bar', 'Bar'),
        ('baz', 'Baz'),
    )
}
```

### Enhancements

* [#7650](https://github.com/netbox-community/netbox/issues/7650) - Add support for local account password validation

### Other Changes

* [#7731](https://github.com/netbox-community/netbox/issues/7731) - Require Python 3.8 or later
* [#7743](https://github.com/netbox-community/netbox/issues/7743) - Remove legacy ASN field from site model
* [#7748](https://github.com/netbox-community/netbox/issues/7748) - Remove legacy contact fields from site model
* [#8031](https://github.com/netbox-community/netbox/issues/8031) - Remove automatic redirection of legacy slug-based URLs

### REST API Changes

* dcim.Site
    * Removed the `asn`, `contact_name`, `contact_phone`, and `contact_email` fields
