# EventRule

An event rule is a mechanism for automatically taking an action (such as running a script or sending a webhook) in response to an event in NetBox. For example, you may want to notify a monitoring system whenever the status of a device is updated in NetBox. This can be done by creating an event for device objects and designating a webhook to be transmitted. When NetBox detects a change to a device, an HTTP request containing the details of the change and who made it be sent to the specified receiver.

See the [event rules documentation](../../features/event-rules.md)  for more information.

## Fields

### Name

A unique human-friendly name.

### Object Types

The type(s) of object in NetBox that will trigger the rule.

### Enabled

If not selected, the event rule will not be processed.

### Events Types

The event types which will trigger the rule. At least one event type must be selected.

| Name           | Description                                 |
|----------------|---------------------------------------------|
| Object created | A new object has been created               |
| Object updated | An existing object has been modified        |
| Object deleted | An object has been deleted                  |
| Job started    | A background job is initiated               |
| Job completed  | A background job completes successfully     |
| Job failed     | A background job fails                      |
| Job errored    | A background job is aborted due to an error |

!!! tip "Custom Event Types"
    The above list includes only built-in event types. NetBox plugins can also register their own custom event types.

### Conditions

A set of [prescribed conditions](../../reference/conditions.md) against which the triggering object will be evaluated. If the conditions are defined but not met by the object, no action will be taken. An event rule that does not define any conditions will _always_ trigger.

### Action Type

The type of action to take when the rule triggers. This must be one of the following choices:

* Webhook
* Custom script
* Notification

### Action Data

An optional dictionary of JSON data to pass when executing the rule. This can be useful to include additional context data, e.g. when transmitting a webhook.
