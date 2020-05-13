## Tokens

A token is a unique identifier that identifies a user to the API. Each user in NetBox may have one or more tokens which he or she can use to authenticate to the API. To create a token, navigate to the API tokens page at `/user/api-tokens/`.

!!! note
    The creation and modification of API tokens can be restricted per user by an administrator. If you don't see an option to create an API token, ask an administrator to grant you access.

Each token contains a 160-bit key represented as 40 hexadecimal characters. When creating a token, you'll typically leave the key field blank so that a random key will be automatically generated. However, NetBox allows you to specify a key in case you need to restore a previously deleted token to operation.

By default, a token can be used for all operations available via the API. Deselecting the "write enabled" option will restrict API requests made with the token to read operations (e.g. GET) only.

Additionally, a token can be set to expire at a specific time. This can be useful if an external client needs to be granted temporary access to NetBox.
