# GraphQL API Overview

NetBox provides a read-only [GraphQL](https://graphql.org/) API to complement its REST API. This API is powered by the [Graphene](https://graphene-python.org/) library and [Graphene-Django](https://docs.graphene-python.org/projects/django/en/latest/).

## Queries

GraphQL enables the client to specify an arbitrary nested list of fields to include in the response. All queries are made to the root `/graphql` API endpoint. For example, to return the circuit ID and provider name of each circuit with an active status, you can issue a request such as the following:

```
curl -H "Authorization: Token $TOKEN" \
-H "Content-Type: application/json" \
-H "Accept: application/json" \
http://netbox/graphql/ \
--data '{"query": "query {circuit_list(status:\"active\") {cid provider {name}}}"}'
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

* `$OBJECT`: Returns a single object. Must specify the object's unique ID as `(id: 123)`.
* `$OBJECT_list`: Returns a list of objects, optionally filtered by given parameters.

For example, query `device(id:123)` to fetch a specific device (identified by its unique ID), and query `device_list` (with an optional set of filters) to fetch all devices.

For more detail on constructing GraphQL queries, see the [Graphene documentation](https://docs.graphene-python.org/en/latest/) as well as the [GraphQL queries documentation](https://graphql.org/learn/queries/).

## Filtering

The GraphQL API employs the same filtering logic as the UI and REST API. Filters can be specified as key-value pairs within parentheses immediately following the query name. For example, the following will return only sites within the North Carolina region with a status of active:

```
query {
  site_list(filters: {region: "us-nc", status: "active"}) {
    name
  }
}
```
In addition, filtering can be done on list of related objects as shown in the following query:

```
{
  device_list {
    id
    name
    interfaces(filters: {enabled: true}) {
      name
    }
  }
}
```

## Multiple Return Types

Certain queries can return multiple types of objects, for example cable terminations can return circuit terminations, console ports and many others.  These can be queried using [inline fragments](https://graphql.org/learn/schema/#union-types) as shown below:

```
{
    cable_list {
      id
      a_terminations {
        ... on CircuitTerminationType {
          id
          class_type
        }
        ... on ConsolePortType {
          id
          class_type
        }
        ... on ConsoleServerPortType {
          id
          class_type
        }
      }
    }
}

```
The field "class_type" is an easy way to distinguish what type of object it is when viewing the returned data, or when filtering.  It contains the class name, for example "CircuitTermination" or "ConsoleServerPort".

## Authentication

NetBox's GraphQL API uses the same API authentication tokens as its REST API. Authentication tokens are included with requests by attaching an `Authorization` HTTP header in the following form:

```
Authorization: Token $TOKEN
```

## Disabling the GraphQL API

If not needed, the GraphQL API can be disabled by setting the [`GRAPHQL_ENABLED`](../configuration/miscellaneous.md#graphql_enabled) configuration parameter to False and restarting NetBox.
