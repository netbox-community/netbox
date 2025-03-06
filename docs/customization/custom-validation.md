# Custom Validation

NetBox validates every object prior to it being written to the database to ensure data integrity. This validation includes things like checking for proper formatting and that references to related objects are valid. However, you may wish to supplement this validation with some rules of your own. For example, perhaps you require that every site's name conforms to a specific pattern.  This can be done using custom validation rules.

## Custom Validation Rules

Custom validation rules are expressed as a mapping of object attributes to a set of rules to which that attribute must conform. For example:

```json
{
  "name": {
    "min_length": 5,
    "max_length": 30
  }
}
```

This defines a custom validator which checks that the length of the `name` attribute for an object is at least five characters long, and no longer than 30 characters. This validation is executed _after_ NetBox has performed its own internal validation.

### Validation Types

The `CustomValidator` class supports several validation types:

* `min`: Minimum value
* `max`: Maximum value
* `min_length`: Minimum string length
* `max_length`: Maximum string length
* `regex`: Application of a [regular expression](https://en.wikipedia.org/wiki/Regular_expression)
* `required`: A value must be specified
* `prohibited`: A value must _not_ be specified
* `eq`: A value must be equal to the specified value
* `neq`: A value must _not_ be equal to the specified value

The `min` and `max` types should be defined for numeric values, whereas `min_length`, `max_length`, and `regex` are suitable for character strings (text values). The `required` and `prohibited` validators may be used for any field, and should be passed a value of `True`.

!!! warning
    Bear in mind that these validators merely supplement NetBox's own validation: They will not override it. For example, if a certain model field is required by NetBox, setting a validator for it with `{'prohibited': True}` will not work.

### Custom Validation Logic

There may be instances where the provided validation types are insufficient. NetBox provides a `CustomValidator` class which can be extended to enforce arbitrary validation logic by overriding its `validate()` method, and calling `fail()` when an unsatisfactory condition is detected. The `validate()` method should accept an instance (the object being saved) as well as the current request effecting the change.

```python
from extras.validators import CustomValidator

class MyValidator(CustomValidator):

    def validate(self, instance, request):
        if instance.status == 'active' and not instance.description:
            self.fail("Active sites must have a description set!", field='status')
```

The `fail()` method may optionally specify a field with which to associate the supplied error message. If specified, the error message will appear to the user as associated with this field. If omitted, the error message will not be associated with any field.

## Assigning Custom Validators

Custom validators are associated with specific NetBox models under the [CUSTOM_VALIDATORS](../configuration/data-validation.md#custom_validators) configuration parameter. There are three manners by which custom validation rules can be defined:

1. Plain JSON mapping (no custom logic)
2. Dotted path to a custom validator class
3. Direct reference to a custom validator class

### Plain Data

For cases where custom logic is not needed, it is sufficient to pass validation rules as plain JSON-compatible objects. This approach typically affords the most portability for your configuration. For instance:

```python
CUSTOM_VALIDATORS = {
    "dcim.site": [
        {
            "name": {
                "min_length": 5,
                "max_length": 30,
            }
        }
    ],
    "dcim.device": [
        {
            "platform": {
                "required": True,
            }
        }
    ]
}
```

#### Referencing Related Object Attributes

The attributes of a related object can be referenced by specifying a dotted path. For example, to reference the name of a region to which a site is assigned, use `region.name`:

```python
CUSTOM_VALIDATORS = {
    "dcim.site": [
        {
            "region.name": {
                "neq": "New York"
            }
        }
    ]
}
```

#### Validating Request Parameters

In addition to validating object attributes, custom validators can also match against parameters of the current request (where available). For example, the following rule will permit only the user named "admin" to modify an object:

```json
{
  "request.user.username": {
    "eq": "admin"
  }
}
```

!!! tip
    Custom validation should generally not be used to enforce permissions. NetBox provides a robust [object-based permissions](../administration/permissions.md) mechanism which should be used for this purpose.

### Dotted Path to Class

In instances where a custom validator class is needed, it can be referenced by its Python path (relative to NetBox's working directory):

```python
CUSTOM_VALIDATORS = {
    'dcim.site': (
        'my_validators.Validator1',
        'my_validators.Validator2',
    ),
    'dcim.device': (
        'my_validators.Validator3',
    )
}
```

### Direct Class Reference

This approach requires each class being instantiated to be imported directly within the Python configuration file.

```python
from my_validators import Validator1, Validator2, Validator3

CUSTOM_VALIDATORS = {
    'dcim.site': (
        Validator1(),
        Validator2(),
    ),
    'dcim.device': (
        Validator3(),
    )
}
```

!!! note
    Even if defining only a single validator, it must be passed as an iterable.
