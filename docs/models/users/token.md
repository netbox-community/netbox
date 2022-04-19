## Tokens

A token is a unique identifier mapped to a NetBox user account. Each user may have one or more tokens which he or she can use for authentication when making REST API requests. To create a token, navigate to the API tokens page under your user profile.

!!! note
    All users can create and manage REST API tokens under the user control panel in the UI. The ability to view, add, change, or delete tokens via the REST API itself is controlled by the relevant model permissions, assigned to users and/or groups in the admin UI. These permissions should be used with great care to avoid accidentally permitting a user to create tokens for other user accounts.

Each token contains a 160-bit key represented as 40 hexadecimal characters. When creating a token, you'll typically leave the key field blank so that a random key will be automatically generated. However, NetBox allows you to specify a key in case you need to restore a previously deleted token to operation.

By default, a token can be used to perform all actions via the API that a user would be permitted to do via the web UI. Deselecting the "write enabled" option will restrict API requests made with the token to read operations (e.g. GET) only.

Additionally, a token can be set to expire at a specific time. This can be useful if an external client needs to be granted temporary access to NetBox.
