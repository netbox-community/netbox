# Tokens

A token is a secret credential associated with a [user](./user.md) which authenticates requests to NetBox's REST and GraphQL APIs. A user may hold multiple tokens; each can be independently expired, restricted, or revoked.

Beginning with NetBox v4.5, two token versions are supported. v2 tokens (the default for newly-created tokens) are stored only as a salted HMAC digest, and the plaintext is shown to the user only once at creation time. Legacy v1 tokens store the plaintext directly; **their use is deprecated and support will be removed in NetBox v5.0.** See the [REST API authentication](../../integrations/rest-api.md#authentication) documentation for the request header formats used by each version.

## Fields

### Version

Indicates whether this is a v1 (legacy) or v2 token. v2 is the default and is strongly preferred. **v1 tokens are deprecated and will be removed in NetBox v5.0.**

### User

The [user](./user.md) which owns the token. All requests authenticated with the token are performed as this user.

### Description

A free-form description of the token (e.g. naming the application or automation that uses it).

### Created

The date and time at which the token was created.

### Expires

An optional date and time after which the token will no longer be valid. Tokens without an expiration never expire.

### Last Used

The date and time at which the token was most recently used to authenticate a request. This value is updated at most once per minute to limit database write overhead.

### Enabled

When unset, the token is temporarily revoked. Disabled tokens cannot be used to authenticate requests but are not deleted, allowing them to be re-enabled later.

### Write Enabled

When unset, the token may only be used for read operations (e.g. `GET`). All write operations (`POST`, `PATCH`, `PUT`, `DELETE`) made with the token will be rejected.

### Allowed IPs

An optional list of IPv4 and/or IPv6 prefixes from which the token may be used. If set, requests originating from any other source address will be rejected.

### Key (v2 only)

A short, randomly-generated identifier transmitted in plaintext alongside each request. The key allows the server to locate the matching token record before validating the secret portion.

### Plaintext (v1 only)

The full plaintext value of a v1 token. Stored as-is in the database, which is one of the reasons v2 tokens are preferred.
