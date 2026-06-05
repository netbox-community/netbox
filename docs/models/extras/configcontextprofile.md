# Config Context Profiles

Profiles can be used to organize [configuration contexts](./configcontext.md) and to enforce a desired structure for their data. The latter is achieved by defining a [JSON schema](https://json-schema.org/) to which all config contexts assigned to the profile must comply. Any context whose data fails validation against the profile's schema cannot be saved.

For example, the following schema defines two keys, `size` and `priority`, of which the former is required:

```json
{
    "properties": {
        "size": {
            "type": "integer"
        },
        "priority": {
            "type": "string",
            "enum": ["high", "medium", "low"],
            "default": "medium"
        }
    },
    "required": [
        "size"
    ]
}
```

A profile's schema may also be populated from a [data source](../core/datasource.md), enabling the schema to be maintained externally (for example, in a git repository) and synchronized into NetBox.

## Fields

### Name

A unique, human-friendly name for the profile.

### Description

An optional description of the profile's purpose.

### Schema

An optional [JSON schema](https://json-schema.org/) document. When set, the schema is enforced for every config context assigned to this profile. Leaving the schema blank allows the profile to be used purely as an organizational grouping.

### Data Source / Data File / Data Path

Optional pointers to a remote [data source](../core/datasource.md) and file from which the schema is populated. When configured, the schema field is overwritten on synchronization.

### Auto Sync Enabled

When set, the profile's schema is automatically refreshed whenever the upstream data file is updated.
