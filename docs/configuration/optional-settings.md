# Optional Configuration Settings

## ADMINS

NetBox will email details about critical errors to the administrators listed here. This should be a list of (name, email) tuples. For example:

```
ADMINS = [
    ['Hank Hill', 'hhill@example.com'],
    ['Dale Gribble', 'dgribble@example.com'],
]
```

---

## BANNER_TOP

## BANNER_BOTTOM

Setting these variables will display content in a banner at the top and/or bottom of the page, respectively. HTML is allowed. To replicate the content of the top banner in the bottom banner, set:

```
BANNER_TOP = 'Your banner text'
BANNER_BOTTOM = BANNER_TOP
```

---

## BANNER_LOGIN

The value of this variable will be displayed on the login page above the login form. HTML is allowed.

---

## BASE_PATH

Default: None

The base URL path to use when accessing NetBox. Do not include the scheme or domain name. For example, if installed at http://example.com/netbox/, set:

```
BASE_PATH = 'netbox/'
```

---

## CACHE_TIMEOUT

Default: 900

The number of seconds to retain cache entries before automatically invalidating them.

---

## CHANGELOG_RETENTION

Default: 90

The number of days to retain logged changes (object creations, updates, and deletions). Set this to `0` to retain changes in the database indefinitely. (Warning: This will greatly increase database size over time.)

---

## CORS_ORIGIN_ALLOW_ALL

Default: False

If True, cross-origin resource sharing (CORS) requests will be accepted from all origins. If False, a whitelist will be used (see below).

---

## CORS_ORIGIN_WHITELIST

## CORS_ORIGIN_REGEX_WHITELIST

These settings specify a list of origins that are authorized to make cross-site API requests. Use `CORS_ORIGIN_WHITELIST` to define a list of exact hostnames, or `CORS_ORIGIN_REGEX_WHITELIST` to define a set of regular expressions. (These settings have no effect if `CORS_ORIGIN_ALLOW_ALL` is True.) For example:

```
CORS_ORIGIN_WHITELIST = [
    'https://example.com',
]
```

---

## DEBUG

Default: False

This setting enables debugging. This should be done only during development or troubleshooting. Never enable debugging on a production system, as it can expose sensitive data to unauthenticated users.

---

## DEVELOPER

Default: False

This parameter serves as a safeguard to prevent some potentially dangerous behavior, such as generating new database schema migrations. Set this to `True` **only** if you are actively developing the NetBox code base.

---

## EMAIL

In order to send email, NetBox needs an email server configured. The following items can be defined within the `EMAIL` setting:

* SERVER - Host name or IP address of the email server (use `localhost` if running locally)
* PORT - TCP port to use for the connection (default: 25)
* USERNAME - Username with which to authenticate
* PASSSWORD - Password with which to authenticate
* TIMEOUT - Amount of time to wait for a connection (seconds)
* FROM_EMAIL - Sender address for emails sent by NetBox

Email is sent from NetBox only for critical events. If you would like to test the email server configuration please use the django function [send_mail()](https://docs.djangoproject.com/en/stable/topics/email/#send-mail):

```
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

## EXEMPT_VIEW_PERMISSIONS

Default: Empty list

A list of models to exempt from the enforcement of view permissions. Models listed here will be viewable by all users and by anonymous users.

List models in the form `<app>.<model>`. For example:

```
EXEMPT_VIEW_PERMISSIONS = [
    'dcim.site',
    'dcim.region',
    'ipam.prefix',
]
```

To exempt _all_ models from view permission enforcement, set the following. (Note that `EXEMPT_VIEW_PERMISSIONS` must be an iterable.)

```
EXEMPT_VIEW_PERMISSIONS = ['*']
```

---

## ENFORCE_GLOBAL_UNIQUE

Default: False

Enforcement of unique IP space can be toggled on a per-VRF basis. To enforce unique IP space within the global table (all prefixes and IP addresses not assigned to a VRF), set `ENFORCE_GLOBAL_UNIQUE` to True.

---

## GITHUB_REPOSITORY_API

Default: 'https://api.github.com/repos/netbox-community/netbox'

The releases of this repository are checked to detect new releases, which are shown on the home page of the web interface. You can change this to your own fork of the NetBox repository, or set it to `None` to disable the check.

---

## GITHUB_CACHE_TIMEOUT

Default: 24 * 3600

The number of seconds to retain the latest version that is fetched from the GitHub API before automatically invalidating it and fetching it from the API again. This must be set to at least one hour (3600 seconds).

---

## LOGGING

By default, all messages of INFO severity or higher will be logged to the console. Additionally, if `DEBUG` is False and email access has been configured, ERROR and CRITICAL messages will be emailed to the users defined in `ADMINS`.

The Django framework on which NetBox runs allows for the customization of logging, e.g. to write logs to file. Please consult the [Django logging documentation](https://docs.djangoproject.com/en/stable/topics/logging/) for more information on configuring this setting. Below is an example which will write all INFO and higher messages to a file:

```
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

---

## LOGIN_REQUIRED

Default: False

Setting this to True will permit only authenticated users to access any part of NetBox. By default, anonymous users are permitted to access most data in NetBox (excluding secrets) but not make any changes.

---

## LOGIN_TIMEOUT

Default: 1209600 seconds (14 days)

The liftetime (in seconds) of the authentication cookie issued to a NetBox user upon login.

---

## MAINTENANCE_MODE

Default: False

Setting this to True will display a "maintenance mode" banner at the top of every page.

---

## MAX_PAGE_SIZE

Default: 1000

An API consumer can request an arbitrary number of objects by appending the "limit" parameter to the URL (e.g. `?limit=1000`). This setting defines the maximum limit. Setting it to `0` or `None` will allow an API consumer to request all objects by specifying `?limit=0`.

---

## MEDIA_ROOT

Default: $BASE_DIR/netbox/media/

The file path to the location where media files (such as image attachments) are stored. By default, this is the `netbox/media/` directory within the base NetBox installation path.

---

## METRICS_ENABLED

Default: False

Toggle exposing Prometheus metrics at `/metrics`. See the [Prometheus Metrics](../../additional-features/prometheus-metrics/) documentation for more details.

---

## NAPALM_USERNAME

## NAPALM_PASSWORD

NetBox will use these credentials when authenticating to remote devices via the [NAPALM library](https://napalm-automation.net/), if installed. Both parameters are optional.

Note: If SSH public key authentication has been set up for the system account under which NetBox runs, these parameters are not needed.

---

## NAPALM_ARGS

A dictionary of optional arguments to pass to NAPALM when instantiating a network driver. See the NAPALM documentation for a [complete list of optional arguments](http://napalm.readthedocs.io/en/latest/support/#optional-arguments). An example:

```
NAPALM_ARGS = {
    'api_key': '472071a93b60a1bd1fafb401d9f8ef41',
    'port': 2222,
}
```

Note: Some platforms (e.g. Cisco IOS) require an argument named `secret` to be passed in addition to the normal password. If desired, you can use the configured `NAPALM_PASSWORD` as the value for this argument:

```
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

Determine how many objects to display per page within each list of objects.

---

## PREFER_IPV4

Default: False

When determining the primary IP address for a device, IPv6 is preferred over IPv4 by default. Set this to True to prefer IPv4 instead.

---

## REPORTS_ROOT

Default: $BASE_DIR/netbox/reports/

The file path to the location where custom reports will be kept. By default, this is the `netbox/reports/` directory within the base NetBox installation path.

---

## SCRIPTS_ROOT

Default: $BASE_DIR/netbox/scripts/

The file path to the location where custom scripts will be kept. By default, this is the `netbox/scripts/` directory within the base NetBox installation path.

---

## SESSION_FILE_PATH

Default: None

Session data is used to track authenticated users when they access NetBox. By default, NetBox stores session data in the PostgreSQL database. However, this inhibits authentication to a standby instance of NetBox without write access to the database. Alternatively, a local file path may be specified here and NetBox will store session data as files instead of using the database. Note that the user as which NetBox runs must have read and write permissions to this path.

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

The time zone NetBox will use when dealing with dates and times. It is recommended to use UTC time unless you have a specific need to use a local time zone. [List of available time zones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).

---

## Date and Time Formatting

You may define custom formatting for date and times. For detailed instructions on writing format strings, please see [the Django documentation](https://docs.djangoproject.com/en/stable/ref/templates/builtins/#date).

Defaults:

```
DATE_FORMAT = 'N j, Y'               # June 26, 2016
SHORT_DATE_FORMAT = 'Y-m-d'          # 2016-06-27
TIME_FORMAT = 'g:i a'                # 1:23 p.m.
SHORT_TIME_FORMAT = 'H:i:s'          # 13:23:00
DATETIME_FORMAT = 'N j, Y g:i a'     # June 26, 2016 1:23 p.m.
SHORT_DATETIME_FORMAT = 'Y-m-d H:i'  # 2016-06-27 13:23
```
