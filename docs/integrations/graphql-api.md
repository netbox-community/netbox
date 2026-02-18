# GraphQL API Overview

NetBox provides a read-only [GraphQL](https://graphql.org/) API to complement its REST API. This API is powered by [Strawberry Django](https://strawberry.rocks/).

## Queries

GraphQL enables the client to specify an arbitrary nested list of fields to include in the response. All queries are made to the root `/graphql` API endpoint. For example, to return the circuit ID and provider name of each circuit with an active status, you can issue a request such as the following:

```
curl -H "Authorization: Token $TOKEN" \
-H "Content-Type: application/json" \
-H "Accept: application/json" \
http://netbox/graphql/ \
--data '{"query": "query {circuit_list(filters:{status: STATUS_ACTIVE}) {cid provider {name}}}"}'
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

For more detail on constructing GraphQL queries, see the [GraphQL queries documentation](https://graphql.org/learn/queries/).  For filtering and lookup syntax, please refer to the [Strawberry Django documentation](https://strawberry.rocks/docs/django/guide/filters).

## Filtering

!!! note "Changed in NetBox v4.3"
    The filtering syntax fo the GraphQL API has changed substantially in NetBox v4.3.

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

## Pagination

The GraphQL API supports two types of pagination. Offset-based pagination operates using an offset relative to the first record in a set, specified by the `offset` parameter. For example, the response to a request specifying an offset of 100 will contain the 101st and later matching records. Offset-based pagination feels very natural, but its performance can suffer when dealing with large data sets due to the overhead involved in calculating the relative offset.

The alternative approach is cursor-based pagination, which operates using absolute (rather than relative) primary key values. (These are the numeric IDs assigned to each object in the database.) When using cursor-based pagination, the response will contain records with a primary key greater than or equal to the specified start value, up to the maximum number of results. This strategy requires keeping track of the last seen primary key from each response when paginating through data, but is extremely performant. The cursor is specified by passing the starting object ID via the `start` parameter.

To ensure consistent ordering, objects will always be ordered by their primary keys when cursor-based pagination is used.

!!! note "Cursor-based pagination was introduced in NetBox v4.5.2."

Both pagination strategies support passing an optional `limit` parameter. In both approaches, this specifies the maximum number of objects to include in the response. If no limit is specified, a default value of 100 is used.

### Offset Pagination

The first page will have an `offset` of zero, or the `offset` parameter will be omitted:

```
query {
  device_list(pagination: {offset: 0, limit: 20}) {
    id
  }
}
```

The second page will have an offset equal to the size of the first page. If the number of records is less than the specified limit, there are no more records to process. For example, if a request specifies a `limit` of 20 but returns only 13 records, we can conclude that this is the final page of records.

```
query {
  device_list(pagination: {offset: 20, limit: 20}) {
    id
  }
}
```

### Cursor Pagination

Set the `start` value to zero to fetch the first page. Note that if the `start` parameter is omitted, offset-based pagination will be used by default.

```
query {
  device_list(pagination: {start: 0, limit: 20}) {
    id
  }
}
```

To determine the `start` value for the next page, add 1 to the primary key (`id`) of the last record in the previous page.

For example, if the ID of the last record in the previous response was 123, we would specify a `start` value of 124:

```
query {
  device_list(pagination: {start: 124, limit: 20}) {
    id
  }
}
```

This will return up to 20 records with an ID greater than or equal to 124.

## Authentication

NetBox's GraphQL API uses the same API authentication tokens as its REST API. See the [REST API authentication](./rest-api.md#authentication) documentation for further detail.

## Disabling the GraphQL API

If not needed, the GraphQL API can be disabled by setting the [`GRAPHQL_ENABLED`](../configuration/graphql-api.md#graphql_enabled) configuration parameter to False and restarting NetBox.
