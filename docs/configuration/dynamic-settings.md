# Dynamic Configuration Settings

These configuration parameters are primarily controlled via NetBox's admin interface (under Admin > Extras > Configuration Revisions). These setting may also be overridden in `configuration.py`; this will prevent them from being modified via the UI.

---

## ALLOWED_URL_SCHEMES

Default: `('file', 'ftp', 'ftps', 'http', 'https', 'irc', 'mailto', 'sftp', 'ssh', 'tel', 'telnet', 'tftp', 'vnc', 'xmpp')`

A list of permitted URL schemes referenced when rendering links within NetBox. Note that only the schemes specified in this list will be accepted: If adding your own, be sure to replicate all of the default values as well (excluding those schemes which are not desirable).

---

## BANNER_TOP

## BANNER_BOTTOM

Setting these variables will display custom content in a banner at the top and/or bottom of the page, respectively. HTML is allowed. To replicate the content of the top banner in the bottom banner, set:

```python
BANNER_TOP = 'Your banner text'
BANNER_BOTTOM = BANNER_TOP
```

---

## BANNER_LOGIN

This defines custom content to be displayed on the login page above the login form. HTML is allowed.

---

## ENFORCE_GLOBAL_UNIQUE

Default: False

By default, NetBox will permit users to create duplicate prefixes and IP addresses in the global table (that is, those which are not assigned to any VRF). This behavior can be disabled by setting `ENFORCE_GLOBAL_UNIQUE` to True.

---

## MAINTENANCE_MODE

Default: False

Setting this to True will display a "maintenance mode" banner at the top of every page. Additionally, NetBox will no longer update a user's "last active" time upon login. This is to allow new logins when the database is in a read-only state. Recording of login times will resume when maintenance mode is disabled.

---

## MAPS_URL

Default: `https://maps.google.com/?q=` (Google Maps)

This specifies the URL to use when presenting a map of a physical location by street address or GPS coordinates. The URL must accept either a free-form street address or a comma-separated pair of numeric coordinates appended to it.

---

## MAX_PAGE_SIZE

Default: 1000

A web user or API consumer can request an arbitrary number of objects by appending the "limit" parameter to the URL (e.g. `?limit=1000`). This parameter defines the maximum acceptable limit. Setting this to `0` or `None` will allow a client to retrieve _all_ matching objects at once with no limit by specifying `?limit=0`.

---

## NAPALM_USERNAME

## NAPALM_PASSWORD

NetBox will use these credentials when authenticating to remote devices via the supported [NAPALM integration](../additional-features/napalm.md), if installed. Both parameters are optional.

!!! note
    If SSH public key authentication has been set up on the remote device(s) for the system account under which NetBox runs, these parameters are not needed.

---

## NAPALM_ARGS

A dictionary of optional arguments to pass to NAPALM when instantiating a network driver. See the NAPALM documentation for a [complete list of optional arguments](https://napalm.readthedocs.io/en/latest/support/#optional-arguments). An example:

```python
NAPALM_ARGS = {
    'api_key': '472071a93b60a1bd1fafb401d9f8ef41',
    'port': 2222,
}
```

Some platforms (e.g. Cisco IOS) require an argument named `secret` to be passed in addition to the normal password. If desired, you can use the configured `NAPALM_PASSWORD` as the value for this argument:

```python
NAPALM_USERNAME = 'username'
NAPALM_PASSWORD = 'MySecretPassword'
NAPALM_ARGS = {
    'secret': NAPALM_PASSWORD,
    # Include any additional args here
}
```

---

## NAPALM_TIMEOUT

Default: 30 seconds

The amount of time (in seconds) to wait for NAPALM to connect to a device.

---

## PAGINATE_COUNT

Default: 50

The default maximum number of objects to display per page within each list of objects.

---

## PREFER_IPV4

Default: False

When determining the primary IP address for a device, IPv6 is preferred over IPv4 by default. Set this to True to prefer IPv4 instead.

---

## RACK_ELEVATION_DEFAULT_UNIT_HEIGHT

Default: 22

Default height (in pixels) of a unit within a rack elevation. For best results, this should be approximately one tenth of `RACK_ELEVATION_DEFAULT_UNIT_WIDTH`.

---

## RACK_ELEVATION_DEFAULT_UNIT_WIDTH

Default: 220

Default width (in pixels) of a unit within a rack elevation.
