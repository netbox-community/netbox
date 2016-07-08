# What is NetBox?

NetBox is an open source web application designed to help manage and document computer networks. Initially conceived by the network engineering team at [DigitalOcean](https://www.digitalocean.com/), NetBox was developed specifically to address the needs of network and infrastructure engineers. It encompasses the following aspects of network management:

* **IP address management (IPAM)** - IP networks and addresses, VRFs, and VLANs
* **Equipment racks** - Organized by group and site
* **Devices** - Types of devices and where they are installed
* **Connections** - Network, console, and power connections among devices
* **Data circuits** - Long-haul communications circuits and providers
* **Secrets** - Encrypted storage of sensitive credentials

It was designed with the following tenets foremost in mind.

## Replicate the Real World

Careful consideration has been given to the data model to ensure that it can accurately reflect a real-world network. For instance, IP addresses are assigned not to devices, but to specific interfaces attached to a device, and an interface may have multiple IP addresses assigned to it.

## Serve as a "Source of Truth"

NetBox intends to represent the _desired_ state of a network versus its _operational_ state. As such, automated import of live network state is strongly discouraged. All data created in NetBox should first be vetted by a human to ensure its integrity. NetBox can then be used to populate monitoring and provisioning systems with a high degree of confidence.

## Keep it Simple

When given a choice between a relatively simple [80% solution](https://en.wikipedia.org/wiki/Pareto_principle) and a much more complex complete solution, the former will typically be favored. This ensures a lean codebase with a low learning curve.

# Application Stack

NetBox is built on the [Django](https://djangoproject.com/) Python framework and utilizes a [PostgreSQL](https://www.postgresql.org/) database. It runs as a WSGI service behind your choice of HTTP server.

| Function     | Component         |
|--------------|-------------------|
| HTTP Service | nginx or Apache   |
| WSGI Service | gunicorn or uWSGI |
| Application  | Django/Python     |
| Database     | PostgreSQL        |

# Getting Started

See the [getting started](getting-started.md) guide for help with getting NetBox up and running quickly.
