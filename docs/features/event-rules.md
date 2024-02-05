# Event Rules

NetBox includes the ability to execute certain functions in response to internal object changes. These include:

* [Scripts](../customization/custom-scripts.md) execution
* [Webhooks](../integrations/webhooks.md) execution

For example, suppose you want to automatically configure a monitoring system to start monitoring a device when its operational status is changed to active, and remove it from monitoring for any other status. You can create a webhook in NetBox for the device model and craft its content and destination URL to effect the desired change on the receiving system. You can then associate an event rule with this webhook and the webhook will be sent automatically by NetBox whenever the configured constraints are met.

Each event must be associated with at least one NetBox object type and at least one event (e.g. create, update, or delete).

## Conditional Event Rules

An event rule may include a set of conditional logic expressed in JSON used to control whether an event triggers for a specific object. For example, you may wish to trigger an event for devices only when the `status` field of an object is "active":

```json
{
  "and": [
    {
      "attr": "status.value",
      "value": "active"
    }
  ]
}
```

For more detail, see the reference documentation for NetBox's [conditional logic](../reference/conditions.md).

## Event Rule Processing

When a change is detected, any resulting events are placed into a Redis queue for processing. This allows the user's request to complete without needing to wait for the outgoing event(s) to be processed. The events are then extracted from the queue by the `rqworker` process. The current event queue and any failed events can be inspected under System > Background Tasks.
