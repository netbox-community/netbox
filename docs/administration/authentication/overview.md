# Authentication

## Local Authentication

Local user accounts and groups can be created in NetBox under the "Authentication" section in the "Admin" menu.

At a minimum, each user account must have a username and password set. User accounts may also denote a first name, last name, and email address. [Permissions](../permissions.md) may also be assigned to individual users and/or groups as needed.

## Remote Authentication

NetBox may be configured to provide user authenticate via a remote backend in addition to local authentication. This is done by setting the `REMOTE_AUTH_BACKEND` configuration parameter to a suitable backend class. NetBox provides several options for remote authentication.

### LDAP Authentication

```python
REMOTE_AUTH_BACKEND = 'netbox.authentication.LDAPBackend'
```

NetBox includes an authentication backend which supports LDAP. See the [LDAP installation docs](../../installation/6-ldap.md) for more detail about this backend.

### HTTP Header Authentication

```python
REMOTE_AUTH_BACKEND = 'netbox.authentication.RemoteUserBackend'
```

Another option for remote authentication in NetBox is to enable HTTP header-based user assignment. The front end HTTP server (e.g. nginx or Apache) performs client authentication as a process external to NetBox, and passes information about the authenticated user via HTTP headers. By default, the user is assigned via the `REMOTE_USER` header, but this can be customized via the `REMOTE_AUTH_HEADER` configuration parameter.

Optionally, user profile information can be supplied by `REMOTE_USER_FIRST_NAME`, `REMOTE_USER_LAST_NAME` and `REMOTE_USER_EMAIL` headers. These are saved to the user's profile during the authentication process. These headers can be customized like the `REMOTE_USER` header.

!!! warning Verify Header Compatibility
    Some WSGI servers may drop headers which contain unsupported characters. For instance, gunicorn v22.0 and later silently drops HTTP headers containing underscores. This behavior can be disabled by changing gunicorn's [`header_map`](https://docs.gunicorn.org/en/stable/settings.html#header-map) setting to `dangerous`.

### Single Sign-On (SSO)

```python
REMOTE_AUTH_BACKEND = 'social_core.backends.google.GoogleOAuth2'
```

NetBox supports single sign-on authentication via the [python-social-auth](https://github.com/python-social-auth) library. To enable SSO, specify the path to the desired authentication backend within the `social_core` Python package. Please see the complete list of [supported authentication backends](https://github.com/python-social-auth/social-core/tree/master/social_core/backends) for the available options.

Most remote authentication backends require some additional configuration through settings prefixed with `SOCIAL_AUTH_`. These will be automatically imported from NetBox's `configuration.py` file. Additionally, the [authentication pipeline](https://python-social-auth.readthedocs.io/en/latest/pipeline.html) can be customized via the `SOCIAL_AUTH_PIPELINE` parameter. (NetBox's default pipeline is defined in `netbox/settings.py` for your reference.)

!!! note "Content Security Policy"
    Beginning an SSO login requires the browser to make a request back to NetBox before it is sent
    on to the identity provider. If you serve NetBox with a Content Security Policy which does not
    permit same-origin connections, SSO logins will fail: add `connect-src 'self'` (or a
    `default-src` which covers it) to your policy.

#### Configuring the SSO module's appearance

The way a remote authentication backend is displayed to the user on the login
page may be adjusted via the `SOCIAL_AUTH_BACKEND_ATTRS` parameter, defaulting
to an empty dictionary. This dictionary maps a `social_core` module's name (ie.
`REMOTE_AUTH_BACKEND.name`) to a couple of parameters, `(display_name, icon)`.

The `display_name` is the name displayed to the user on the login page. The
icon may either be the URL of an icon; refer to a [Material Design
Icons](https://github.com/google/material-design-icons) icon's name; or be
`None` for no icon.

For instance, the OIDC backend may be customized with

```python
SOCIAL_AUTH_BACKEND_ATTRS = {
    'oidc': ("My awesome SSO", "login"),
}
```

#### IdP-Initiated Login

By default, SSO logins are **SP-initiated**: the user clicks a provider button on NetBox's login page, and NetBox redirects the browser to the identity provider. This requires the browser to first make a request back to NetBox, which is why same-origin connections must be permitted by your Content Security Policy (see the note above).

**IdP-initiated login** is the reverse flow: the identity provider itself starts the authentication, for example when a user clicks the NetBox application tile in an Okta dashboard. The IdP navigates the user's browser directly to a NetBox endpoint carrying an `iss` (issuer) and `target_link_uri`.

With `social-auth-app-django` v6, the standard login endpoint `/oauth/login/<backend>/` only accepts `POST` requests to protect against CSRF vulnerabilities. An IdP-initiated login arrives as a `GET` request, so NetBox responds with **HTTP 405 Method Not Allowed**.

To support IdP-initiated logins, enable the upstream launch bridge by adding the following to `configuration.py`:

```python
SOCIAL_AUTH_ENABLE_LAUNCH_BRIDGES = ['idp_launch']
```

This exposes the endpoint `/oauth/idp-launch/<backend>/` (e.g. `/oauth/idp-launch/okta-openidconnect/` for Okta). Configure your identity provider's "Initiate login URI" (or equivalent) to use this endpoint rather than `/oauth/login/<backend>/`.

The two endpoints serve different purposes:

- `/oauth/login/<backend>/` — SP-initiated login. Used by the "Log In" button on NetBox's login page. Accepts `POST` only.
- `/oauth/idp-launch/<backend>/` — IdP-initiated login. Used by the identity provider's dashboard tile. Accepts `GET` and bridges it into the standard `POST`-based login flow.

The launch bridge is opt-in and returns HTTP 404 when not enabled. It requires an OpenID Connect backend, which covers the Okta, Microsoft Entra ID, Google, and generic OIDC backends documented here.
