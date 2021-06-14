# REST API Authentication

The NetBox REST API primarily employs token-based authentication. For convenience, cookie-based authentication can also be used when navigating the browsable API.

{!docs/models/users/token.md!}

## Authenticating to the API

An authentication token is attached to a request by setting the `Authorization` header to the string `Token` followed by a space and the user's token:

```
$ curl -H "Authorization: Token $TOKEN" \
-H "Accept: application/json; indent=4" \
https://netbox/api/dcim/sites/
{
    "count": 10,
    "next": null,
    "previous": null,
    "results": [...]
}
```

A token is not required for read-only operations which have been exempted from permissions enforcement (using the [`EXEMPT_VIEW_PERMISSIONS`](../configuration/optional-settings.md#exempt_view_permissions) configuration parameter). However, if a token _is_ required but not present in a request, the API will return a 403 (Forbidden) response:

```
$ curl https://netbox/api/dcim/sites/
{
    "detail": "Authentication credentials were not provided."
}
```

## Initial Token Provisioning

Ideally, each user should provision his or her own REST API token(s) via the web UI. However, you may encounter where a token must be created by a user via the REST API itself. NetBox provides a special endpoint to provision tokens using a valid username and password combination.

To provision a token via the REST API, make a `POST` request to the `/api/users/tokens/provision/` endpoint:

```
$ curl -X POST \
-H "Content-Type: application/json" \
-H "Accept: application/json; indent=4" \
https://netbox/api/users/tokens/provision/
{
    "username": "hankhill",
    "password: "I<3C3H8",
}
```

Note that we are _not_ passing an existing REST API token with this request. If the supplied credentials are valid, a new REST API token will be automatically created for the user. Note that the key will be automatically generated, and write ability will be enabled.

```json
{
    "id": 6,
    "url": "https://netbox/api/users/tokens/6/",
    "display": "3c9cb9 (hankhill)",
    "user": {
        "id": 2,
        "url": "https://netbox/api/users/users/2/",
        "display": "hankhill",
        "username": "hankhill"
    },
    "created": "2021-06-11T20:09:13.339367Z",
    "expires": null,
    "key": "9fc9b897abec9ada2da6aec9dbc34596293c9cb9",
    "write_enabled": true,
    "description": ""
}
```
