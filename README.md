<div align="center">
  <img src="https://raw.githubusercontent.com/netbox-community/netbox/develop/docs/netbox_logo.svg" width="400" alt="NetBox logo" />
  <p><strong>The cornerstone of every automated network</strong></p>
  <a href="https://github.com/netbox-community/netbox/releases"><img src="https://img.shields.io/github/v/release/netbox-community/netbox" alt="Latest release" /></a>
  <a href="https://github.com/netbox-community/netbox/blob/master/LICENSE.txt"><img src="https://img.shields.io/badge/license-Apache_2.0-blue.svg" alt="License" /></a>
  <a href="https://github.com/netbox-community/netbox/graphs/contributors"><img src="https://img.shields.io/github/contributors/netbox-community/netbox?color=blue" alt="Contributors" /></a>
  <a href="https://github.com/netbox-community/netbox/stargazers"><img src="https://img.shields.io/github/stars/netbox-community/netbox?style=flat" alt="GitHub stars" /></a>
  <a href="https://explore.transifex.com/netbox-community/netbox/"><img src="https://img.shields.io/badge/languages-10-blue" alt="Languages supported" /></a>
  <a href="https://github.com/netbox-community/netbox/actions/workflows/ci.yml"><img src="https://github.com/netbox-community/netbox/workflows/CI/badge.svg?branch=master" alt="CI status" /></a>
  <p></p>
</div>

NetBox exists to empower network engineers. Since its release in 2016, it has become the go-to solution for modeling and documenting network infrastructure for thousands of organizations worldwide. As a successor to legacy IPAM and DCIM applications, NetBox provides a cohesive, extensive, and accessible data model for all things networked. By providing a single robust user interface and programmable APIs for everything from cable maps to device configurations, NetBox serves as the central source of truth for the modern network.

<p align="center">
  <a href="#netboxs-role">NetBox's Role</a> |
  <a href="#why-netbox">Why NetBox?</a> |
  <a href="#getting-started">Getting Started</a> |
  <a href="#get-involved">Get Involved</a> |
  <a href="#project-stats">Project Stats</a> |
  <a href="#screenshots">Screenshots</a>
</p>

<p align="center">
  <img src="docs/media/screenshots/home-light.png" width="600" alt="NetBox user interface screenshot" />
</p>

## NetBox's Role

NetBox functions as the **source of truth** for your network infrastructure. Its job is to define and validate the _intended state_ of all network components and resources. NetBox does not interact with network nodes directly; rather, it makes this data available programmatically to purpose-built automation, monitoring, and assurance tools. This separation of duties enables the construction of a robust yet flexible automation system.

<p align="center">
  <img src="docs/media/misc/reference_architecture.png" alt="Reference network automation architecture" />
</p>

The diagram above illustrates the recommended deployment architecture for an automated network, leveraging NetBox as the central authority for network state. This approach allows your team to swap out individual tools to meet changing needs while retaining a predictable, modular workflow.

## Why NetBox?

### Comprehensive Data Model

Racks, devices, cables, IP addresses, VLANs, circuits, power, VPNs, and lots more: NetBox is built for networks. Its comprehensive and thoroughly inter-linked data model provides for natural and highly structured modeling of myriad network primitives that just isn't possible using general-purpose tools. And there's no need to waste time contemplating how to build out a database: Everything is ready to go upon installation.

### Focused Development

NetBox strives to meet a singular goal: Provide the best available solution for making network infrastructure programmatically accessible. Unlike "all-in-one" tools which awkwardly bolt on half-baked features in an attempt to check every box, NetBox is committed to its core function. NetBox provides the best possible solution for modeling network infrastructure, and provides rich APIs for integrating with tools that excel in other areas of network automation.

### Extensible and Customizable

No two networks are exactly the same. Users are empowered to extend NetBox's native data model with custom fields and tags to best suit their unique needs. You can even write your own plugins to introduce entirely new objects and functionality!

### Flexible Permissions

NetBox includes a fully customizable permission system, which affords administrators incredible granularity when assigning roles to users and groups. Want to restrict certain users to working only with cabling and not be able to change IP addresses? Or maybe each team should have access only to a particular tenant? NetBox enables you to craft roles as you see fit.

### Custom Validation & Protection Rules

The data you put into NetBox is crucial to network operations. In addition to its robust native validation rules, NetBox provides mechanisms for administrators to define their own custom validation rules for objects. Custom validation can be used both to ensure new or modified objects adhere to a set of rules, and to prevent the deletion of objects which don't meet certain criteria. (For example, you might want to prevent the deletion of a device with an "active" status.)

### Device Configuration Rendering

NetBox can render user-created Jinja2 templates to generate device configurations from its own data. Configuration templates can be uploaded individually or pulled automatically from an external source, such as a git repository. Rendered configurations can be retrieved via the REST API for application directly to network devices via a provisioning tool such as Ansible or Salt.

### Custom Scripts

Complex workflows, such as provisioning a new branch office, can be tedious to carry out via the user interface. NetBox allows you to write and upload custom scripts that can be run directly from the UI. Scripts prompt users for input and then automate the necessary tasks to greatly simplify otherwise burdensome processes.

### Automated Events

Users can define event rules to automatically trigger a custom script or outbound webhook in response to a NetBox event. For example, you might want to automatically update a network monitoring service whenever a new device is added to NetBox, or update a DHCP server when an IP range is allocated.

### Comprehensive Change Logging

NetBox automatically logs the creation, modification, and deletion of all managed objects, providing a thorough change history. Changes can be attributed to the executing user, and related changes are grouped automatically by request ID.

> [!NOTE]
> A complete list of NetBox's myriad features can be found in [the introductory documentation](https://docs.netbox.dev/en/stable/introduction/).

## Getting Started

* Just want to explore? Check out [our public demo](https://demo.netbox.dev/) right now!
* The [official documentation](https://docs.netbox.dev) offers a comprehensive introduction.
* Check out [our wiki](https://github.com/netbox-community/netbox/wiki/Community-Contributions) for even more projects to get the most out of NetBox!

<p align="center">
  <a href="https://netboxlabs.com/netbox-cloud/"><img src="docs/media/misc/netbox_cloud.png" alt="NetBox Cloud" /></a><br />
  Looking for a managed solution? Check out <strong><a href="https://netboxlabs.com/netbox-cloud/">NetBox Cloud</a></strong> or <strong><a href="https://netboxlabs.com/netbox-enterprise/">NetBox Enterprise</a></strong>!
</p>

## Get Involved

* Follow [@NetBoxOfficial](https://twitter.com/NetBoxOfficial) on Twitter!
* Join the conversation on [the discussion forum](https://github.com/netbox-community/netbox/discussions) and [Slack](https://netdev.chat/)!
* Already a power user? You can [suggest a feature](https://github.com/netbox-community/netbox/issues/new?assignees=&labels=type%3A+feature&template=feature_request.yaml) or [report a bug](https://github.com/netbox-community/netbox/issues/new?assignees=&labels=type%3A+bug&template=bug_report.yaml) on GitHub.
* Contributions from the community are encouraged and appreciated! Check out our [contributing guide](CONTRIBUTING.md) to get started.
* [Share your idea](https://plugin-ideas.netbox.dev/) for a new plugin, or [learn how to build one](https://github.com/netbox-community/netbox-plugin-tutorial) yourself!

## Screenshots

<p align="center">
  <strong>NetBox Dashboard (Light Mode)</strong><br />
  <img src="docs/media/screenshots/home-light.png" width="600" alt="NetBox dashboard (light mode)" />
</p>
<p align="center">
  <strong>NetBox Dashboard (Dark Mode)</strong><br />
  <img src="docs/media/screenshots/home-dark.png" width="600" alt="NetBox dashboard (dark mode)" />
</p>
<p align="center">
  <strong>Prefixes List</strong><br />
  <img src="docs/media/screenshots/prefixes-list.png" width="600" alt="Prefixes list" />
</p>
<p align="center">
  <strong>Rack View</strong><br />
  <img src="docs/media/screenshots/rack.png" width="600" alt="Rack view" />
</p>
<p align="center">
  <strong>Cable Trace</strong><br />
  <img src="docs/media/screenshots/cable-trace.png" width="600" alt="Cable trace" />
</p>
