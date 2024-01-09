<div align="center">
  <img src="https://raw.githubusercontent.com/netbox-community/netbox/develop/docs/netbox_logo.svg" width="400" alt="NetBox logo" />
  <p><strong>The cornerstone of every automated network</strong></p>
  <a href="https://github.com/netbox-community/netbox/releases"><img src="https://img.shields.io/github/v/release/netbox-community/netbox" alt="Latest release" /></a>
  <a href="https://github.com/netbox-community/netbox/blob/develop/README.md"><img src="https://img.shields.io/badge/license-Apache_2.0-blue.svg" alt="License" /></a>
  <a href="https://github.com/netbox-community/netbox/graphs/contributors"><img src="https://img.shields.io/github/contributors/netbox-community/netbox?color=blue" alt="Contributors" /></a>
  <img src="https://img.shields.io/github/stars/netbox-community/netbox?style=flat" alt="GitHub stars" />
  <img src="https://img.shields.io/badge/languages-4-blue" alt="Languages supported" />
  <img src="https://github.com/netbox-community/netbox/workflows/CI/badge.svg?branch=master" alt="CI status" />
  <p></p>
</div>

NetBox exists to empower network engineers. Since its release in 2016, it has become the go-to solution for modeling and documenting network infrastructure for thousands of organizations worldwide. As a successor to legacy IPAM and DCIM applications, NetBox provides a cohesive, extensive, and accessible data model for all things networked. By providing a single robust user interface and programmable APIs for everything from cable maps to device configurations, NetBox serves as the central source of truth for the modern network.

<div align="center">
  <img src="docs/media/screenshots/netbox-ui.png" width="600" alt="NetBox user interface screenshot" />
</div>

<p align="center">
  <a href="#why-netbox">Why NetBox?</a> |
  <a href="#getting-started">Getting Started</a> |
  <a href="#get-involved">Get Involved</a> |
  <a href="#project-stats">Project Stats</a> |
  <a href="#screenshots">Screenshots</a>
</p>

## Why NetBox?

### Comprehensive Data Model

Racks, devices, cables, IP addresses, VLANs, circuits, power, VPNs, and lots more: NetBox is built for networks. Its comprehensive and thoroughly inter-linked data model provides for natural and robust modeling of myriad network primitives that just can't be matched by general-purpose tools. And there's no need to waste time contemplating how to set up your database: Everything is ready to go upon installation.

### Focused Development

NetBox strives to meet a singular goal: Provide the best available solution for making network infrastructure programmatically accessible. Unlike "all-in-one" tools which awkwardly bolt on half-baked features in an attempt to check every box, NetBox is committed to its central focus. NetBox provides the best possible solution for modeling network infrastructure, and provides rich APIs for integrating with tools that excel in other areas of network automation.

### Extensible and Customizable

Of course, no two networks are exactly the same. Users are empowered to extend NetBox's native data model with custom fields and tags to best suit their unique needs. You can even write your own plugins to introduce entirely new models and functionality!

### Flexible Permissions

NetBox includes a fully customizable permission system, which affords administrators incredible granularity when assigning roles to users and groups. Want to restrict certain users to working only with cabling and not be able to change IP addresses? Or maybe each team should have access only to a particular tenant? NetBox enables you to craft roles as you see fit.

### Custom Validation & Protection Rules

The data you put into NetBox is crucial. In addition to its robust native validation rules, NetBox provides mechanisms for administrators to define their own custom validation rules for objects. Custom validation can be used both to ensure new or modified objects adhere to a set of rules, and to prevent the deletion of objects which don't meet certain criteria. (For example, you might want to prevent the deletion of a device with an "active" status.)

### Device Configuration Rendering

NetBox can render user-created Jinja2 templates to generate device configurations from its own data. Templates can be uploaded individually or pulled automatically from an external source, such as a git repository. Rendered templates can be retrieved via the REST API for application directly to network devices via a provisioning tool such as Ansible or Salt.

### Custom Scripts

Complex workflows, such as provisioning a new branch office or allocating a new address block, can be tedious to carry out via the user interface. NetBox allows you to write and upload custom scripts that can be run directly from the UI. Scripts prompt users for input and then automate the necessary tasks to greatly simplify otherwise burdensome processes.

### Automated Events

Users can define event rules to automatically trigger a custom script or outbound webhook in response to a NetBox event. For example, you might want to automatically update a network monitoring service whenever a new device is added to NetBox, or update a DHCP server when an IP range is allocated.

### Comprehensive Change Logging

NetBox automatically logs the creation, modification, and deletion of all managed objects, providing a thorough change history. Changes can be attributed to the executing user, and related changes are grouped automatically by request ID.

## Getting Started

<div align="center">

  [![NetBox logo](https://raw.githubusercontent.com/wiki/netbox-community/netbox/images/deploy/deploy1.png)](https://github.com/netbox-community/netbox)
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  [![Docker logo](https://raw.githubusercontent.com/wiki/netbox-community/netbox/images/deploy/deploy2.png)](https://github.com/netbox-community/netbox-docker)
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  [![NetBox Labs logo](https://raw.githubusercontent.com/wiki/netbox-community/netbox/images/deploy/deploy3.png)](https://netboxlabs.com/netbox-cloud/)

</div>

* Just want to explore? Check out [our public demo](https://demo.netbox.dev/) right now!
* The [official documentation](https://docs.netbox.dev) offers a comprehensive introduction.
* Check out [our wiki](https://github.com/netbox-community/netbox/wiki/Community-Contributions) for even more projects to get the most out of NetBox!

## Get Involved

* Follow [@NetBoxOfficial](https://twitter.com/NetBoxOfficial) on Twitter!
* Join the conversation on [the discussion forum](https://github.com/netbox-community/netbox/discussions) and [Slack](https://netdev.chat/)!
* Already a power user? You can [suggest a feature](https://github.com/netbox-community/netbox/issues/new?assignees=&labels=type%3A+feature&template=feature_request.yaml) or [report a bug](https://github.com/netbox-community/netbox/issues/new?assignees=&labels=type%3A+bug&template=bug_report.yaml) on GitHub.
* Contributions from the community are encouraged and appreciated! Check out our [contributing guide](CONTRIBUTING.md) to get started.

## Project Stats

<div align="center">
  <a href="https://github.com/netbox-community/netbox/commits"><img src="https://images.repography.com/29023055/netbox-community/netbox/recent-activity/whQtEr_TGD9PhW1BPlhlEQ5jnrgQ0KJpm-LlGtpoGO0/3Kx_iWUSBRJ5-AI4QwJEJWrUDEz3KrX2lvh8aYE0WXY_timeline.svg" alt="Timeline graph"></a>
  <a href="https://github.com/netbox-community/netbox/issues"><img src="https://images.repography.com/29023055/netbox-community/netbox/recent-activity/whQtEr_TGD9PhW1BPlhlEQ5jnrgQ0KJpm-LlGtpoGO0/3Kx_iWUSBRJ5-AI4QwJEJWrUDEz3KrX2lvh8aYE0WXY_issues.svg" alt="Issues graph"></a>
  <a href="https://github.com/netbox-community/netbox/pulls"><img src="https://images.repography.com/29023055/netbox-community/netbox/recent-activity/whQtEr_TGD9PhW1BPlhlEQ5jnrgQ0KJpm-LlGtpoGO0/3Kx_iWUSBRJ5-AI4QwJEJWrUDEz3KrX2lvh8aYE0WXY_prs.svg" alt="Pull requests graph"></a>
  <a href="https://github.com/netbox-community/netbox/graphs/contributors"><img src="https://images.repography.com/29023055/netbox-community/netbox/recent-activity/whQtEr_TGD9PhW1BPlhlEQ5jnrgQ0KJpm-LlGtpoGO0/3Kx_iWUSBRJ5-AI4QwJEJWrUDEz3KrX2lvh8aYE0WXY_users.svg" alt="Top contributors"></a>
  <br />Stats via <a href="https://repography.com">Repography</a>
</div>

## Screenshots

![Screenshot of main page (dark mode)](docs/media/screenshots/home-dark.png "Main page (dark mode)")

![Screenshot of rack elevation](docs/media/screenshots/rack.png "Rack elevation")

![Screenshot of prefixes hierarchy](docs/media/screenshots/prefixes-list.png "Prefixes hierarchy")

![Screenshot of cable trace](docs/media/screenshots/cable-trace.png "Cable tracing")
