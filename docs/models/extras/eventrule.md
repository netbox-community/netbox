# EventRule

An event rule is a mechanism for automatically taking an action (such as running a script or sending a webhook) in response to an event in NetBox. For example, you may want to notify a monitoring system whenever the status of a device is updated in NetBox. This can be done by creating an event for device objects and designating a webhook to be transmitted. When NetBox detects a change to a device, an HTTP request containing the details of the change and who made it be sent to the specified receiver.

See the [event rules documentation](../../features/event-rules.md)  for more information.

## Fields

### Name

A unique human-friendly name.

### Content Types

The type(s) of object in NetBox that will trigger the rule.

### Enabled

If not selected, the event rule will not be processed.

### Events

The events which will trigger the rule. At least one event type must be selected.

| Name       | Description                          |
|------------|--------------------------------------|
| Creations  | A new object has been created        |
| Updates    | An existing object has been modified |
| Deletions  | An object has been deleted           |
| Job starts | A job for an object starts           |
| Job ends   | A job for an object terminates       |

### Conditions

A set of [prescribed conditions](../../reference/conditions.md) against which the triggering object will be evaluated. If the conditions are defined but not met by the object, no action will be taken. An event rule that does not define any conditions will _always_ trigger.
