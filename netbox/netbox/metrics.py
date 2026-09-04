from django.conf import settings
from django_prometheus import middleware
from django_prometheus.conf import NAMESPACE
from prometheus_client import Counter

__all__ = (
    'Metrics',
    'increment_client_disconnects',
)


class Metrics(middleware.Metrics):
    """
    Expand the stock Metrics class from django_prometheus to add our own counters.
    """

    def register(self):
        super().register()

        # REST API metrics
        self.rest_api_requests = self.register_metric(
            Counter,
            "rest_api_requests_total_by_method",
            "Count of total REST API requests by method",
            ["method"],
            namespace=NAMESPACE,
        )
        self.rest_api_requests_by_view_method = self.register_metric(
            Counter,
            "rest_api_requests_total_by_view_method",
            "Count of REST API requests by view & method",
            ["view", "method"],
            namespace=NAMESPACE,
        )

        # GraphQL API metrics
        self.graphql_api_requests = self.register_metric(
            Counter,
            "graphql_api_requests_total",
            "Count of total GraphQL API requests",
            namespace=NAMESPACE,
        )

        # Client disconnect metrics
        self.client_disconnects = self.register_metric(
            Counter,
            "netbox_client_disconnects_total",
            "Count of requests aborted because the HTTP client disconnected, by method & view",
            ["method", "view"],
            namespace=NAMESPACE,
        )


def increment_client_disconnects(method, view):
    """
    Increment the client disconnect counter.

    ClientDisconnectMiddleware is not a django_prometheus middleware and so has no Metrics instance
    of its own. Instantiating the singleton unconditionally would register the entire django_prometheus
    metric set on installations which never expose /metrics, so this is a no-op unless metric
    exposition is enabled. Always go through get_instance(): calling Metrics() directly bypasses the
    singleton and re-registers every metric name in the global registry.
    """
    if not settings.METRICS_ENABLED:
        return
    Metrics.get_instance().client_disconnects.labels(method=method, view=view).inc()
