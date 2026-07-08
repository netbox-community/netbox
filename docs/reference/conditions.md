# Conditions

Conditions are NetBox's mechanism for evaluating whether a set data meets a prescribed set of conditions. It allows the author to convey simple logic by declaring an arbitrary number of attribute-value-operation tuples nested within a hierarchy of logical AND and OR statements.

## Conditions

A condition is expressed as a JSON object with the following keys:

| Key name | Required | Default | Description |
|----------|----------|---------|-------------|
| attr     | Yes      | -       | Name of the key within the data being evaluated |
| value    | See note | -       | The reference value to which the given data will be compared. Not used by snapshot operators (`changed`, `unchanged`). |
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
* `regex`: Matches a regular expression
* `changed`: The attribute's value differs between the pre-change and post-change snapshots (no `value` required)
* `unchanged`: The attribute's value is the same in both snapshots (no `value` required)

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
  "attr": "status.value",
  "value": ["planned", "staging"],
  "op": "in",
  "negate": true
}
```

!!! note "Evaluating static choice fields"
    Pay close attention when evaluating static choice fields, such as the `status` field above. These fields typically render as a dictionary specifying both the field's raw value (`value`) and its human-friendly label (`label`). Be sure to specify on which of these you want to match.

## Snapshot Conditions (Event Rules)

When used in an [event rule](../features/event-rules.md), conditions can also inspect the **pre-change and post-change snapshots** captured at the time of the event. This allows rules to fire only when a specific field actually changes value, rather than whenever it has a particular value.

### Snapshot Operators

The `changed` and `unchanged` operators compare an attribute's value across the two snapshots. They do not accept a `value` key.

Fire only when `status` changes (to any value):

```json
{
  "attr": "status",
  "op": "changed"
}
```

### Combining with Standard Conditions

The canonical use case — fire only when `status` changes **to** `active` — combines a standard value check with the `changed` operator:

```json
{
  "and": [
    {
      "attr": "status.value",
      "value": "active"
    },
    {
      "attr": "status",
      "op": "changed"
    }
  ]
}
```

### Direct Snapshot Path Access

You can also read pre- or post-change values directly using the `snapshots.prechange.<attr>` and `snapshots.postchange.<attr>` dot-path syntax with any standard operator:

```json
{
  "attr": "snapshots.prechange.status",
  "value": "planned"
}
```

!!! warning "Snapshot serialization format"
    Snapshot data uses the **model serializer format**, not the REST API format. Choice fields such as `status` are stored as raw strings (e.g. `"active"`) rather than nested objects (e.g. `{"value": "active", "label": "Active"}`). Use `attr: "snapshots.prechange.status"` — not `"snapshots.prechange.status.value"` — when referencing snapshot attributes. The `changed`/`unchanged` operators compare the same format on both sides, so they are not affected by this distinction.

!!! note "Snapshot availability"
    Snapshots are only populated for update and delete events. For create events, `prechange` is `null` — conditions using the `changed` operator on a create event evaluate to `true` (the field transitioned from non-existent to its initial value), while conditions using `snapshots.prechange.*` paths evaluate to `false`. For delete events, `postchange` is `null` — the `changed` operator evaluates to `true` for any attribute present in the prechange snapshot, and `unchanged` evaluates to `false`.

## Condition Sets

Multiple conditions can be combined into nested sets using AND or OR logic. This is done by declaring a JSON object with a single key (`and` or `or`) containing a list of condition objects and/or child condition sets.

### Examples

`status` is "active" and `primary_ip4` is defined _or_ the "exempt" tag is applied.

```json
{
  "or": [
    {
      "and": [
        {
          "attr": "status.value",
          "value": "active"
        },
        {
          "attr": "primary_ip4",
          "value": null,
          "negate": true
        }
      ]
    },
    {
      "attr": "tags.slug",
      "value": "exempt",
      "op": "contains"
    }
  ]
}
```
