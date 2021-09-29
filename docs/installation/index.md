# Installation

The installation instructions provided here have been tested to work on Ubuntu 20.04 and CentOS 8.2. The particular commands needed to install dependencies on other distributions may vary significantly. Unfortunately, this is outside the control of the NetBox maintainers. Please consult your distribution's documentation for assistance with any errors.

The following sections detail how to set up a new instance of NetBox:

1. [PostgreSQL database](1-postgresql.md)
1. [Redis](2-redis.md)
3. [NetBox components](3-netbox.md)
4. [Gunicorn](4-gunicorn.md)
5. [HTTP server](5-http-server.md)
6. [LDAP authentication](6-ldap.md) (optional)

The video below demonstrates the installation of NetBox v2.10.3 on Ubuntu 20.04 for your reference.

<iframe width="560" height="315" src="https://www.youtube.com/embed/7Fpd2-q9_28" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## Requirements

| Dependency | Minimum Version |
|------------|-----------------|
| Python     | 3.7             |
| PostgreSQL | 10              |
| Redis      | 4.0             |

Below is a simplified overview of the NetBox application stack for reference:

![NetBox UI as seen by a non-authenticated user](../media/installation/netbox_application_stack.png)

## Upgrading

If you are upgrading from an existing installation, please consult the [upgrading guide](upgrading.md).
