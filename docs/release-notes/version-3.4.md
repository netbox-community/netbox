# NetBox v3.4

!!! warning "PostgreSQL 11 Required"
    NetBox v3.4 requires PostgreSQL 11 or later.

### Enhancements

* [#9892](https://github.com/netbox-community/netbox/issues/9892) - Add optional `name` field for FHRP groups

### Plugins API

* [#10314](https://github.com/netbox-community/netbox/issues/10314) - Move `clone()` method from NetBoxModel to CloningMixin

### Other Changes

* [#10358](https://github.com/netbox-community/netbox/issues/10358) - Raise minimum required PostgreSQL version from 10 to 11

### REST API Changes

* ipam.FHRPGroup
    * Added optional `name` field
