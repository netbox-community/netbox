# Custom Field Choice Sets

Single- and multi-selection [custom fields](../../customization/custom-fields.md) must define a set of valid choices from which the user may choose when defining the field value. These choices are defined as sets that may be reused among multiple custom fields.

A choice set must define a base choice set and/or a set of arbitrary extra choices.

## Fields

### Name

The human-friendly name of the choice set.

### Base Choices

The set of pre-defined choices to include. Available sets are listed below. This is an optional setting.

* IATA airport codes
* ISO 3166 - Two-letter country codes
* UN/LOCODE - Five-character location identifiers

### Extra Choices

A set of custom choices that will be appended to the base choice set (if any).

### Order Alphabetically

If enabled, the choices list will be automatically ordered alphabetically. If disabled, choices will appear in the order in which they were defined.
