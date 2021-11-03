# Conditions

Conditions are NetBox's mechanism for evaluating whether a set data meets a prescribed set of conditions. It allows the author to convey simple logic by declaring an arbitrary number of attribute-value-operation tuples nested within a hierarchy of logical AND and OR statements.

## Conditions

A condition is expressed as a JSON object with the following keys:

| Key name | Required | Default | Description |
|----------|----------|---------|-------------|
| attr     | Yes      | -       | Name of the key within the data being evaluated |
| value    | Yes      | -       | The reference value to which the given data will be compared |
| op       | No       | `eq`    | The logical operation to be performed |
| negate   | No       | False   | Negate (invert) the result of the condition's evaluation |

### Available Operations

* `eq`: Equals
* `gt`: Greater than
* `gte`: Greater than or equal to
* `lt`: Less than
* `lte`: Less than or equal to
* `in`: Is present within a list of values
* `contains`: Contains the specified value

### Accessing Nested Keys

To access nested keys, use dots to denote the path to the desired attribute. For example, assume the following data:

```json
{
  "a": {
    "b": {
      "c": 123
    }
  }
}
```

The following condition will evaluate as true:

```json
{
  "attr": "a.b.c",
  "value": 123
}
```

### Examples

`name` equals "foo":

```json
{
  "attr": "name",
  "value": "foo"
}
```

`name` does not equal "foo"

```json
{
  "attr": "name",
  "value": "foo",
  "negate": true
}
```

`asn` is greater than 65000:

```json
{
  "attr": "asn",
  "value": 65000,
  "op": "gt"
}
```

`status` is not "planned" or "staging":

```json
{
  "attr": "status",
  "value": ["planned", "staging"],
  "op": "in",
  "negate": true
}
```

## Condition Sets

Multiple conditions can be combined into nested sets using AND or OR logic. This is done by declaring a JSON object with a single key (`and` or `or`) containing a list of condition objects and/or child condition sets.

### Examples

`status` is "active" and `primary_ip` is defined _or_ the "exempt" tag is applied.

```json
{
  "or": [
    {
      "and": [
        {
          "attr": "status",
          "value": "active"
        },
        {
          "attr": "primary_ip",
          "value": "",
          "negate": true
        }
      ]
    },
    {
      "attr": "tags",
      "value": "exempt",
      "op": "contains"
    }
  ]
}
```
