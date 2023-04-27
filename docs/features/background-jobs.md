# Background Jobs

NetBox includes the ability to execute certain functions as background tasks. These include:

* [Report](../customization/reports.md) execution
* [Custom script](../customization/custom-scripts.md) execution
* Synchronization of [remote data sources](../integrations/synchronized-data.md)

Additionally, NetBox plugins can enqueue their own background tasks. This is accomplished using the [Job model](../models/core/job.md). Background tasks are executed by the `rqworker` process(es).

## Scheduled Jobs

Background jobs can be configured to run immediately, or at a set time in the future. Scheduled jobs can also be configured to repeat at a set interval.
