# Optional Configuration Settings

## ADMINS

NetBox will email details about critical errors to the administrators listed here. This should be a list of (name, email) tuples. For example:

```python
ADMINS = [
    ['Hank Hill', 'hhill@example.com'],
    ['Dale Gribble', 'dgribble@example.com'],
]
```

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

## BASE_PATH

Default: None

The base URL path to use when accessing NetBox. Do not include the scheme or domain name. For example, if installed at http://example.com/netbox/, set:

```python
BASE_PATH = 'netbox/'
```

---

## CACHE_TIMEOUT

Default: 900

The number of seconds to cache entries will be retained before expiring.

---

## CHANGELOG_RETENTION

Default: 90

The number of days to retain logged changes (object creations, updates, and deletions). Set this to `0` to retain
changes in the database indefinitely.

!!! warning
    If enabling indefinite changelog retention, it is recommended to periodically delete old entries. Otherwise, the database may eventually exceed capacity.

---

## CORS_ORIGIN_ALLOW_ALL

Default: False

If True, cross-origin resource sharing (CORS) requests will be accepted from all origins. If False, a whitelist will be used (see below).

---

## CORS_ORIGIN_WHITELIST

## CORS_ORIGIN_REGEX_WHITELIST

These settings specify a list of origins that are authorized to make cross-site API requests. Use
`CORS_ORIGIN_WHITELIST` to define a list of exact hostnames, or `CORS_ORIGIN_REGEX_WHITELIST` to define a set of regular 
expressions. (These settings have no effect if `CORS_ORIGIN_ALLOW_ALL` is True.) For example:

```python
CORS_ORIGIN_WHITELIST = [
    'https://example.com',
]
```

---

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

This parameter serves as a safeguard to prevent some potentially dangerous behavior, such as generating new database schema migrations. Set this to `True` **only** if you are actively developing the NetBox code base.

---

## DOCS_ROOT

Default: `$INSTALL_ROOT/docs/`

The filesystem path to NetBox's documentation. This is used when presenting context-sensitive documentation in the web UI. By default, this will be the `docs/` directory within the root NetBox installation path. (Set this to `None` to disable the embedded documentation.)

---

## EMAIL

In order to send email, NetBox needs an email server configured. The following items can be defined within the `EMAIL` configuration parameter:

* `SERVER` - Hostname or IP address of the email server (use `localhost` if running locally)
* `PORT` - TCP port to use for the connection (default: `25`)
* `USERNAME` - Username with which to authenticate
* `PASSSWORD` - Password with which to authenticate
* `USE_SSL` - Use SSL when connecting to the server (default: `False`)
* `USE_TLS` - Use TLS when connecting to the server (default: `False`)
* `SSL_CERTFILE` - Path to the PEM-formatted SSL certificate file (optional)
* `SSL_KEYFILE` - Path to the PEM-formatted SSL private key file (optional)
* `TIMEOUT` - Amount of time to wait for a connection, in seconds (default: `10`)
* `FROM_EMAIL` - Sender address for emails sent by NetBox

!!! note
    The `USE_SSL` and `USE_TLS` parameters are mutually exclusive.

Email is sent from NetBox only for critical events or if configured for [logging](#logging). If you would like to test the email server configuration, Django provides a convenient [send_mail()](https://docs.djangoproject.com/en/stable/topics/email/#send-mail) fuction accessible within the NetBox shell:

```no-highlight
# python ./manage.py nbshell
>>> from django.core.mail import send_mail
>>> send_mail(
  'Test Email Subject',
  'Test Email Body',
  'noreply-netbox@example.com',
  ['users@example.com'],
  fail_silently=False
)
```

---

## ENFORCE_GLOBAL_UNIQUE

Default: False

By default, NetBox will permit users to create duplicate prefixes and IP addresses in the global table (that is, those which are not assigned to any VRF). This behavior can be disabled by setting `ENFORCE_GLOBAL_UNIQUE` to True.

---

## EXEMPT_VIEW_PERMISSIONS

Default: Empty list

A list of NetBox models to exempt from the enforcement of view permissions. Models listed here will be viewable by all users, both authenticated and anonymous.

List models in the form `<app>.<model>`. For example:

```python
EXEMPT_VIEW_PERMISSIONS = [
    'dcim.site',
    'dcim.region',
    'ipam.prefix',
]
```

To exempt _all_ models from view permission enforcement, set the following. (Note that `EXEMPT_VIEW_PERMISSIONS` must be an iterable.)

```python
EXEMPT_VIEW_PERMISSIONS = ['*']
```

!!! note
    Using a wildcard will not affect certain potentially sensitive models, such as user permissions. If there is a need to exempt these models, they must be specified individually.

---

## HTTP_PROXIES

Default: None

A dictionary of HTTP proxies to use for outbound requests originating from NetBox (e.g. when sending webhook requests). Proxies should be specified by schema (HTTP and HTTPS) as per the [Python requests library documentation](https://2.python-requests.org/en/master/user/advanced/). For example:

```python
HTTP_PROXIES = {
    'http': 'http://10.10.1.10:3128',
    'https': 'http://10.10.1.10:1080',
}
```

---

## INTERNAL_IPS

Default: `('127.0.0.1', '::1')`

A list of IP addresses recognized as internal to the system, used to control the display of debugging output. For
example, the debugging toolbar will be viewable only when a client is accessing NetBox from one of the listed IP
addresses (and [`DEBUG`](#debug) is true).

---

## LOGGING

By default, all messages of INFO severity or higher will be logged to the console. Additionally, if [`DEBUG`](#debug) is False and email access has been configured, ERROR and CRITICAL messages will be emailed to the users defined in [`ADMINS`](#admins).

The Django framework on which NetBox runs allows for the customization of logging format and destination. Please consult the [Django logging documentation](https://docs.djangoproject.com/en/stable/topics/logging/) for more information on configuring this setting. Below is an example which will write all INFO and higher messages to a local file:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/netbox.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

### Available Loggers

* `netbox.<app>.<model>` - Generic form for model-specific log messages
* `netbox.auth.*` - Authentication events
* `netbox.api.views.*` - Views which handle business logic for the REST API
* `netbox.reports.*` - Report execution (`module.name`)
* `netbox.scripts.*` - Custom script execution (`module.name`)
* `netbox.views.*` - Views which handle business logic for the web UI

---

## LOGIN_REQUIRED

Default: False

Setting this to True will permit only authenticated users to access any part of NetBox. By default, anonymous users are permitted to access most data in NetBox (excluding secrets) but not make any changes.

---

## LOGIN_TIMEOUT

Default: 1209600 seconds (14 days)

The lifetime (in seconds) of the authentication cookie issued to a NetBox user upon login.

---

## MAINTENANCE_MODE

Default: False

Setting this to True will display a "maintenance mode" banner at the top of every page. Additionally, NetBox will no longer update a user's "last active" time upon login. This is to allow new logins when the database is in a read-only state. Recording of login times will resume when maintenance mode is disabled.

---

## MAX_PAGE_SIZE

Default: 1000

A web user or API consumer can request an arbitrary number of objects by appending the "limit" parameter to the URL (e.g. `?limit=1000`). This parameter defines the maximum acceptable limit. Setting this to `0` or `None` will allow a client to retrieve _all_ matching objects at once with no limit by specifying `?limit=0`.

---

## MEDIA_ROOT

Default: $INSTALL_ROOT/netbox/media/

The file path to the location where media files (such as image attachments) are stored. By default, this is the `netbox/media/` directory within the base NetBox installation path.

---

## METRICS_ENABLED

Default: False

Toggle the availability Prometheus-compatible metrics at `/metrics`. See the [Prometheus Metrics](../../additional-features/prometheus-metrics/) documentation for more details.

---

## NAPALM_USERNAME

## NAPALM_PASSWORD

NetBox will use these credentials when authenticating to remote devices via the [NAPALM library](https://napalm-automation.net/), if installed. Both parameters are optional.

!!! note
    If SSH public key authentication has been set up on the remote device(s) for the system account under which NetBox runs, these parameters are not needed.

---

## NAPALM_ARGS

A dictionary of optional arguments to pass to NAPALM when instantiating a network driver. See the NAPALM documentation for a [complete list of optional arguments](http://napalm.readthedocs.io/en/latest/support/#optional-arguments). An example:

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

## PLUGINS

Default: Empty

A list of installed [NetBox plugins](../../plugins/) to enable. Plugins will not take effect unless they are listed here.

!!! warning
    Plugins extend NetBox by allowing external code to run with the same access and privileges as NetBox itself. Only install plugins from trusted sources. The NetBox maintainers make absolutely no guarantees about the integrity or security of your installation with plugins enabled.

---

## PLUGINS_CONFIG

Default: Empty

This parameter holds configuration settings for individual NetBox plugins. It is defined as a dictionary, with each key using the name of an installed plugin. The specific parameters supported are unique to each plugin: Reference the plugin's documentation to determine the supported parameters. An example configuration is shown below:

```python
PLUGINS_CONFIG = {
    'plugin1': {
        'foo': 123,
        'bar': True
    },
    'plugin2': {
        'foo': 456,
    },
}
```

Note that a plugin must be listed in `PLUGINS` for its configuration to take effect.

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

---

## REMOTE_AUTH_AUTO_CREATE_USER

Default: `False`

If true, NetBox will automatically create local accounts for users authenticated via a remote service. (Requires `REMOTE_AUTH_ENABLED`.)

---

## REMOTE_AUTH_BACKEND

Default: `'netbox.authentication.RemoteUserBackend'`

This is the Python path to the custom [Django authentication backend](https://docs.djangoproject.com/en/stable/topics/auth/customizing/) to use for external user authentication. NetBox provides two built-in backends (listed below), though custom authentication backends may also be provided by other packages or plugins.

* `netbox.authentication.RemoteUserBackend`
* `netbox.authentication.LDAPBackend`

---

## REMOTE_AUTH_DEFAULT_GROUPS

Default: `[]` (Empty list)

The list of groups to assign a new user account when created using remote authentication. (Requires `REMOTE_AUTH_ENABLED`.)

---

## REMOTE_AUTH_DEFAULT_PERMISSIONS

Default: `{}` (Empty dictionary)

A mapping of permissions to assign a new user account when created using remote authentication. Each key in the dictionary should be set to a dictionary of the attributes to be applied to the permission, or `None` to allow all objects. (Requires `REMOTE_AUTH_ENABLED`.)

---

## REMOTE_AUTH_ENABLED

Default: `False`

NetBox can be configured to support remote user authentication by inferring user authentication from an HTTP header set by the HTTP reverse proxy (e.g. nginx or Apache). Set this to `True` to enable this functionality. (Local authentication will still take effect as a fallback.)

---

## REMOTE_AUTH_HEADER

Default: `'HTTP_REMOTE_USER'`

When remote user authentication is in use, this is the name of the HTTP header which informs NetBox of the currently authenticated user. (Requires `REMOTE_AUTH_ENABLED`.)

---

## RELEASE_CHECK_TIMEOUT

Default: 86,400 (24 hours)

The number of seconds to retain the latest version that is fetched from the GitHub API before automatically invalidating it and fetching it from the API again. This must be set to at least one hour (3600 seconds).

---

## RELEASE_CHECK_URL

Default: None (disabled)

This parameter defines the URL of the repository that will be checked periodically for new NetBox releases. When a new release is detected, a message will be displayed to administrative users on the home page. This can be set to the official repository (`'https://api.github.com/repos/netbox-community/netbox/releases'`) or a custom fork. Set this to `None` to disable automatic update checks.

!!! note
    The URL provided **must** be compatible with the [GitHub REST API](https://docs.github.com/en/rest).

---

## REPORTS_ROOT

Default: `$INSTALL_ROOT/netbox/reports/`

The file path to the location where custom reports will be kept. By default, this is the `netbox/reports/` directory within the base NetBox installation path.

---

## RQ_DEFAULT_TIMEOUT

Default: `300`

The maximum execution time of a background task (such as running a custom script), in seconds.

---

## SCRIPTS_ROOT

Default: `$INSTALL_ROOT/netbox/scripts/`

The file path to the location where custom scripts will be kept. By default, this is the `netbox/scripts/` directory within the base NetBox installation path.

---

## SESSION_FILE_PATH

Default: None

HTTP session data is used to track authenticated users when they access NetBox. By default, NetBox stores session data in its PostgreSQL database. However, this inhibits authentication to a standby instance of NetBox without write access to the database. Alternatively, a local file path may be specified here and NetBox will store session data as files instead of using the database. Note that the NetBox system user must have read and write permissions to this path.

---

## STORAGE_BACKEND

Default: None (local storage)

The backend storage engine for handling uploaded files (e.g. image attachments). NetBox supports integration with the [`django-storages`](https://django-storages.readthedocs.io/en/stable/) package, which provides backends for several popular file storage services. If not configured, local filesystem storage will be used.

The configuration parameters for the specified storage backend are defined under the `STORAGE_CONFIG` setting.

---

## STORAGE_CONFIG

Default: Empty

A dictionary of configuration parameters for the storage backend configured as `STORAGE_BACKEND`. The specific parameters to be used here are specific to each backend; see the [`django-storages` documentation](https://django-storages.readthedocs.io/en/stable/) for more detail.

If `STORAGE_BACKEND` is not defined, this setting will be ignored.

---

## TIME_ZONE

Default: UTC

The time zone NetBox will use when dealing with dates and times. It is recommended to use UTC time unless you have a specific need to use a local time zone. Please see the [list of available time zones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).

---

## Date and Time Formatting

You may define custom formatting for date and times. For detailed instructions on writing format strings, please see [the Django documentation](https://docs.djangoproject.com/en/stable/ref/templates/builtins/#date). Default formats are listed below.

```python
DATE_FORMAT = 'N j, Y'               # June 26, 2016
SHORT_DATE_FORMAT = 'Y-m-d'          # 2016-06-26
TIME_FORMAT = 'g:i a'                # 1:23 p.m.
SHORT_TIME_FORMAT = 'H:i:s'          # 13:23:00
DATETIME_FORMAT = 'N j, Y g:i a'     # June 26, 2016 1:23 p.m.
SHORT_DATETIME_FORMAT = 'Y-m-d H:i'  # 2016-06-26 13:23
```
