# NetBox Development

NetBox is maintained as a [GitHub project](https://github.com/digitalocean/netbox) under the Apache 2 license. Users are encouraged to submit GitHub issues for feature requests and bug reports, however we are very selective about pull requests. Please see the `CONTRIBUTING` guide for more direction on contributing to NetBox.

All development of the current NetBox release occurs in the `develop` branch; releases are packaged from the `master` branch. The `master` branch should _always_ represent the current stable release in its entirety, such that installing NetBox by either downloading a packaged release or cloning the `master` branch provides the same code base.

# Project Structure

NetBox components are arranged into functional subsections called _apps_ (a carryover from Django verancular). Each app holds the models, views, and templates relevant to a particular function:

* `circuits`: Communications circuits and providers (not to be confused with power circuits)
* `dcim`: Datacenter infrastructure management (sites, racks, and devices)
* `extras`: Additional features not considered part of the core data model
* `ipam`: IP address management (VRFs, prefixes, IP addresses, and VLANs)
* `secrets`: Encrypted storage of sensitive data (e.g. login credentials)
* `tenancy`: Tenants (such as customers) to which NetBox objects may be assigned
* `utilities`: Resources which are not user-facing (extendable classes, etc.)
* `virtualization`: Virtual machines and clusters

# Style Guide

NetBox generally follows the [Django style guide](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/), which is itself based on [PEP 8](https://www.python.org/dev/peps/pep-0008/). The following exceptions are noted:

* [Pycodestyle](https://github.com/pycqa/pycodestyle) is used to validate code formatting, ignoring certain violations. See `scripts/cibuild.sh`.
* Constants may be imported via wildcard (for example, `from .constants import *`).
