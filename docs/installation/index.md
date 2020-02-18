# Installation

The following sections detail how to set up a new instance of NetBox:

1. [PostgreSQL database](1-postgresql.md)
2. [NetBox components](2-netbox.md)
3. [HTTP daemon](3-http-daemon.md)
4. [LDAP authentication](4-ldap.md) (optional)

# Upgrading

If you are upgrading from an existing installation, please consult the [upgrading guide](upgrading.md).

NetBox v2.5 and later requires Python 3.5 or higher. Please see the instructions for [migrating to Python 3](migrating-to-python3.md) if you are still using Python 2.

Netbox v2.5.9 and later moved to using systemd instead of supervisord.  Please see the instructions for [migrating to systemd](migrating-to-systemd.md) if you are still using supervisord.
