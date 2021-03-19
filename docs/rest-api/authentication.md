# REST API Authentication

The NetBox REST API primarily employs token-based authentication. For convenience, cookie-based authentication can also be used when navigating the browsable API.

{!docs/models/users/token.md!}

## Authenticating to the API

An authentication token is attached to a request by setting the `Authorization` header to the string `Token` followed by a space and the user's token:

```
$ curl -H "Authorization: Token $TOKEN" \
-H "Accept: application/json; indent=4" \
http://netbox/api/dcim/sites/
{
    "count": 10,
    "next": null,
    "previous": null,
    "results": [...]
}
```

A token is not required for read-only operations which have been exempted from permissions enforcement (using the [`EXEMPT_VIEW_PERMISSIONS`](../configuration/optional-settings.md#exempt_view_permissions) configuration parameter). However, if a token _is_ required but not present in a request, the API will return a 403 (Forbidden) response:

```
$ curl http://netbox/api/dcim/sites/
{
    "detail": "Authentication credentials were not provided."
}
```
