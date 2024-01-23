# Introduction to NetBox

## Origin Story

NetBox was originally developed by its lead maintainer, [Jeremy Stretch](https://github.com/jeremystretch), while he was working as a network engineer at [DigitalOcean](https://www.digitalocean.com/) in 2015 as part of an effort to automate their network provisioning. Recognizing the new tool's potential, DigitalOcean agreed to release it as an open source project in June 2016.

Since then, thousands of organizations around the world have embraced NetBox as their central network source of truth to empower both network operators and automation. Today, the open source project is stewarded by [NetBox Labs](https://netboxlabs.com/) and a team of volunteer maintainers. Beyond the core product, myriad [plugins](https://netbox.dev/plugins/) have been developed by the NetBox community to enhance and expand its feature set.

## Key Features

NetBox was built specifically to serve the needs of network engineers and operators. Below is a very brief overview of the core features it provides.

* IP address management (IPAM) with full IPv4/IPv6 parity
* Automatic provisioning of next available prefix/IP
* VRFs with import & export route targets
* VLANs with variably-scoped groups
* AS number (ASN) management
* Rack elevations with SVG rendering
* Device modeling using pre-defined types
* Virtual chassis and device contexts
* Network, power, and console cabling with SVG traces
* Breakout cables
* Power distribution modeling
* Data circuit and provider tracking
* Wireless LAN and point-to-point links
* VPN tunnels
* IKE & IPSec policies
* Layer 2 VPN overlays
* FHRP groups (VRRP, HSRP, etc.)
* Application service bindings
* Virtual machines & clusters
* Flexible hierarchy for sites and locations
* Tenant ownership assignment
* Device & VM configuration contexts for advanced configuration rendering
* Custom fields for data model extension
* Custom validation & protection rules
* Custom reports & scripts executable directly within the UI
* Extensive plugin framework for adding custom functionality
* Single sign-on (SSO) authentication
* Robust object-based permissions
* Detailed, automatic change logging
* Global search engine
* Event-driven scripts & webhooks

## What NetBox Is Not

While NetBox strives to cover many areas of network management, the scope of its feature set is necessarily limited. This ensures that development focuses on core functionality and that scope creep is reasonably contained. To that end, it might help to provide some examples of functionality that NetBox **does not** provide:

* Network monitoring
* DNS server
* RADIUS server
* Configuration management
* Facilities management

That said, NetBox _can_ be used to great effect in populating external tools with the data they need to perform these functions.

## Design Philosophy

NetBox was designed with the following tenets foremost in mind.

### Replicate the Real World

Careful consideration has been given to the data model to ensure that it can accurately reflect a real-world network. For instance, IP addresses are assigned not to devices, but to specific interfaces attached to a device, and an interface may have multiple IP addresses assigned to it.

### Serve as a "Source of Truth"

NetBox intends to represent the _desired_ state of a network versus its _operational_ state. As such, automated import of live network state is strongly discouraged. All data created in NetBox should first be vetted by a human to ensure its integrity. NetBox can then be used to populate monitoring and provisioning systems with a high degree of confidence.

### Keep it Simple

When given a choice between a relatively simple [80% solution](https://en.wikipedia.org/wiki/Pareto_principle) and a much more complex complete solution, the former will typically be favored. This ensures a lean codebase with a low learning curve.

## Application Stack

NetBox is built on the [Django](https://djangoproject.com/) Python framework and utilizes a [PostgreSQL](https://www.postgresql.org/) database. It runs as a WSGI service behind your choice of HTTP server.

| Function           | Component         |
|--------------------|-------------------|
| HTTP service       | nginx or Apache   |
| WSGI service       | gunicorn or uWSGI |
| Application        | Django/Python     |
| Database           | PostgreSQL 12+    |
| Task queuing       | Redis/django-rq   |
