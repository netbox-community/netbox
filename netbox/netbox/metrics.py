from django_prometheus.conf import NAMESPACE
from django_prometheus import middleware
from prometheus_client import Counter

__all__ = (
    'Metrics',
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
