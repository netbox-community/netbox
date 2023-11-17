# EventRule

An event rule is a mechanism for taking an action (such as running a script or sending a webhook) when a change takes place in NetBox. For example, you may want to notify a monitoring system whenever the status of a device is updated in NetBox. This can be done by creating an event pointing to a webhook for the device model in NetBox and identifying the webhook receiver. When NetBox detects a change to a device, an HTTP request containing the details of the change and who made it be sent to the specified receiver.

See the [event rules documentation](../features/event-rules.md)  for more information.

## Fields

### Name

A unique human-friendly name.

### Content Types

The type(s) of object in NetBox that will trigger the webhook.

### Enabled

If not selected, the webhook will be inactive.

### Events

The events which will trigger the action. At least one event type must be selected.

| Name       | Description                          |
|------------|--------------------------------------|
| Creations  | A new object has been created        |
| Updates    | An existing object has been modified |
| Deletions  | An object has been deleted           |
| Job starts | A job for an object starts           |
| Job ends   | A job for an object terminates       |

### Conditions

A set of [prescribed conditions](../../reference/conditions.md) against which the triggering object will be evaluated. If the conditions are defined but not met by the object, the webhook will not be sent. A webhook that does not define any conditions will _always_ trigger.
