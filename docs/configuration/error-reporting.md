# Error Reporting Settings

## SENTRY_DSN

Default: None

Defines a Sentry data source name (DSN) for automated error reporting. `SENTRY_ENABLED` must be True for this parameter to take effect. For example:

```
SENTRY_DSN = "https://examplePublicKey@o0.ingest.sentry.io/0"
```

---

## SENTRY_ENABLED

Default: False

Set to True to enable automatic error reporting via [Sentry](https://sentry.io/).

!!! note
    The `sentry-sdk` Python package is required to enable Sentry integration.

---

## SENTRY_SAMPLE_RATE

Default: 1.0 (all)

The sampling rate for errors. Must be a value between 0 (disabled) and 1.0 (report on all errors).

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

Default: 0 (disabled)

The sampling rate for transactions. Must be a value between 0 (disabled) and 1.0 (report on all transactions).

!!! warning "Consider performance implications"
    A high sampling rate for transactions can induce significant performance penalties. If transaction reporting is desired, it is recommended to use a relatively low sample rate of 10% to 20% (0.1 to 0.2).
