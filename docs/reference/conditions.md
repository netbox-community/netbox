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

!!! note "Missing keys and absent data"
    A condition which references a key that does not exist in the data being evaluated fails closed: the condition set evaluates as false, and (for an [event rule](../features/event-rules.md)) an error is logged to `netbox.event_rules` so that a typo does not silently disable the rule.

    Where the data is absent altogether rather than merely missing the referenced key — an event rule evaluating a job which recorded no data, say — the condition does not match. Such an absence is a normal property of the event rather than a mistake, so it is not treated as an error and does not affect the evaluation of the other conditions in the set. Because there is nothing to compare against, the condition does not match whatever the operator, and remains a non-match when `negate` is set: no rule fires on data an event never carried.

    A snapshot which does not exist for the event type is the exception: it resolves to `null`, so that a condition can distinguish (for example) a newly created object from an updated one. See [below](#snapshot-conditions-event-rules).

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

!!! info "This feature was introduced in NetBox v4.7."

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

An attribute which resolves in neither snapshot — a misspelling, an attribute the object type does not have, or an event which recorded no snapshots at all — leaves nothing to compare. The condition fails closed (the rule does not fire) and an error is logged to `netbox.event_rules`. This holds regardless of `negate`: negating a condition whose attribute cannot be resolved does not turn it into a match.

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
    Snapshot data uses the **model serializer format**, not the REST API format. Choice fields such as `status` are stored as raw strings (e.g. `"active"`) rather than nested objects (e.g. `{"value": "active", "label": "Active"}`). Use `status` — not `status.value` — when referencing a snapshot attribute, both in `snapshots.prechange.*`/`snapshots.postchange.*` paths and with the `changed`/`unchanged` operators. A `.value` suffix cannot be resolved against a snapshot: the condition fails closed (the rule does not fire) and an error is logged to `netbox.event_rules`.

!!! note "Snapshot availability"
    For create events, `prechange` is `null`. The `changed` operator evaluates to `true` for any attribute present in the postchange snapshot (each field transitioned from non-existent to its initial value), and a `snapshots.prechange.*` path resolves to `null` — so it matches a condition testing for `null` and fails any other comparison.

    For delete events, `postchange` is `null`. The `changed` operator evaluates to `true` for any attribute present in the prechange snapshot, `unchanged` evaluates to `false`, and a `snapshots.postchange.*` path resolves to `null`.

    An absent snapshot excuses only the absence of the data, not a path which does not describe it. The attribute path is checked against the opposite snapshot, and fails closed (the rule does not fire, and an error is logged) if it cannot be resolved there — whether because it cannot be resolved against a snapshot at all, such as the `.value` suffix above, or because the attribute is misspelled or unknown. Otherwise a typo would resolve to `null` and fire the rule on every create or delete.

    To test only whether a snapshot is absent, reference the snapshot itself rather than an attribute of it: `{"attr": "snapshots.prechange", "value": null}`.

Because an absent snapshot resolves to `null` rather than raising an error — matching a condition testing for `null` and failing any other comparison, whichever operator is used — a snapshot path can be combined safely with other conditions in a rule that also fires on create or delete. For example, this rule fires when a site is created, or when a site whose status was previously `planned` is updated:

```json
{
  "or": [
    {
      "attr": "snapshots.prechange.status",
      "value": null
    },
    {
      "attr": "snapshots.prechange.status",
      "value": "planned"
    }
  ]
}
```

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
