# NAPALM Parameters

## NAPALM_USERNAME

## NAPALM_PASSWORD

!!! tip "Dynamic Configuration Parameter"

NetBox will use these credentials when authenticating to remote devices via the supported [NAPALM integration](../integrations/napalm.md), if installed. Both parameters are optional.

!!! note
    If SSH public key authentication has been set up on the remote device(s) for the system account under which NetBox runs, these parameters are not needed.

---

## NAPALM_ARGS

!!! tip "Dynamic Configuration Parameter"

A dictionary of optional arguments to pass to NAPALM when instantiating a network driver. See the NAPALM documentation for a [complete list of optional arguments](https://napalm.readthedocs.io/en/latest/support/#optional-arguments). An example:

```python
NAPALM_ARGS = {
    'api_key': '472071a93b60a1bd1fafb401d9f8ef41',
    'port': 2222,
}
```

Some platforms (e.g. Cisco IOS) require an argument named `secret` to be passed in addition to the normal password. If desired, you can use the configured `NAPALM_PASSWORD` as the value for this argument:

```python
NAPALM_USERNAME = 'username'
NAPALM_PASSWORD = 'MySecretPassword'
NAPALM_ARGS = {
    'secret': NAPALM_PASSWORD,
    # Include any additional args here
}
```

---

## NAPALM_TIMEOUT

!!! tip "Dynamic Configuration Parameter"

Default: 30 seconds

The amount of time (in seconds) to wait for NAPALM to connect to a device.

---

