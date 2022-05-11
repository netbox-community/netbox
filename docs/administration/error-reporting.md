# Error Reporting

## Sentry

NetBox v3.2.3 and later support native integration with [Sentry](https://sentry.io/) for automatic error reporting. To enable this feature, begin by creating a new project in Sentry to represent your NetBox deployment and obtain its corresponding data source name (DSN). This looks like a URL similar to the example below:

```
https://examplePublicKey@o0.ingest.sentry.io/0
```

Once you have obtained a DSN, configure Sentry in NetBox's `configuration.py` file with the following parameters:

```python
SENTRY_ENABLED = True
SENTRY_DSN = "https://YourDSNgoesHere@o0.ingest.sentry.io/0"
```

You can optionally attach one or more arbitrary tags to the outgoing error reports if desired by setting the `SENTRY_TAGS` parameter:

```python
SENTRY_TAGS = {
    "custom.foo": "123",
    "custom.bar": "abc",
}
```

Once the configuration has been saved, restart the NetBox service.

To test Sentry operation, try generating a 404 (page not found) error by navigating to an invalid URL, such as `https://netbox/404-error-testing`. After receiving a 404 response from the NetBox server, you should see the issue appear shortly in Sentry.
