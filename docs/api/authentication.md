# REST API Authentication

The NetBox API employs token-based authentication. For convenience, cookie authentication can also be used when navigating the browsable API.

{!docs/models/users/token.md!}

## Authenticating to the API

By default, read operations will be available without authentication. In this case, a token may be included in the request, but is not necessary.

```
$ curl -H "Accept: application/json; indent=4" http://localhost/api/dcim/sites/
{
    "count": 10,
    "next": null,
    "previous": null,
    "results": [...]
}
```

However, if the [`LOGIN_REQUIRED`](../../configuration/optional-settings/#login_required) configuration setting has been set to `True`, all requests must be authenticated.

```
$ curl -H "Accept: application/json; indent=4" http://localhost/api/dcim/sites/
{
    "detail": "Authentication credentials were not provided."
}
```

To authenticate to the API, set the HTTP `Authorization` header to the string `Token ` (note the trailing space) followed by the token key.

```
$ curl -H "Authorization: Token d2f763479f703d80de0ec15254237bc651f9cdc0" -H "Accept: application/json; indent=4" http://localhost/api/dcim/sites/
{
    "count": 10,
    "next": null,
    "previous": null,
    "results": [...]
}
```

Additionally, the browsable interface to the API (which can be seen by navigating to the API root `/api/` in a web browser) will attempt to authenticate requests using the same cookie that the normal NetBox front end uses. Thus, if you have logged into NetBox, you will be logged into the browsable API as well.
