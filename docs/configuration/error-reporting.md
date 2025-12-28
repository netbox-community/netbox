# Error Reporting Settings

## SENTRY_CONFIG

A dictionary mapping keyword arguments to values, to be passed to `sentry_sdk.init()`. See the [Sentry Python SDK documentation](https://docs.sentry.io/platforms/python/) for more information on supported parameters.

The default configuration is shown below:

```python
{
    "sample_rate": 1.0,
    "send_default_pii": False,
    "traces_sample_rate": 0,
}
```

Additionally, `http_proxy` and `https_proxy` are set to the HTTP and HTTPS proxies, respectively, configured for NetBox (if any).

## SENTRY_DSN

!!! warning "This parameter will be removed in NetBox v4.5."
    Set this using `SENTRY_CONFIG` instead:

    ```
    SENTRY_CONFIG = {
        "dsn": "https://examplePublicKey@o0.ingest.sentry.io/0",
    }
    ```

Default: `None`

Defines a Sentry data source name (DSN) for automated error reporting. `SENTRY_ENABLED` must be `True` for this parameter to take effect. For example:

```
SENTRY_DSN = "https://examplePublicKey@o0.ingest.sentry.io/0"
```

---

## SENTRY_ENABLED

Default: `False`

Set to `True` to enable automatic error reporting via [Sentry](https://sentry.io/).

!!! note
    The `sentry-sdk` Python package is required to enable Sentry integration.

---

## SENTRY_SAMPLE_RATE

!!! warning "This parameter will be removed in NetBox v4.5."
    Set this using `SENTRY_CONFIG` instead:

    ```
    SENTRY_CONFIG = {
        "sample_rate": 0.2,
    }
    ```

Default: `1.0` (all)

The sampling rate for errors. Must be a value between 0 (disabled) and 1.0 (report on all errors).

---

## SENTRY_SEND_DEFAULT_PII

!!! warning "This parameter will be removed in NetBox v4.5."
    Set this using `SENTRY_CONFIG` instead:

    ```
    SENTRY_CONFIG = {
        "send_default_pii": True,
    }
    ```

Default: `False`

Maps to the Sentry SDK's [`send_default_pii`](https://docs.sentry.io/platforms/python/configuration/options/#send-default-pii) parameter. If enabled, certain personally identifiable information (PII) is added.

!!! warning "Sensitive data"
    If you enable this option, be aware that sensitive data such as cookies and authentication tokens will be logged.

---

## SENTRY_TAGS

An optional dictionary of tag names and values to apply to Sentry error reports.For example:

```
SENTRY_TAGS = {
    "custom.foo": "123",
    "custom.bar": "abc",
}
```

!!! warning "Reserved tag prefixes"
    Avoid using any tag names which begin with `netbox.`, as this prefix is reserved by the NetBox application.

---

## SENTRY_TRACES_SAMPLE_RATE

!!! warning "This parameter will be removed in NetBox v4.5."
    Set this using `SENTRY_CONFIG` instead:

    ```
    SENTRY_CONFIG = {
        "traces_sample_rate": 0.2,
    }
    ```

Default: `0` (disabled)

The sampling rate for transactions. Must be a value between 0 (disabled) and 1.0 (report on all transactions).

!!! warning "Consider performance implications"
    A high sampling rate for transactions can induce significant performance penalties. If transaction reporting is desired, it is recommended to use a relatively low sample rate of 10% to 20% (0.1 to 0.2).
