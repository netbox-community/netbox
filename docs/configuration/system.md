# System Parameters

## BASE_PATH

Default: `None`

The base URL path to use when accessing NetBox. Do not include the scheme or domain name. For example, if installed at https://example.com/netbox/, set:

```python
BASE_PATH = 'netbox/'
```

---

## DATABASE_ROUTERS

Default: `[]` (empty list)

An iterable of [database routers](https://docs.djangoproject.com/en/stable/topics/db/multi-db/) to use for automatically selecting the appropriate database(s) for a query. This is useful only when [multiple databases](./required-parameters.md#databases) have been configured.

---

## DEFAULT_LANGUAGE

Default: `en-us` (US English)

Defines the default preferred language/locale for requests that do not specify one. (This parameter maps to Django's [`LANGUAGE_CODE`](https://docs.djangoproject.com/en/stable/ref/settings/#language-code) internal setting.)

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
* `PASSWORD` - Password with which to authenticate
* `USE_SSL` - Use SSL when connecting to the server (default: `False`)
* `USE_TLS` - Use TLS when connecting to the server (default: `False`)
* `SSL_CERTFILE` - Path to the PEM-formatted SSL certificate file (optional)
* `SSL_KEYFILE` - Path to the PEM-formatted SSL private key file (optional)
* `TIMEOUT` - Amount of time to wait for a connection, in seconds (default: `10`)
* `FROM_EMAIL` - Sender address for emails sent by NetBox

!!! note
    The `USE_SSL` and `USE_TLS` parameters are mutually exclusive.

Email is sent from NetBox only for critical events or if configured for [logging](#logging). If you would like to test the email server configuration, Django provides a convenient [send_mail()](https://docs.djangoproject.com/en/stable/topics/email/#send-mail) function accessible within the NetBox shell:

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

## HOSTNAME

!!! info "This parameter was introduced in NetBox v4.4."

Default: System hostname

The hostname displayed in the user interface identifying the system on which NetBox is running. If not defined, this defaults to the system hostname as reported by Python's `platform.node()`.

---

## HTTP_PROXIES

Default: `None`

A dictionary of HTTP proxies to use for outbound requests originating from NetBox (e.g. when sending webhook requests). Proxies should be specified by schema (HTTP and HTTPS) as per the [Python requests library documentation](https://requests.readthedocs.io/en/latest/user/advanced/#proxies). For example:

```python
HTTP_PROXIES = {
    'http': 'http://10.10.1.10:3128',
    'https': 'http://10.10.1.10:1080',
}
```

If more flexibility is needed in determining which proxy to use for a given request, consider implementing one or more custom proxy routers via the [`PROXY_ROUTERS`](#proxy_routers) parameter.

---

## INTERNAL_IPS

Default: `('127.0.0.1', '::1')`

A list of IP addresses recognized as internal to the system, used to control the display of debugging output. For
example, the debugging toolbar will be viewable only when a client is accessing NetBox from one of the listed IP
addresses (and [`DEBUG`](./development.md#debug) is `True`).

---

## ISOLATED_DEPLOYMENT

Default: `False`

Set this configuration parameter to `True` for NetBox deployments which do not have Internet access. This will disable miscellaneous functionality which depends on access to the Internet.

!!! note
    If Internet access is available via a proxy, set [`HTTP_PROXIES`](#http_proxies) instead.

---

## JINJA2_FILTERS

Default: `{}`

A dictionary of custom Jinja2 filters with the key being the filter name and the value being a callable. For more information see the [Jinja2 documentation](https://jinja.palletsprojects.com/en/3.1.x/api/#custom-filters). For example:

```python
def uppercase(x):
    return str(x).upper()

JINJA2_FILTERS = {
    'uppercase': uppercase,
}
```

---

## LOGGING

By default, all messages of INFO severity or higher will be logged to the console. Additionally, if [`DEBUG`](./development.md#debug) is False and email access has been configured, ERROR and CRITICAL messages will be emailed to the users defined in [`ADMINS`](./miscellaneous.md#admins).

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
* `netbox.event_rules` - Event rules
* `netbox.jobs.*` - Background jobs
* `netbox.reports.*` - Report execution (`module.name`)
* `netbox.scripts.*` - Custom script execution (`module.name`)
* `netbox.views.*` - Views which handle business logic for the web UI

---

## MEDIA_ROOT

Default: `$INSTALL_ROOT/netbox/media/`

The file path to the location where media files (such as image attachments) are stored. By default, this is the `netbox/media/` directory within the base NetBox installation path.

---

## PROXY_ROUTERS

Default: `["utilities.proxy.DefaultProxyRouter"]`

A list of Python classes responsible for determining which proxy server(s) to use for outbound HTTP requests. Each item in the list can be the class itself or the dotted path to the class.

The `route()` method on each class must return a dictionary of candidate proxies arranged by protocol (e.g. `http` and/or `https`), or None if no viable proxy can be determined. The default class, `DefaultProxyRouter`, simply returns the content of [`HTTP_PROXIES`](#http_proxies).

---

## REPORTS_ROOT

Default: `$INSTALL_ROOT/netbox/reports/`

The file path to the location where [custom reports](../customization/reports.md) will be kept. By default, this is the `netbox/reports/` directory within the base NetBox installation path.

---

## SCRIPTS_ROOT

Default: `$INSTALL_ROOT/netbox/scripts/`

The file path to the location where [custom scripts](../customization/custom-scripts.md) will be kept. By default, this is the `netbox/scripts/` directory within the base NetBox installation path.

---

## SEARCH_BACKEND

Default: `'netbox.search.backends.CachedValueSearchBackend'`

The dotted path to the desired search backend class. `CachedValueSearchBackend` is currently the only search backend provided in NetBox, however this setting can be used to enable a custom backend. 

---

## STORAGES

The backend storage engine for handling uploaded files such as [image attachments](../models/extras/imageattachment.md) and [custom scripts](../customization/custom-scripts.md). NetBox integrates with the [`django-storages`](https://django-storages.readthedocs.io/en/stable/) and [`django-storage-swift`](https://github.com/dennisv/django-storage-swift) libraries, which provide backends for several popular file storage services. If not configured, local filesystem storage will be used.

By default, the following configuration is used:

```python
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
    "scripts": {
        "BACKEND": "extras.storage.ScriptFileSystemStorage",
    },
}
```

Within the `STORAGES` dictionary, `"default"` is used for image uploads, "staticfiles" is for static files and `"scripts"` is used for custom scripts.

If using a remote storage like S3, define the config as `STORAGES[key]["OPTIONS"]` for each storage item as needed. For example:

```python
STORAGES = { 
    "scripts": { 
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage", 
        "OPTIONS": { 
            'access_key': 'access key', 
            'secret_key': 'secret key',
        }
    }, 
}
```

The specific configuration settings for each storage backend can be found in the [django-storages documentation](https://django-storages.readthedocs.io/en/latest/index.html).

!!! note
    Any keys defined in the `STORAGES` configuration parameter replace those in the default configuration. It is only necessary to define keys within the `STORAGES` for the specific backend(s) you wish to configure.

### Environment Variables and Third-Party Libraries

NetBox uses an explicit Python configuration approach rather than automatic environment variable detection. While this provides clear configuration management and version control capabilities, it affects how some third-party libraries like `django-storages` function within NetBox's context.

Many Django libraries (including `django-storages`) expect to automatically detect environment variables like `AWS_STORAGE_BUCKET_NAME` or `AWS_S3_ACCESS_KEY_ID`. However, NetBox's configuration processing prevents this automatic detection from working as documented in some of these libraries.

When using third-party libraries that rely on environment variable detection, you may need to explicitly read environment variables in your NetBox `configuration.py`:

```python
import os

STORAGES = {
    'default': {
        'BACKEND': 'storages.backends.s3.S3Storage',
        'OPTIONS': {
            'bucket_name': os.environ.get('AWS_STORAGE_BUCKET_NAME'),
            'access_key': os.environ.get('AWS_S3_ACCESS_KEY_ID'),
            'secret_key': os.environ.get('AWS_S3_SECRET_ACCESS_KEY'),
            'endpoint_url': os.environ.get('AWS_S3_ENDPOINT_URL'),
            'location': 'media/',
        }
    },
    'staticfiles': {
        'BACKEND': 'storages.backends.s3.S3Storage',
        'OPTIONS': {
            'bucket_name': os.environ.get('AWS_STORAGE_BUCKET_NAME'),
            'access_key': os.environ.get('AWS_S3_ACCESS_KEY_ID'),
            'secret_key': os.environ.get('AWS_S3_SECRET_ACCESS_KEY'),
            'endpoint_url': os.environ.get('AWS_S3_ENDPOINT_URL'),
            'location': 'static/',
        }
    },
}
```

This approach works because the environment variables are resolved during NetBox's configuration processing, before the third-party library attempts its own environment variable detection.

!!! warning "Configuration Behavior"
    Simply setting environment variables like `AWS_STORAGE_BUCKET_NAME` without explicitly reading them in your configuration will not work. The variables must be read using `os.environ.get()` within your `configuration.py` file.

---

## TIME_ZONE

Default: `"UTC"`

The time zone NetBox will use when dealing with dates and times. It is recommended to use UTC time unless you have a specific need to use a local time zone. Please see the [list of available time zones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).

---

## TRANSLATION_ENABLED

Default: `True`

Enables language translation for the user interface. (This parameter maps to Django's [USE_I18N](https://docs.djangoproject.com/en/stable/ref/settings/#std-setting-USE_I18N) setting.)
