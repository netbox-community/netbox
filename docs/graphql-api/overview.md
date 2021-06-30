# GraphQL API Overview

NetBox provides a read-only [GraphQL](https://graphql.org/) API to complement its REST API. This API is powered by the [Graphene](https://graphene-python.org/) library and [Graphene-Django](https://docs.graphene-python.org/projects/django/en/latest/).

## Queries

GraphQL enables the client to specify an arbitrary nested list of fields to include in the response. All queries are made to the root `/graphql` API endpoint. For example, to return the circuit ID and provider name of each circuit with an active status, you can issue a request such as the following:

```
curl -H "Authorization: Token $TOKEN" \
-H "Content-Type: application/json" \
-H "Accept: application/json" \
http://netbox/graphql/ \
--data '{"query": "query {circuits(status:\"active\" {cid provider {name}}}"}'
```

The response will include the requested data formatted as JSON:

```json
{
  "data": {
    "circuits": [
      {
        "cid": "1002840283",
        "provider": {
          "name": "CenturyLink"
        }
      },
      {
        "cid": "1002840457",
        "provider": {
          "name": "CenturyLink"
        }
      }
    ]
  }
}
```

!!! note
    It's recommended to pass the return data through a JSON parser such as `jq` for better readability.

NetBox provides both a singular and plural query field for each object type:

* `object`: Returns a single object. Must specify the object's unique ID as `(id: 123)`.
* `objects`: Returns a list of objects, optionally filtered by given parameters.

For more detail on constructing GraphQL queries, see the [Graphene documentation](https://docs.graphene-python.org/en/latest/).

## Filtering

The GraphQL API employs the same filtering logic as the UI and REST API. Filters can be specified as key-value pairs within parentheses immediately following the query name. For example, the following will return only sites within the North Carolina region with a status of active:

```
{"query": "query {sites(region:\"north-carolina\", status:\"active\") {name}}"}
```

## Authentication

NetBox's GraphQL API uses the same API authentication tokens as its REST API. Authentication tokens are included with requests by attaching an `Authorization` HTTP header in the following form:

```
Authorization: Token $TOKEN
```

## Disabling the GraphQL API

If not needed, the GraphQL API can be disabled by setting the [`GRAPHQL_ENABLED`](../configuration/optional-settings.md#graphql_enabled) configuration parameter to False and restarting NetBox.
