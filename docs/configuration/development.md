# Development Parameters

## DEBUG

Default: `False`

This setting enables debugging and displays a debugging toolbar in the user interface. Debugging should be enabled only during development or troubleshooting.

Note that the debugging toolbar will be displayed only for requests originating from [internal IP addresses](./system.md#internal_ips), if defined. If no internal IPs are defined, the toolbar will be displayed for all requests.

!!! warning
    Never enable debugging on a production system, as it can expose sensitive data to unauthenticated users and impose a
    substantial performance penalty.

---

## DEVELOPER

Default: `False`

This parameter serves as a safeguard to prevent some potentially dangerous behavior, such as generating new database schema migrations. Additionally, enabling this setting disables the debug warning banner in the UI. Set this to `True` **only** if you are actively developing the NetBox code base.
