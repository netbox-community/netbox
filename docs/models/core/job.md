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

The amount of time the job spent executing, calculated as the difference between its start and completion times. This is populated only once a started job has completed.

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

### Access

The job's access class, which determines which users may access the job in addition to the permissions assigned for jobs. It is set by the job runner when the job is created. Superusers can access all jobs regardless of access class.

| Value | Who can access the job |
|-------|------------------------|
| Requester | Only the user who created the job |
| Object | Only users permitted to view the job's assigned object |
| Shared | Any user permitted to view jobs |

### Data

Any data associated with the execution of the job, such as log output.

### Job ID

The job's UUID, used for unique identification within a queue.
