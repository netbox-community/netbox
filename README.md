<div align="center">
  <img src="https://raw.githubusercontent.com/netbox-community/netbox/develop/docs/netbox_logo.svg" width="400" alt="NetBox logo" />
</div>

![Master branch build status](https://github.com/netbox-community/netbox/workflows/CI/badge.svg?branch=master)

NetBox is the leading solution for modeling and documenting modern networks. By
combining the traditional disciplines of IP address management (IPAM) and
datacenter infrastructure management (DCIM) with powerful APIs and extensions,
NetBox provides the ideal "source of truth" to power network automation.
Available as open source software under the Apache 2.0 license, NetBox is
employed by thousands of organizations around the world.

![Screenshot of Netbox UI](docs/media/screenshots/netbox-ui.png "NetBox UI")

Myriad infrastructure components can be modeled in NetBox, including:

* Hierarchical regions, site groups, sites, and locations
* Racks, devices, and device components
* Cables and wireless connections
* Power distribution
* Data circuits and providers
* Virtual machines and clusters
* IP prefixes, ranges, and addresses
* VRFs and route targets
* L2VPN and overlays
* FHRP groups (VRRP, HSRP, etc.)
* AS numbers
* VLANs and scoped VLAN groups
* Organizational tenants and contacts

In addition to its extensive built-in models and functionality, NetBox can be
customized and extended through the use of:

* Custom fields
* Custom links
* Configuration contexts
* Custom model validation rules
* Reports
* Custom scripts
* Export templates
* Conditional webhooks
* Plugins
* Single sign-on (SSO) authentication
* NAPALM integration
* Detailed change logging

NetBox also features a complete REST API as well as a GraphQL API for easily
integrating with other tools and systems.

The complete documentation for NetBox can be found at [docs.netbox.dev](https://docs.netbox.dev/).
A public demo instance is available at [demo.netbox.dev](https://demo.netbox.dev).

NetBox runs as a web application atop the [Django](https://www.djangoproject.com/)
Python framework with a [PostgreSQL](https://www.postgresql.org/) database. For a
complete list of requirements, see `requirements.txt`. The code is available
[on GitHub](https://github.com/netbox-community/netbox).

<div align="center">
  <h4>Thank you to our sponsors!</h4>

  [![DigitalOcean](https://raw.githubusercontent.com/wiki/netbox-community/netbox/images/sponsors/digitalocean.png)](https://try.digitalocean.com/developer-cloud)
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  [![Equinix Metal](https://raw.githubusercontent.com/wiki/netbox-community/netbox/images/sponsors/equinix.png)](https://metal.equinix.com/)
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  [![NS1](https://raw.githubusercontent.com/wiki/netbox-community/netbox/images/sponsors/ns1.png)](https://ns1.com/)
  <br />
  [![Sentry](https://raw.githubusercontent.com/wiki/netbox-community/netbox/images/sponsors/sentry.png)](https://sentry.io/)
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  [![Stellar Technologies](https://raw.githubusercontent.com/wiki/netbox-community/netbox/images/sponsors/stellar.png)](https://stellar.tech/)

</div>

### Discussion

* [GitHub Discussions](https://github.com/netbox-community/netbox/discussions) - Discussion forum hosted by GitHub; ideal for Q&A and other structured discussions
* [Slack](https://netdev.chat/) - Real-time chat hosted by the NetDev Community; best for unstructured discussion or just hanging out

### Installation

Please see [the documentation](https://docs.netbox.dev/) for
instructions on installing NetBox. To upgrade NetBox, please download the
[latest release](https://github.com/netbox-community/netbox/releases) and
run `upgrade.sh`.

### Providing Feedback

The best platform for general feedback, assistance, and other discussion is our
[GitHub discussions](https://github.com/netbox-community/netbox/discussions).
To report a bug or request a specific feature, please open a GitHub issue using
the [appropriate template](https://github.com/netbox-community/netbox/issues/new/choose).

If you are interested in contributing to the development of NetBox, please read
our [contributing guide](CONTRIBUTING.md) prior to beginning any work.

### Screenshots

![Screenshot of main page (dark mode)](docs/media/screenshots/home-dark.png "Main page (dark mode)")

![Screenshot of rack elevation](docs/media/screenshots/rack.png "Rack elevation")

![Screenshot of prefixes hierarchy](docs/media/screenshots/prefixes-list.png "Prefixes hierarchy")

![Screenshot of cable trace](docs/media/screenshots/cable-trace.png "Cable tracing")

### Related projects

Please see [our wiki](https://github.com/netbox-community/netbox/wiki/Community-Contributions)
for a list of relevant community projects.
