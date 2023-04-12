# Development Parameters

## DEBUG

Default: False

This setting enables debugging. Debugging should be enabled only during development or troubleshooting. Note that only
clients which access NetBox from a recognized [internal IP address](#internal_ips) will see debugging tools in the user
interface.

!!! warning
    Never enable debugging on a production system, as it can expose sensitive data to unauthenticated users and impose a
    substantial performance penalty.

---

## DEVELOPER

Default: False

This parameter serves as a safeguard to prevent some potentially dangerous behavior, such as generating new database schema migrations. Additionally, enabling this setting disables the debug warning banner in the UI. Set this to `True` **only** if you are actively developing the NetBox code base.
