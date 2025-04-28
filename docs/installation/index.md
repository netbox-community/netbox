# Installation

<div class="grid cards" markdown>

-   :material-clock-fast:{ .lg .middle } __Eager to Get Started?__

    ---

    Check out the [NetBox Cloud Free Plan](https://netboxlabs.com/free-netbox-cloud/)! Skip the installation process and grab your own NetBox Cloud instance, preconfigured and ready to go in minutes. Completely free!

    [:octicons-arrow-right-24: Sign Up](https://signup.netboxlabs.com/)

</div>

The installation instructions provided here have been tested to work on Ubuntu 22.04. The particular commands needed to install dependencies on other distributions may vary significantly. Unfortunately, this is outside the control of the NetBox maintainers. Please consult your distribution's documentation for assistance with any errors.

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
| PostgreSQL | 14+                |
| Redis      | 4.0+               |

Below is a simplified overview of the NetBox application stack for reference:

![NetBox UI as seen by a non-authenticated user](../media/installation/netbox_application_stack.png)

## Upgrading

If you are upgrading from an existing installation, please consult the [upgrading guide](upgrading.md).
