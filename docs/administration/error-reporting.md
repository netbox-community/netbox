# Error Reporting

## Sentry

### Enabling Error Reporting

NetBox supports native integration with [Sentry](https://sentry.io/) for automatic error reporting. To enable this functionality, simply set `SENTRY_ENABLED` to True in `configuration.py`. Errors will be sent to a Sentry ingestor maintained by the NetBox team for analysis.

```python
SENTRY_ENABLED = True
```

### Using a Custom DSN

If you prefer instead to use your own Sentry ingestor, you'll need to first create a new project under your Sentry account to represent your NetBox deployment and obtain its corresponding data source name (DSN). This looks like a URL similar to the example below:

```
https://examplePublicKey@o0.ingest.sentry.io/0
```

Once you have obtained a DSN, configure Sentry in NetBox's `configuration.py` file with the following parameters:

```python
SENTRY_ENABLED = True
SENTRY_DSN = "https://examplePublicKey@o0.ingest.sentry.io/0"
```

### Assigning Tags

You can optionally attach one or more arbitrary tags to the outgoing error reports if desired by setting the `SENTRY_TAGS` parameter:

```python
SENTRY_TAGS = {
    "custom.foo": "123",
    "custom.bar": "abc",
}
```

!!! warning "Reserved tag prefixes"
    Avoid using any tag names which begin with `netbox.`, as this prefix is reserved by the NetBox application.

### Testing

Once the configuration has been saved, restart the NetBox service.

To test Sentry operation, try generating a 404 (page not found) error by navigating to an invalid URL, such as `https://netbox/404-error-testing`. (Be sure that debug mode has been disabled.) After receiving a 404 response from the NetBox server, you should see the issue appear shortly in Sentry.
