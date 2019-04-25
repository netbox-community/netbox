# Prometheus Metrics

NetBox supports optionally exposing native Prometheus metrics from the application. [Prometheus](https://prometheus.io/) is a popular time series metric platform used for monitoring.

NetBox exposes metrics at the `/metrics` HTTP endpoint, e.g. `https://netbox.local/metrics`. Metric exposition can be toggled with the `METRICS_ENABLED` configuration setting. Metrics are exposed by default.

## Metric Types

NetBox makes use of the [django-prometheus](https://github.com/korfuri/django-prometheus) library to export a number of different types of metrics, including:

- Per model insert, update, and delete counters
- Per view request counters
- Per view request latency histograms
- Request body size histograms
- Response body size histograms
- Response code counters
- Database connection, execution, and error counters
- Cache hit, miss, and invalidation counters
- Django middleware latency histograms
- Other Django related metadata metrics

For the exhaustive list of exposed metrics, visit the `/metrics` endpoint on your NetBox instance.
