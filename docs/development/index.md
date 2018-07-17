# NetBox Structure

NetBox components are arranged into functional subsections called _apps_ (a carryover from Django verancular). Each app holds the models, views, and templates relevant to a particular function:

* `circuits`: Communications circuits and providers (not to be confused with power circuits)
* `dcim`: Datacenter infrastructure management (sites, racks, and devices)
* `ipam`: IP address management (VRFs, prefixes, IP addresses, and VLANs)
* `secrets`: Encrypted storage of sensitive data (e.g. login credentials)
* `tenancy`: Tenants (such as customers) to which NetBox objects may be assigned
* `virtualization`: Virtual machines and clusters
