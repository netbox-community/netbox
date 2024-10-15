# Authentication & Permissions

## Object-Based Permissions

NetBox boasts a very robust permissions system which extends well beyond the model-based permissions of the underlying Django framework. Assigning permissions in NetBox involves several dimensions:

* The type(s) of object to which the permission applies
* The users and/or groups being granted the permissions
* The action(s) permitted by the permission (e.g. view, add, change, etc.)
* Any constraints limiting application of the permission to a particular subset of objects

The implementation of constrains is what enables NetBox administrators to assign per-object permissions: Users can be limited to viewing or interacting with arbitrary subsets of objects based on the objects' attributes. For example, you might restrict a particular user to viewing only those prefixes or IP addresses within a particular VRF. Or you might restrict a group to modifying devices within a particular region.

Permission constraints are declared in JSON format when creating a permission, and operate very similarly to Django ORM queries. For instance, here's a constraint that matches reserved VLANs with a VLAN ID between 100 and 199:

```json
[
  {
    "vid__gte": 100,
    "vid__lt": 200
  },
  {
    "status": "reserved"
  }
]
```

Check out the [permissions documentation](../administration/permissions.md) for more information about permission constraints.

## LDAP Authentication

NetBox includes a built-in authentication backend for authenticating users against a remote LDAP server. The [installation documentation](../installation/6-ldap.md) provides more detail on this capability.

## Single Sign-On (SSO)

NetBox integrates with the open source [python-social-auth](https://github.com/python-social-auth) library to provide [myriad options](https://python-social-auth.readthedocs.io/en/latest/backends/index.html#supported-backends) for single sign-on (SSO) authentication. These include:

* Cognito
* GitHub & GitHub Enterprise
* GitLab
* Google
* Hashicorp Vault
* Keycloak
* Microsoft Entra ID
* Microsoft Graph
* Okta
* OIDC

...and many others. It's also possible to build your own custom backends as needed using python-social-auth's base OAuth, OpenID, and SAML classes. You can find some examples of configuring SSO in NetBox' [authentication documentation](../administration/authentication/overview.md).
