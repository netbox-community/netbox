# NAPALM

NetBox supports integration with the [NAPALM automation](https://napalm-automation.net/) library. NAPALM allows NetBox to fetch live data from devices and return it to a requester via its REST API.

!!! info
    To enable the integration, the NAPALM library must be installed. See [installation steps](../../installation/3-netbox/#napalm-automation-optional) for more information.

```
GET /api/dcim/devices/1/napalm/?method=get_environment

{
    "get_environment": {
        ...
    }
}
```

## Authentication

By default, the [`NAPALM_USERNAME`](../../configuration/optional-settings/#napalm_username) and [`NAPALM_PASSWORD`](../../configuration/optional-settings/#napalm_password) are used for NAPALM authentication. They can be overridden for an individual API call through the `X-NAPALM-Username` and `X-NAPALM-Password` headers.

```
$ curl "http://localhost/api/dcim/devices/1/napalm/?method=get_environment" \
-H "Authorization: Token f4b378553dacfcfd44c5a0b9ae49b57e29c552b5" \
-H "Content-Type: application/json" \
-H "Accept: application/json; indent=4" \
-H "X-NAPALM-Username: foo" \
-H "X-NAPALM-Password: bar"
```

## Method Support

The list of supported NAPALM methods depends on the [NAPALM driver](https://napalm.readthedocs.io/en/latest/support/index.html#general-support-matrix) configured for the platform of a device. NetBox only supports [get](https://napalm.readthedocs.io/en/latest/support/index.html#getters-support-matrix) methods.

## Multiple Methods

More than one method in an API call can be invoked by adding multiple `method` parameters. For example:

```
GET /api/dcim/devices/1/napalm/?method=get_ntp_servers&method=get_ntp_peers

{
    "get_ntp_servers": {
        ...
    },
    "get_ntp_peers": {
        ...
    }
}
```

## Optional Arguments

The behavior of NAPALM drivers can be adjusted according to the [optional arguments](https://napalm.readthedocs.io/en/latest/support/index.html#optional-arguments). NetBox exposes those arguments using headers prefixed with `X-NAPALM-`.


For instance, the SSH port is changed to 2222 in this API call:

```
$ curl "http://localhost/api/dcim/devices/1/napalm/?method=get_environment" \
-H "Authorization: Token f4b378553dacfcfd44c5a0b9ae49b57e29c552b5" \
-H "Content-Type: application/json" \
-H "Accept: application/json; indent=4" \
-H "X-NAPALM-port: 2222"
```
