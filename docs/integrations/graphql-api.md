# GraphQL API Overview

NetBox provides a read-only [GraphQL](https://graphql.org/) API to complement its REST API. This API is powered by [Strawberry Django](https://strawberry.rocks/).

## Queries

GraphQL enables the client to specify an arbitrary nested list of fields to include in the response. All queries are made to the root `/graphql` API endpoint. For example, to return the circuit ID and provider name of each circuit with an active status, you can issue a request such as the following:

```
curl -H "Authorization: Token $TOKEN" \
-H "Content-Type: application/json" \
-H "Accept: application/json" \
http://netbox/graphql/ \
--data '{"query": "query {circuit_list(filters:{status: STATUS_ACTIVE}) {results {cid provider {name}}}}"}'
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
If using the GraphQL API v2 the format will be:

```json
{
  "data": {
    "circuit_list": {
      "results": [
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
}
```

!!! note
    It's recommended to pass the return data through a JSON parser such as `jq` for better readability.

NetBox provides both a singular and plural query field for each object type:

* `$OBJECT`: Returns a single object. Must specify the object's unique ID as `(id: 123)`.
* `$OBJECT_list`: Returns a list of objects, optionally filtered by given parameters.

For example, query `device(id:123)` to fetch a specific device (identified by its unique ID), and query `device_list` (with an optional set of filters) to fetch all devices.

!!! note "Changed in NetBox v4.5"
    If using the GraphQL API v2, List queries now return paginated results. The actual objects are contained within the `results` field of the response, along with `total_count` and `page_info` fields for pagination metadata. Prior to v4.5, list queries returned objects directly as an array.

For more detail on constructing GraphQL queries, see the [GraphQL queries documentation](https://graphql.org/learn/queries/).  For filtering and lookup syntax, please refer to the [Strawberry Django documentation](https://strawberry.rocks/docs/django/guide/filters).

## Filtering

!!! note "Changed in NetBox v4.3"
    The filtering syntax for the GraphQL API has changed substantially in NetBox v4.3.

Filters can be specified as key-value pairs within parentheses immediately following the query name. For example, the following will return only active sites:

```
query {
  site_list(
    filters: {
      status: STATUS_ACTIVE
    }
  ) {
    name
  }
}
```
If using the GraphQL API v2 the format will be:

```
query {
  site_list(
    filters: {
      status: STATUS_ACTIVE
    }
  ) {
    results {
      name
    }
  }
}
```

Filters can be combined with logical operators, such as `OR` and `NOT`. For example, the following will return every site that is planned _or_ assigned to a tenant named Foo:

```
query {
  site_list(
    filters: {
      status: STATUS_PLANNED,
      OR: {
        tenant: {
          name: {
            exact: "Foo"
          }
        }
      }
    }
  ) {
    name
  }
}
```
If using the GraphQL API v2 the format will be:

```
query {
  site_list(
    filters: {
      status: STATUS_PLANNED,
      OR: {
        tenant: {
          name: {
            exact: "Foo"
          }
        }
      }
    }
  ) {
    results {
      name
    }
  }
}
```

Filtering can also be applied to related objects. For example, the following query will return only enabled interfaces for each device:

```
query {
  device_list {
    id
    name
    interfaces(filters: {enabled: true}) {
      name
    }
  }
}
```
If using the GraphQL API v2 the format will be:

```
query {
  device_list {
    results {
      id
      name
      interfaces(filters: {enabled: {exact: true}}) {
        name
      }
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
If using the GraphQL API v2 the format will be:

```
{
  cable_list {
    results {
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
}
```

The field "class_type" is an easy way to distinguish what type of object it is when viewing the returned data, or when filtering.  It contains the class name, for example "CircuitTermination" or "ConsoleServerPort".

## Pagination

Queries can be paginated by specifying pagination in the query and supplying an offset and optionaly a limit in the query.  If no limit is given, a default of 100 is used.  Queries are not paginated unless requested in the query. An example paginated query is shown below:

```
query {
  device_list(pagination: { offset: 0, limit: 20 }) {
    id
  }
}
```
### Pagination in GraphQL API V2

All list queries return paginated results using the `OffsetPaginated` type, which includes:

- `results`: The list of objects matching the query
- `total_count`: The total number of objects matching the filters (without pagination)
- `page_info`: Pagination metadata including `offset` and `limit`

By default, queries return up to 100 results. You can control pagination by specifying the `pagination` parameter with `offset` and `limit` values:

```
query {
  device_list(pagination: { offset: 0, limit: 20 }) {
    total_count
    page_info {
      offset
      limit
    }
    results {
      id
      name
    }
  }
}
```

If you don't need pagination metadata, you can simply query the `results`:

```
query {
  device_list {
    results {
      id
      name
    }
  }
}
```

!!! note
    When not specifying the `pagination` parameter, avoid querying `page_info.limit` as it may return an undefined value. Either provide explicit pagination parameters or only query the `results` and `total_count` fields.

## Authentication

NetBox's GraphQL API uses the same API authentication tokens as its REST API. Authentication tokens are included with requests by attaching an `Authorization` HTTP header in the following form:

```
Authorization: Token $TOKEN
```

## Disabling the GraphQL API

If not needed, the GraphQL API can be disabled by setting the [`GRAPHQL_ENABLED`](../configuration/graphql-api.md#graphql_enabled) configuration parameter to False and restarting NetBox.
