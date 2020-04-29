# Prometheus Metrics

NetBox supports optionally exposing native Prometheus metrics from the application. [Prometheus](https://prometheus.io/) is a popular time series metric platform used for monitoring.

NetBox exposes metrics at the `/metrics` HTTP endpoint, e.g. `https://netbox.local/metrics`. Metric exposition can be toggled with the `METRICS_ENABLED` configuration setting. Metrics are not exposed by default.

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

## Multi Processing Notes

When deploying NetBox in a multiprocess mannor--such as using Gunicorn as recomented in the installation docs--the Prometheus client library requires the use of a shared directory
to collect metrics from all the worker processes. This can be any arbitrary directory to which the processes have read/write access. This directory is then made available by use of the
`prometheus_multiproc_dir` environment variable.

This can be setup by first creating a shared directory and then adding this line (with the appropriate directory) to the `[Service]` section of the systemd unit file.

```
Environment=prometheus_multiproc_dir=/tmp/prometheus_metrics
```
