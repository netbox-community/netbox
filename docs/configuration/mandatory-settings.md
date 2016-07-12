NetBox's local configuration is held in `netbox/netbox/configuration.py`. An example configuration is provided at `netbox/netbox/configuration.example.py`. You may copy or rename the example configuration and make changes as appropriate. NetBox will not run without a configuration file.

## ALLOWED_HOSTS

This is a list of valid fully-qualified domain names (FQDNs) for the NetBox server. NetBox will not permit write access to the server via any other hostnames. The first FQDN in the list will be treated as the preferred name.

Example:

```
ALLOWED_HOSTS = ['netbox.example.com', '192.0.2.123']
```

---

## DATABASE

NetBox requires access to a PostgreSQL database service to store data. This service can run locally or on a remote system. The following parameters must be defined within the `DATABASE` dictionary:

* NAME - Database name
* USER - PostgreSQL username
* PASSWORD - PostgreSQL password
* HOST - Name or IP address of the database server (use `localhost` if running locally)
* PORT - TCP port of the PostgreSQL service; leave blank for default port (5432)

Example:

```
DATABASE = {
    'NAME': 'netbox',               # Database name
    'USER': 'netbox',               # PostgreSQL username
    'PASSWORD': 'J5brHrAXFLQSif0K', # PostgreSQL password
    'HOST': 'localhost',            # Database server
    'PORT': '',                     # Database port (leave blank for default)
}
```

---

## SECRET_KEY

This is a secret cryptographic key is used to improve the security of cookies and password resets. The key defined here should not be shared outside of the configuration file. `SECRET_KEY` can be changed at any time, however be aware that doing so will invalidate all existing sessions.

Please note that this key is **not** used for hashing user passwords or for the encrypted storage of secret data in NetBox.

`SECRET_KEY` should be at least 50 characters in length and contain a random mix of letters, digits, and symbols. The script located at `netbox/generate_secret_key.py` may be used to generate a suitable key.
