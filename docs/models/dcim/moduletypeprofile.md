# Module Type Profiles

Each [module type](./moduletype.md) may optionally be assigned a profile according to its classification. A profile can extend module types with user-configured attributes. For example, you might want to specify the input current and voltage of a power supply, or the clock speed and number of cores for a processor.

Module type attributes are managed via the configuration of a [JSON schema](https://json-schema.org/) on the profile. For example, the following schema introduces three module type attributes, two of which are designated as required attributes.

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

The assignment of module types to a profile is optional. The designation of a schema for a profile is also optional: A profile can be used simply as a mechanism for classifying module types if the addition of custom attributes is not needed.

## Fields

### Schema

This field holds the [JSON schema](https://json-schema.org/) for the profile. The configured JSON schema must be valid (or the field must be null).
