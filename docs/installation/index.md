# Installation

!!! info "NetBox Cloud"
    The instructions below are for installing NetBox as a standalone, self-hosted application. For a Cloud-delivered solution, check out [NetBox Cloud](https://netboxlabs.com/netbox-cloud/) by NetBox Labs.

The installation instructions provided here have been tested to work on Ubuntu 22.04 and CentOS 8.3. The particular commands needed to install dependencies on other distributions may vary significantly. Unfortunately, this is outside the control of the NetBox maintainers. Please consult your distribution's documentation for assistance with any errors.

<iframe width="560" height="315" src="https://www.youtube.com/embed/_y5JRiW_PLM" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

The following sections detail how to set up a new instance of NetBox:

1. [PostgreSQL database](1-postgresql.md)
1. [Redis](2-redis.md)
3. [NetBox components](3-netbox.md)
4. [Gunicorn](4a-gunicorn.md) or [uWSGI](4b-uwsgi.md)
5. [HTTP server](5-http-server.md)
6. [LDAP authentication](6-ldap.md) (optional)

## Requirements

| Dependency | Supported Versions |
|------------|--------------------|
| Python     | 3.10, 3.11, 3.12   |
| PostgreSQL | 13+                |
| Redis      | 4.0+               |

Below is a simplified overview of the NetBox application stack for reference:

![NetBox UI as seen by a non-authenticated user](../media/installation/netbox_application_stack.png)

## Upgrading

If you are upgrading from an existing installation, please consult the [upgrading guide](upgrading.md).
