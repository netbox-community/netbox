# Background Jobs

NetBox includes the ability to execute certain functions as background tasks. These include:

* [Custom script](../customization/custom-scripts.md) execution
* Synchronization of [remote data sources](../integrations/synchronized-data.md)
* Housekeeping tasks

Additionally, NetBox plugins can enqueue their own background tasks. This is accomplished using the [Job model](../models/core/job.md). Background tasks are executed by the `rqworker` process(es).

## Job Access

Each job has an access class, which determines who may access it in addition to the permissions assigned for jobs:

* **Requester** - Only the user who created the job. Jobs for background REST API bulk operations and background UI operations use this class.
* **Object** - Only users permitted to view the job's assigned object. For example, the results of a custom script are visible only to users permitted to view the script, and those of a data source synchronization only to users permitted to view the data source.
* **Shared** - Any user permitted to view jobs. Housekeeping and other system jobs use this class.

Superusers can access all jobs regardless of access class. The access class applies to every action, so only superusers can view or delete another user's requester jobs, even if permitted to delete jobs. (Housekeeping still purges all jobs under [`JOB_RETENTION`](../configuration/miscellaneous.md#job_retention).)

## Scheduled Jobs

Background jobs can be configured to run immediately, or at a set time in the future. Scheduled jobs can also be configured to repeat at a set interval.
