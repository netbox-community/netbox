# API Filtering

The NetBox API supports robust filtering of results based on the fields of each model.
Generally speaking you are able to filter based on the attributes (fields) present in
the response body. Please note however that certain read-only or metadata fields are not
filterable.

Filtering is achieved by passing HTTP query parameters and the parameter name is the
name of the field you wish to filter on and the value is the field value.

E.g. filtering based on a device's name:
```
/api/dcim/devices/?name=DC-SPINE-1
```

## Multi Value Logic

While you are able to filter based on an arbitrary number of fields, you are also able to
pass multiple values for the same field. In most cases filtering on multiple values is
implemented as a logical OR operation. A notible exception is the `tag` filter which
is a logical AND. Passing multiple values for one field, can be combined with other fields.

For example, filtering for devices with either the name of DC-SPINE-1 _or_ DC-LEAF-4:
```
/api/dcim/devices/?name=DC-SPINE-1&name=DC-LEAF-4
```

Filtering for devices with tag `router` and `customer-a` will return only devices with
_both_ of those tags applied:
```
/api/dcim/devices/?tag=router&tag=customer-a
```

## Lookup Expressions

Certain model fields also support filtering using additonal lookup expressions. This allows
for negation and other context specific filtering.

These lookup expressions can be applied by adding a suffix to the desired field's name.
E.g. `mac_address__n`. In this case, the filter expression is for negation and it is seperated
by two underscores. Below are the lookup expressions that are supported across different field
types.

### Numeric Fields

Numeric based fields (ASN, VLAN ID, etc) support these lookup expressions:

- `n` - not equal (negation)
- `lt` - less than
- `lte` - less than or equal
- `gt` - greater than
- `gte` - greater than or equal

### String Fields

String based (char) fields (Name, Address, etc) support these lookup expressions:

- `n` - not equal (negation)
- `ic` - case insensitive contains
- `nic` - negated case insensitive contains
- `isw` - case insensitive starts with
- `nisw` - negated case insensitive starts with
- `iew` - case insensitive ends with
- `niew` - negated case insensitive ends with
- `ie` - case sensitive exact match
- `nie` - negated case sensitive exact match

### Foreign Keys & Other Fields

Certain other fields, namely foreign key relationships support just the negation
expression: `n`.
