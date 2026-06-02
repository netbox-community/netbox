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

## SENTRY_ENABLED

Default: `False`

Set to `True` to enable automatic error reporting via [Sentry](https://sentry.io/).

!!! note
    The `sentry-sdk` Python package is required to enable Sentry integration.

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

