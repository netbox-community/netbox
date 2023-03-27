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
