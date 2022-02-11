# NetBox Development

NetBox is maintained as a [GitHub project](https://github.com/netbox-community/netbox) under the Apache 2 license. Users are encouraged to submit GitHub issues for feature requests and bug reports, however we are very selective about pull requests. Each pull request must be preceded by an **approved** issue. Please see the `CONTRIBUTING` guide for more direction on contributing to NetBox.

## Communication

There are several official forums for communication among the developers and community members:

* [GitHub issues](https://github.com/netbox-community/netbox/issues) - All feature requests, bug reports, and other substantial changes to the code base **must** be documented in a GitHub issue.
* [GitHub Discussions](https://github.com/netbox-community/netbox/discussions) - The preferred forum for general discussion and support issues. Ideal for shaping a feature request prior to submitting an issue.
* [#netbox on NetDev Community Slack](https://netdev.chat/) - Good for quick chats. Avoid any discussion that might need to be referenced later on, as the chat history is not retained long.
* [Google Group](https://groups.google.com/g/netbox-discuss) - Legacy mailing list; slowly being phased out in favor of GitHub discussions.

## Governance

NetBox follows the [benevolent dictator](http://oss-watch.ac.uk/resources/benevolentdictatorgovernancemodel) model of governance, with [Jeremy Stretch](https://github.com/jeremystretch) ultimately responsible for all changes to the code base. While community contributions are welcomed and encouraged, the lead maintainer's primary role is to ensure the project's long-term maintainability and continued focus on its primary functions.

## Project Structure

All development of the current NetBox release occurs in the `develop` branch; releases are packaged from the `master` branch. The `master` branch should _always_ represent the current stable release in its entirety, such that installing NetBox by either downloading a packaged release or cloning the `master` branch provides the same code base. Only pull requests representing new releases should be merged into `master`.

NetBox components are arranged into Django apps. Each app holds the models, views, and other resources relevant to a particular function:

* `circuits`: Communications circuits and providers (not to be confused with power circuits)
* `dcim`: Datacenter infrastructure management (sites, racks, and devices)
* `extras`: Additional features not considered part of the core data model
* `ipam`: IP address management (VRFs, prefixes, IP addresses, and VLANs)
* `tenancy`: Tenants (such as customers) to which NetBox objects may be assigned
* `users`: Authentication and user preferences
* `utilities`: Resources which are not user-facing (extendable classes, etc.)
* `virtualization`: Virtual machines and clusters
* `wireless`: Wireless links and LANs

All core functionality is stored within the `netbox/` subdirectory. HTML templates are stored in a common `templates/` directory, with model- and view-specific templates arranged by app. Documentation is kept in the `docs/` root directory.
