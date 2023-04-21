# API & Integration

NetBox includes a slew of features which enable integration with other tools and resources powering your network.

## REST API

NetBox's REST API, powered by the [Django REST Framework](https://www.django-rest-framework.org/), provides a robust yet accessible interface for creating, modifying, and deleting objects. Employing HTTP for transfer and JSON for data encapsulation, the REST API is easily consumed by clients on any platform and extremely well suited for automation tasks.

```no-highlight
curl -s -X POST \
-H "Authorization: Token $TOKEN" \
-H "Content-Type: application/json" \
http://netbox/api/ipam/prefixes/ \
--data '{"prefix": "192.0.2.0/24", "site": {"name": "Branch 12"}}'
```

The REST API employs token-based authentication, which maps API clients to user accounts and their assigned permissions. The API endpoints are fully documented using OpenAPI, and NetBox even includes a convenient browser-based version of the API for exploration. The open source [pynetbox](https://github.com/netbox-community/pynetbox) and [go-netbox](https://github.com/netbox-community/go-netbox) API client libraries are also available for Python and Go, respectively.

To learn more about this feature, check out the [REST API documentation](../integrations/rest-api.md).

## GraphQL API

NetBox also provides a [GraphQL](https://graphql.org/) API to complement its REST API. GraphQL enables complex queries for arbitrary objects and fields, enabling the client to retrieve only the specific data it needs from NetBox. This is a special-purpose read-only API intended for efficient queries. Like the REST API, the GraphQL API employs token-based authentication.

To learn more about this feature, check out the [GraphQL API documentation](../integrations/graphql-api.md).

## Webhooks

A webhook is a mechanism for conveying to some external system a change that took place in NetBox. For example, you may want to notify a monitoring system whenever the status of a device is updated in NetBox. This can be done by creating a webhook for the device model in NetBox and identifying the webhook receiver. When NetBox detects a change to a device, an HTTP request containing the details of the change and who made it be sent to the specified receiver. Webhooks are an excellent mechanism for building event-based automation processes.

To learn more about this feature, check out the [webhooks documentation](../integrations/webhooks.md).

## Prometheus Metrics

NetBox includes a special `/metrics` view which exposes metrics for a [Prometheus](https://prometheus.io/) scraper, powered by the open source [django-prometheus](https://github.com/korfuri/django-prometheus) library. To learn more about this feature, check out the [Prometheus metrics documentation](../integrations/prometheus-metrics.md).
