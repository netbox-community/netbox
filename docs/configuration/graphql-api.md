# GraphQL API Parameters

## GRAPHQL_DEFAULT_VERSION

!!! note "This parameter was introduced in NetBox v4.5."

Default: `1`

Designates the default version of the GraphQL API served by `/graphql/`. To access a specific version, append the version number to the URL, e.g. `/graphql/v2/`.

---

## GRAPHQL_ENABLED

!!! tip "Dynamic Configuration Parameter"

Default: `True`

Setting this to `False` will disable the GraphQL API.

---

## GRAPHQL_MAX_ALIASES

Default: `10`

The maximum number of queries that a GraphQL API request may contain.

---

## GRAPHQL_MAX_QUERY_DEPTH

!!! note "This parameter was introduced in NetBox v4.6.1."

Default: `None` (no limit)

The maximum allowed depth of any GraphQL query. When set to a positive integer, requests containing queries that exceed this depth will be rejected. Leaving this parameter unset (or setting it to `None` or `0`) disables query depth enforcement.
