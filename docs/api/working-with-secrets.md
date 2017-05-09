As with most other objects, the NetBox API can be used to create, modify, and delete secrets. However, additional steps are needed to encrypt or decrypt secret data.

# Generating a Session Key

In order to encrypt or decrypt secret data, a session key must be attached to the API request. To generate a session key, send an authenticated request to the `/api/secrets/get-session-key/` endpoint with the private RSA key which matches your [UserKey](../data-model/secrets/#user-keys). The private key must be POSTed with the name `private_key`.

```
$ curl -X POST http://localhost:8000/api/secrets/get-session-key/ \
-H "Authorization: Token c639d619ecbeb1f3055c4141ba6870e20572edd7" \
-H "Accept: application/json; indent=4" \
--data-urlencode "private_key@<filename>"
{
    "session_key": "dyEnxlc9lnGzaOAV1dV/xqYPV63njIbdZYOgnAlGPHk="
}
```

!!! note
    To read the private key from a file, use the convention above. Alternatively, the private key can be read from an environment variable using `--data-urlencode "private_key=$PRIVATE_KEY"`.

The request uses your private key to unlock your stored copy of the master key and generate a session key which can be attached in the `X-Session-Key` header of future API requests.

# Retrieving Secrets

A session key is not needed to retrieve unencrypted secrets: The secret is returned like any normal object with its `plaintext` field set to null.

```
$ curl http://localhost:8000/api/secrets/secrets/2587/ \
-H "Authorization: Token c639d619ecbeb1f3055c4141ba6870e20572edd7" \
-H "Accept: application/json; indent=4"
{
    "id": 2587,
    "device": {
        "id": 1827,
        "url": "http://localhost:8000/api/dcim/devices/1827/",
        "name": "MyTestDevice",
        "display_name": "MyTestDevice"
    },
    "role": {
        "id": 1,
        "url": "http://localhost:8000/api/secrets/secret-roles/1/",
        "name": "Login Credentials",
        "slug": "login-creds"
    },
    "name": "admin",
    "plaintext": null,
    "hash": "pbkdf2_sha256$1000$G6mMFe4FetZQ$f+0itZbAoUqW5pd8+NH8W5rdp/2QNLIBb+LGdt4OSKA=",
    "created": "2017-03-21",
    "last_updated": "2017-03-21T19:28:44.265582Z"
}
```

To decrypt a secret, we must include our session key in the `X-Session-Key` header:

```
$ curl http://localhost:8000/api/secrets/secrets/2587/ \
-H "Authorization: Token c639d619ecbeb1f3055c4141ba6870e20572edd7" \
-H "Accept: application/json; indent=4" \
-H "X-Session-Key: dyEnxlc9lnGzaOAV1dV/xqYPV63njIbdZYOgnAlGPHk="
{
    "id": 2587,
    "device": {
        "id": 1827,
        "url": "http://localhost:8000/api/dcim/devices/1827/",
        "name": "MyTestDevice",
        "display_name": "MyTestDevice"
    },
    "role": {
        "id": 1,
        "url": "http://localhost:8000/api/secrets/secret-roles/1/",
        "name": "Login Credentials",
        "slug": "login-creds"
    },
    "name": "admin",
    "plaintext": "foobar",
    "hash": "pbkdf2_sha256$1000$G6mMFe4FetZQ$f+0itZbAoUqW5pd8+NH8W5rdp/2QNLIBb+LGdt4OSKA=",
    "created": "2017-03-21",
    "last_updated": "2017-03-21T19:28:44.265582Z"
}
```

Lists of secrets can be decrypted in this manner as well:

```
$ curl http://localhost:8000/api/secrets/secrets/?limit=3 \
-H "Authorization: Token c639d619ecbeb1f3055c4141ba6870e20572edd7" \
-H "Accept: application/json; indent=4" \
-H "X-Session-Key: dyEnxlc9lnGzaOAV1dV/xqYPV63njIbdZYOgnAlGPHk="
{
    "count": 3482,
    "next": "http://localhost:8000/api/secrets/secrets/?limit=3&offset=3",
    "previous": null,
    "results": [
        {
            "id": 2587,
            ...
            "plaintext": "foobar",
            ...
        },
        {
            "id": 2588,
            ...
            "plaintext": "MyP@ssw0rd!",
            ...
        },
        {
            "id": 2589,
            ...
            "plaintext": "AnotherSecret!",
            ...
        },
    ]
}
```

# Creating Secrets

Session keys are also used to decrypt new or modified secrets. This is done by setting the `plaintext` field of the submitted object:

```
$ curl -X POST http://localhost:8000/api/secrets/secrets/ \
-H "Content-Type: application/json" \
-H "Authorization: Token c639d619ecbeb1f3055c4141ba6870e20572edd7" \
-H "Accept: application/json; indent=4" \
-H "X-Session-Key: dyEnxlc9lnGzaOAV1dV/xqYPV63njIbdZYOgnAlGPHk=" \
--data '{"device": 1827, "role": 1, "name": "backup", "plaintext": "Drowssap1"}'
{
    "id": 2590,
    "device": 1827,
    "role": 1,
    "name": "backup",
    "plaintext": "Drowssap1"
}
```

!!! note
    Don't forget to include the `Content-Type: application/json` header when making a POST request.
