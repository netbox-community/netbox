# Module Type Profiles

Each [module type](./moduletype.md) may optionally be assigned a profile according to its classification. A profile can extend module types with user-configured attributes — for example, the input current and voltage of a power supply, or the clock speed and number of cores for a processor.

Module type attributes are managed by configuring a [JSON schema](https://json-schema.org/) on the profile. The schema below introduces three module type attributes, two of which are designated as required:

```json
{
    "properties": {
        "type": {
            "type": "string",
            "title": "Disk type",
            "enum": ["HD", "SSD", "NVME"],
            "default": "HD"
        },
        "capacity": {
            "type": "integer",
            "title": "Capacity (GB)",
            "description": "Gross disk size"
        },
        "speed": {
            "type": "integer",
            "title": "Speed (RPM)"
        }
    },
    "required": [
        "type", "capacity"
    ]
}
```

Both the assignment of module types to a profile and the designation of a schema for a profile are optional: a profile can be used purely as a classification mechanism if the addition of custom attributes is not needed.

## Fields

### Name

A unique name for the profile (for example, `Power Supply` or `Disk`).

### Description

An optional description of the profile.

### Schema

An optional [JSON schema](https://json-schema.org/) defining the attributes that may (or must) be set on each assigned module type. The schema must be valid JSON Schema, or else null.

### Comments

Free-form Markdown-supported notes about the profile.
