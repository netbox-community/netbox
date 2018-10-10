The NetBox API employs token-based authentication. For convenience, cookie authentication can also be used when navigating the browsable API.

# Tokens

A token is a unique identifier that identifies a user to the API. Each user in NetBox may have one or more tokens which he or she can use to authenticate to the API. To create a token, navigate to the API tokens page at `/user/api-tokens/`.

!!! note
    The creation and modification of API tokens can be restricted per user by an administrator. If you don't see an option to create an API token, ask an administrator to grant you access.

Each token contains a 160-bit key represented as 40 hexadecimal characters. When creating a token, you'll typically leave the key field blank so that a random key will be automatically generated. However, NetBox allows you to specify a key in case you need to restore a previously deleted token to operation.

By default, a token can be used for all operations available via the API. Deselecting the "write enabled" option will restrict API requests made with the token to read operations (e.g. GET) only.

Additionally, a token can be set to expire at a specific time. This can be useful if an external client needs to be granted temporary access to NetBox.

# Authenticating to the API

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

However, if the [`LOGIN_REQUIRED`](../configuration/optional-settings/#login_required) configuration setting has been set to `True`, all requests must be authenticated.

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
