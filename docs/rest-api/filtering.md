# REST API Filtering

## Filtering Objects

The objects returned by an API list endpoint can be filtered by attaching one or more query parameters to the request URL. For example, `GET /api/dcim/sites/?status=active` will return only sites with a status of "active."

Multiple parameters can be joined to further narrow results. For example, `GET /api/dcim/sites/?status=active&region=europe` will return only active sites within the Europe region.

Generally, passing multiple values for a single parameter will result in a logical OR operation. For example, `GET /api/dcim/sites/?region=north-america&region=south-america` will return sites in North America _or_ South America. However, a logical AND operation will be used in instances where a field may have multiple values, such as tags. For example, `GET /api/dcim/sites/?tag=foo&tag=bar` will return only sites which have both the "foo" _and_ "bar" tags applied.

### Filtering by Choice Field

Some models have fields which are limited to specific choices, such as the `status` field on the Prefix model. To find all available choices for this field, make an authenticated `OPTIONS` request to the model's list endpoint, and use `jq` to extract the relevant parameters:

```no-highlight
$ curl -s -X OPTIONS \
-H "Authorization: Token $TOKEN" \
-H "Content-Type: application/json" \
http://netbox/api/ipam/prefixes/ | jq ".actions.POST.status.choices"
[
  {
    "value": "container",
    "display_name": "Container"
  },
  {
    "value": "active",
    "display_name": "Active"
  },
  {
    "value": "reserved",
    "display_name": "Reserved"
  },
  {
    "value": "deprecated",
    "display_name": "Deprecated"
  }
]
```

!!! note
    The above works only if the API token used to authenticate the request has permission to make a `POST` request to this endpoint.

### Filtering by Custom Field

To filter results by a custom field value, prepend `cf_` to the custom field name. For example, the following query will return only sites where a custom field named `foo` is equal to 123:

```no-highlight
GET /api/dcim/sites/?cf_foo=123
```

Custom fields can be mixed with built-in fields to further narrow results. When creating a custom string field, the type of filtering selected (loose versus exact) determines whether partial or full matching is used.

## Lookup Expressions

Certain model fields also support filtering using additional lookup expressions. This allows
for negation and other context-specific filtering.

These lookup expressions can be applied by adding a suffix to the desired field's name, e.g. `mac_address__n`. In this case, the filter expression is for negation and it is separated by two underscores. Below are the lookup expressions that are supported across different field types.

### Numeric Fields

Numeric based fields (ASN, VLAN ID, etc) support these lookup expressions:

| Filter | Description |
|--------|-------------|
| `n` | Not equal to |
| `lt` | Less than |
| `lte` | Less than or equal to |
| `gt` | Greater than |
| `gte` | Greater than or equal to |

### String Fields

String based (char) fields (Name, Address, etc) support these lookup expressions:

| Filter | Description |
|--------|-------------|
| `n` | Not equal to |
| `ic` | Contains (case-insensitive) |
| `nic` | Does not contain (case-insensitive) |
| `isw` | Starts with (case-insensitive) |
| `nisw` | Does not start with (case-insensitive) |
| `iew` | Ends with (case-insensitive) |
| `niew` | Does not end with (case-insensitive) |
| `ie` | Exact match (case-insensitive) |
| `nie` | Inverse exact match (case-insensitive) |
| `empty` | Is empty (boolean) |

### Foreign Keys & Other Fields

Certain other fields, namely foreign key relationships support just the negation
expression: `n`.
