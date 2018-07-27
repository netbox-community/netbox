![NetBox](netbox_logo.png "NetBox logo")

# What is NetBox?

NetBox is an open source web application designed to help manage and document computer networks. Initially conceived by the network engineering team at [DigitalOcean](https://www.digitalocean.com/), NetBox was developed specifically to address the needs of network and infrastructure engineers. It encompasses the following aspects of network management:

* **IP address management (IPAM)** - IP networks and addresses, VRFs, and VLANs
* **Equipment racks** - Organized by group and site
* **Devices** - Types of devices and where they are installed
* **Connections** - Network, console, and power connections among devices
* **Virtualization** - Virtual machines and clusters
* **Data circuits** - Long-haul communications circuits and providers
* **Secrets** - Encrypted storage of sensitive credentials

# What NetBox Is Not

While NetBox strives to cover many areas of network management, the scope of its feature set is necessarily limited. This ensures that development focuses on core functionality and that scope creep is reasonably contained. To that end, it might help to provide some examples of functionality that NetBox **does not** provide:

* Network monitoring
* DNS server
* RADIUS server
* Configuration management
* Facilities management

That said, NetBox _can_ be used to great effect in populating external tools with the data they need to perform these functions.

# Design Philosophy

NetBox was designed with the following tenets foremost in mind.

## Replicate the Real World

Careful consideration has been given to the data model to ensure that it can accurately reflect a real-world network. For instance, IP addresses are assigned not to devices, but to specific interfaces attached to a device, and an interface may have multiple IP addresses assigned to it.

## Serve as a "Source of Truth"

NetBox intends to represent the _desired_ state of a network versus its _operational_ state. As such, automated import of live network state is strongly discouraged. All data created in NetBox should first be vetted by a human to ensure its integrity. NetBox can then be used to populate monitoring and provisioning systems with a high degree of confidence.

## Keep it Simple

When given a choice between a relatively simple [80% solution](https://en.wikipedia.org/wiki/Pareto_principle) and a much more complex complete solution, the former will typically be favored. This ensures a lean codebase with a low learning curve.

# Application Stack

NetBox is built on the [Django](https://djangoproject.com/) Python framework and utilizes a [PostgreSQL](https://www.postgresql.org/) database. It runs as a WSGI service behind your choice of HTTP server.

| Function           | Component         |
|--------------------|-------------------|
| HTTP service       | nginx or Apache   |
| WSGI service       | gunicorn or uWSGI |
| Application        | Django/Python     |
| Database           | PostgreSQL 9.4+   |
| Task queuing       | Redis/django-rq   |
| Live device access | NAPALM            |

# Getting Started

See the [installation guide](installation/index.md) for help getting NetBox up and running quickly.
