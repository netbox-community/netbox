# Config Context Profiles

Profiles can be used to organize [configuration contexts](./configcontext.md) and to enforce a desired structure for their data. The later is achieved by defining a [JSON schema](https://json-schema.org/) to which all config context with this profile assigned must comply.

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

## Fields

### Name

A unique human-friendly name.

### Schema

The JSON schema to be enforced for all assigned config contexts (optional).
