# Remote Authentication Settings

The configuration parameters listed here control remote authentication for NetBox. Note that `REMOTE_AUTH_ENABLED` must be true in order for these settings to take effect.

---

## REMOTE_AUTH_AUTO_CREATE_USER

Default: `False`

If true, NetBox will automatically create local accounts for users authenticated via a remote service. (Requires `REMOTE_AUTH_ENABLED`.)

---

## REMOTE_AUTH_BACKEND

Default: `'netbox.authentication.RemoteUserBackend'`

This is the Python path to the custom [Django authentication backend](https://docs.djangoproject.com/en/stable/topics/auth/customizing/) to use for external user authentication. NetBox provides two built-in backends (listed below), though custom authentication backends may also be provided by other packages or plugins. Provide a string for a single backend, or an iterable for multiple backends, which will be attempted in the order given.

* `netbox.authentication.RemoteUserBackend`
* `netbox.authentication.LDAPBackend`

---

## REMOTE_AUTH_DEFAULT_GROUPS

Default: `[]` (Empty list)

The list of groups to assign a new user account when created using remote authentication. (Requires `REMOTE_AUTH_ENABLED`.)

---

## REMOTE_AUTH_DEFAULT_PERMISSIONS

Default: `{}` (Empty dictionary)

A mapping of permissions to assign a new user account when created using remote authentication. Each key in the dictionary should be set to a dictionary of the attributes to be applied to the permission, or `None` to allow all objects. (Requires `REMOTE_AUTH_ENABLED` as True and `REMOTE_AUTH_GROUP_SYNC_ENABLED` as False.)

---

## REMOTE_AUTH_ENABLED

Default: `False`

NetBox can be configured to support remote user authentication by inferring user authentication from an HTTP header set by the HTTP reverse proxy (e.g. nginx or Apache). Set this to `True` to enable this functionality. (Local authentication will still take effect as a fallback.) (`REMOTE_AUTH_DEFAULT_GROUPS` will not function if `REMOTE_AUTH_ENABLED` is disabled)

---

## REMOTE_AUTH_GROUP_HEADER

Default: `'HTTP_REMOTE_USER_GROUP'`

When remote user authentication is in use, this is the name of the HTTP header which informs NetBox of the currently authenticated user. For example, to use the request header `X-Remote-User-Groups` it needs to be set to `HTTP_X_REMOTE_USER_GROUPS`. (Requires `REMOTE_AUTH_ENABLED` and `REMOTE_AUTH_GROUP_SYNC_ENABLED` )

---

## REMOTE_AUTH_GROUP_SEPARATOR

Default: `|` (Pipe)

The Seperator upon which `REMOTE_AUTH_GROUP_HEADER` gets split into individual Groups. This needs to be coordinated with your authentication Proxy. (Requires `REMOTE_AUTH_ENABLED` and `REMOTE_AUTH_GROUP_SYNC_ENABLED` )

---

## REMOTE_AUTH_GROUP_SYNC_ENABLED

Default: `False`

NetBox can be configured to sync remote user groups by inferring user authentication from an HTTP header set by the HTTP reverse proxy (e.g. nginx or Apache). Set this to `True` to enable this functionality. (Local authentication will still take effect as a fallback.) (Requires `REMOTE_AUTH_ENABLED`.)

---

## REMOTE_AUTH_HEADER

Default: `'HTTP_REMOTE_USER'`

When remote user authentication is in use, this is the name of the HTTP header which informs NetBox of the currently authenticated user. For example, to use the request header `X-Remote-User` it needs to be set to `HTTP_X_REMOTE_USER`. (Requires `REMOTE_AUTH_ENABLED`.)

---

## REMOTE_AUTH_USER_EMAIL

Default: `'HTTP_REMOTE_USER_EMAIL'`

When remote user authentication is in use, this is the name of the HTTP header which informs NetBox of the email address of the currently authenticated user. For example, to use the request header `X-Remote-User-Email` it needs to be set to `HTTP_X_REMOTE_USER_EMAIL`. (Requires `REMOTE_AUTH_ENABLED`.)

---

## REMOTE_AUTH_USER_FIRST_NAME

Default: `'HTTP_REMOTE_USER_FIRST_NAME'`

When remote user authentication is in use, this is the name of the HTTP header which informs NetBox of the first name of the currently authenticated user. For example, to use the request header `X-Remote-User-First-Name` it needs to be set to `HTTP_X_REMOTE_USER_FIRST_NAME`. (Requires `REMOTE_AUTH_ENABLED`.)

---

## REMOTE_AUTH_USER_LAST_NAME

Default: `'HTTP_REMOTE_USER_LAST_NAME'`

When remote user authentication is in use, this is the name of the HTTP header which informs NetBox of the last name of the currently authenticated user. For example, to use the request header `X-Remote-User-Last-Name` it needs to be set to `HTTP_X_REMOTE_USER_LAST_NAME`. (Requires `REMOTE_AUTH_ENABLED`.)

---

## REMOTE_AUTH_SUPERUSER_GROUPS

Default: `[]` (Empty list)

The list of groups that promote an remote User to Superuser on Login. If group isn't present on next Login, the Role gets revoked. (Requires `REMOTE_AUTH_ENABLED` and `REMOTE_AUTH_GROUP_SYNC_ENABLED` )

---

## REMOTE_AUTH_SUPERUSERS

Default: `[]` (Empty list)

The list of users that get promoted to Superuser on Login. If user isn't present in list on next Login, the Role gets revoked. (Requires `REMOTE_AUTH_ENABLED` and `REMOTE_AUTH_GROUP_SYNC_ENABLED` )

---

## REMOTE_AUTH_STAFF_GROUPS

Default: `[]` (Empty list)

The list of groups that promote an remote User to Staff on Login. If group isn't present on next Login, the Role gets revoked. (Requires `REMOTE_AUTH_ENABLED` and `REMOTE_AUTH_GROUP_SYNC_ENABLED` )

---

## REMOTE_AUTH_STAFF_USERS

Default: `[]` (Empty list)

The list of users that get promoted to Staff on Login. If user isn't present in list on next Login, the Role gets revoked. (Requires `REMOTE_AUTH_ENABLED` and `REMOTE_AUTH_GROUP_SYNC_ENABLED` )
