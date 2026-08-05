# Jobs

The Job model is used to schedule and record the execution of [background tasks](../../features/background-jobs.md).

## Fields

### Name

The name or other identifier of the NetBox object with which the job is associated.

## Object Type

The type of object (model) associated with this job.

### Created

The date and time at which the job itself was created.

### Scheduled

The date and time at which the job is/was scheduled to execute (if not submitted for immediate execution at the time of creation).

### Interval

The interval (in minutes) at which a scheduled job should re-execute.

### Completed

The date and time at which the job completed (if complete).

### Execution Time

The amount of time the job spent executing, calculated as the difference between its start and completion times. This is populated only once a started job has completed; while a job is still running, NetBox displays the time elapsed since it started instead.

!!! warning "The duration property is deprecated"
    The job model's `duration` property, which returned a preformatted string such as `5 minutes, 3.00 seconds`, has been **deprecated** and is planned for removal in NetBox v5.0. Export templates and plugins should reference `elapsed_time` instead, which returns a duration rather than a string and which also reports progress for a job that is still running.

!!! note "Filtering and sorting behave differently"
    Filtering on execution time matches only the recorded value, so a job which is still running is never returned: it has no execution time yet. Sorting the jobs list by the **Execution Time** column instead orders by the value displayed, which for a running job is the time elapsed so far. A long-running job therefore appears near the top when sorting in descending order, but is excluded by a filter on the same attribute. Exports likewise carry only the recorded value, in seconds.

### User

The user who created the job.

### Status

The job's current status. Potential values include:

| Value | Description |
|-------|-------------|
| Pending | Awaiting execution by an RQ worker process |
| Scheduled | Scheduled for a future date/time |
| Running | Currently executing |
| Completed | Successfully completed |
| Failed | The job did not complete successfully |
| Errored | An unexpected error was encountered during execution |

### Data

Any data associated with the execution of the job, such as log output.

### Job ID

The job's UUID, used for unique identification within a queue.
