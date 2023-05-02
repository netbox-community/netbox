# Security & Authentication Parameters

## ALLOW_TOKEN_RETRIEVAL

Default: True

If disabled, the values of API tokens will not be displayed after each token's initial creation. A user **must** record the value of a token immediately upon its creation, or it will be lost. Note that this affects _all_ users, regardless of assigned permissions.

---

## ALLOWED_URL_SCHEMES

!!! tip "Dynamic Configuration Parameter"

Default: `('file', 'ftp', 'ftps', 'http', 'https', 'irc', 'mailto', 'sftp', 'ssh', 'tel', 'telnet', 'tftp', 'vnc', 'xmpp')`

A list of permitted URL schemes referenced when rendering links within NetBox. Note that only the schemes specified in this list will be accepted: If adding your own, be sure to replicate all the default values as well (excluding those schemes which are not desirable).

---

## AUTH_PASSWORD_VALIDATORS

This parameter acts as a pass-through for configuring Django's built-in password validators for local user accounts. If configured, these will be applied whenever a user's password is updated to ensure that it meets minimum criteria such as length or complexity. An example is provided below. For more detail on the available options, please see [the Django documentation](https://docs.djangoproject.com/en/stable/topics/auth/passwords/#password-validation).

```python
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 10,
        }
    },
]
```

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

## CSRF_COOKIE_NAME

Default: `csrftoken`

The name of the cookie to use for the cross-site request forgery (CSRF) authentication token. See the [Django documentation](https://docs.djangoproject.com/en/stable/ref/settings/#csrf-cookie-name) for more detail.

---

## CSRF_COOKIE_SECURE

Default: False

If true, the cookie employed for cross-site request forgery (CSRF) protection will be marked as secure, meaning that it can only be sent across an HTTPS connection.

---

## CSRF_TRUSTED_ORIGINS

Default: `[]`

Defines a list of trusted origins for unsafe (e.g. `POST`) requests. This is a pass-through to Django's [`CSRF_TRUSTED_ORIGINS`](https://docs.djangoproject.com/en/4.0/ref/settings/#std:setting-CSRF_TRUSTED_ORIGINS) setting. Note that each host listed must specify a scheme (e.g. `http://` or `https://).

```python
CSRF_TRUSTED_ORIGINS = (
    'http://netbox.local',
    'https://netbox.local',
)
```

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

## LOGIN_PERSISTENCE

Default: False

If true, the lifetime of a user's authentication session will be automatically reset upon each valid request. For example, if [`LOGIN_TIMEOUT`](#login_timeout) is configured to 14 days (the default), and a user whose session is due to expire in five days makes a NetBox request (with a valid session cookie), the session's lifetime will be reset to 14 days.

Note that enabling this setting causes NetBox to update a user's session in the database (or file, as configured per [`SESSION_FILE_PATH`](#session_file_path)) with each request, which may introduce significant overhead in very active environments. It also permits an active user to remain authenticated to NetBox indefinitely.

---

## LOGIN_REQUIRED

Default: False

Setting this to True will permit only authenticated users to access any part of NetBox. By default, anonymous users are permitted to access most data in NetBox but not make any changes.

---

## LOGIN_TIMEOUT

Default: 1209600 seconds (14 days)

The lifetime (in seconds) of the authentication cookie issued to a NetBox user upon login.

---

## LOGOUT_REDIRECT_URL

Default: `'home'`

The view name or URL to which a user is redirected after logging out.

---

## SECURE_SSL_REDIRECT

Default: False

If true, all non-HTTPS requests will be automatically redirected to use HTTPS.

!!! warning
    Ensure that your frontend HTTP daemon has been configured to forward the HTTP scheme correctly before enabling this option. An incorrectly configured frontend may result in a looping redirect.

---

## SESSION_COOKIE_NAME

Default: `sessionid`

The name used for the session cookie. See the [Django documentation](https://docs.djangoproject.com/en/stable/ref/settings/#session-cookie-name) for more detail.

---

## SESSION_COOKIE_SECURE

Default: False

If true, the cookie employed for session authentication will be marked as secure, meaning that it can only be sent across an HTTPS connection.

---

## SESSION_FILE_PATH

Default: None

HTTP session data is used to track authenticated users when they access NetBox. By default, NetBox stores session data in its PostgreSQL database. However, this inhibits authentication to a standby instance of NetBox without write access to the database. Alternatively, a local file path may be specified here and NetBox will store session data as files instead of using the database. Note that the NetBox system user must have read and write permissions to this path.
