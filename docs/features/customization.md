# Customization

While NetBox strives to meet the needs of every network, the needs of users to cater to their own unique environments cannot be ignored. NetBox was built with this in mind, and can be customized in many ways to better suit your particular needs.

## Custom Fields

While NetBox provides a rather extensive data model out of the box, the need may arise to store certain additional data associated with NetBox objects. For example, you might need to record the invoice ID alongside an installed device, or record an approving authority when creating a new IP prefix. NetBox administrators can create custom fields on built-in objects to meet these needs.

NetBox supports many types of custom field, from basic data types like strings and integers, to complex structures like selection lists or raw JSON. It's even possible to add a custom field which references other NetBox objects. Custom field data is stored directly alongside the object to which it is applied in the database, which ensures minimal performance impact. And custom field data can be written and read via the REST API, just like built-in fields.

To learn more about this feature, check out the [custom field documentation](../customization/custom-fields.md).

## Custom Links

TODO

To learn more about this feature, check out the [custom link documentation](../customization/custom-links.md).

## Custom Validation

TODO

To learn more about this feature, check out the [custom validation documentation](../customization/custom-validation.md).

## Export Templates

TODO

To learn more about this feature, check out the [export template documentation](../customization/export-templates.md).

## Reports

TODO

To learn more about this feature, check out the [documentation for reports](../customization/reports.md).

## Custom Scripts

TODO

To learn more about this feature, check out the [documentation for custom scripts](../customization/custom-scripts.md).
