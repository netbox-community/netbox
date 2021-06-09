# Custom Validation

NetBox validates every object prior to it being written to the database to ensure data integrity. This validation includes things like checking for proper formatting and that references to related objects are valid. However, you may wish to supplement this validation with some rules of your own. For example, perhaps you require that every site's name conforms to a specific pattern.  This can be done using NetBox's `CustomValidator` class.

## CustomValidator

### Validation Rules

A custom validator can be instantiated by passing a mapping of attributes to a set of rules to which that attribute must conform. For example:

```python
from extras.validators import CustomValidator

CustomValidator({
    'name': {
        'min_length': 5,
        'max_length': 30,
    }
})
```

This defines a custom validator which checks that the length of the `name` attribute for an object is at least five characters long, and no longer than 30 characters. This validation is executed _after_ NetBox has performed its own internal validation.

The `CustomValidator` class supports several validation types:

* `min`: Minimum value
* `max`: Maximum value
* `min_length`: Minimum string length
* `max_length`: Maximum string length
* `regex`: Application of a [regular expression](https://en.wikipedia.org/wiki/Regular_expression)

The `min` and `max` types should be defined for numeric values, whereas `min_length`, `max_length`, and `regex` are suitable for character strings (text values).

### Custom Validation Logic

There may be instances where the provided validation types are insufficient. The `CustomValidator` class can be extended to enforce arbitrary validation logic by overriding its `validate()` method, and calling `fail()` when an unsatisfactory condition is detected.

```python
from extras.validators import CustomValidator

class MyValidator(CustomValidator):
    def validate(self, instance):
        if instance.status == 'active' and not instance.description:
            self.fail("Active sites must have a description set!", attr='status')
```

The `fail()` method may optionally specify a field with which to associate the supplied error message. If specified, the error message will appear to the user as associated with this field. If omitted, the error message will not be associated with any field.

## Assigning Custom Validators

Custom validators are associated with specific NetBox models under the [CUSTOM_VALIDATORS](../configuration/optional-settings.md#custom_validators) configuration parameter, as such:

```python
CUSTOM_VALIDATORS = {
    'dcim.site': (
        Validator1,
        Validator2,
        Validator3
    )
}
```

!!! note
    Even if defining only a single validator, it must be passed as an iterable.

When it is not necessary to define a custom `validate()` method, you may opt to pass a `CustomValidator` instance directly:

```python
from extras.validators import CustomValidator

CUSTOM_VALIDATORS = {
    'dcim.site': (
        CustomValidator({
            'name': {
                'min_length': 5,
                'max_length': 30,
            }
        }),
    )
}
```
