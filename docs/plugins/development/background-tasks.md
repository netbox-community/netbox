# Background Tasks

NetBox supports the queuing of tasks that need to be performed in the background, decoupled from the request-response cycle.

## High level API

NetBox provides an easy-to-use interface for programming and managing different types of jobs. In general, there are different types of jobs that can be used to perform any kind of background task. Due to inheritance, the general job logic remains the same, but each of them fulfills a specific task and has its own management logic around it.

### Background Job

A background job implements a basic [Job](../../models/core/job.md) executor for all kinds of tasks. It has logic implemented to handle the management of the associated job object, rescheduling of periodic jobs in the given interval and error handling. Adding custom jobs is done by subclassing NetBox's `BackgroundJob` class.

#### Example

```python title="jobs.py"
from utilities.jobs import BackgroundJob

class MyTestJob(BackgroundJob):
    class Meta:
        name = "My Test Job"

    def run(self, *args, **kwargs):
        obj = self.job.object
        # your logic goes here
```

You can schedule the background job from within your code (e.g. from a model's `save()` method or a view) by calling `MyTestJob.enqueue()`. This method passes through all arguments to `Job.enqueue()`. However, no `name` argument must be passed, as the background job name will be used instead.

::: core.models.Job.enqueue

#### Job Attributes

Background job attributes are defined under a class named `Meta` within the job. These are optional, but encouraged.

##### `name`

This is the human-friendly names of your background job. If omitted, the class name will be used.

### Scheduled Jobs

As described above, jobs can be scheduled for immediate execution or at any later time using the `enqueue()` method. However, for management purposes, the `enqueue_once()` method allows a job to be scheduled exactly once avoiding duplicates. If a job is already scheduled for a particular instance, a second one won't be scheduled, respecting thread safety. An example use case would be to schedule a periodic task that is bound to an instance in general, but not to any event of that instance (such as updates). The parameters of the `enqueue_once()` method are identical to those of `enqueue()`.

!!! tip
    It is not forbidden to `enqueue()` additional jobs while an interval schedule is active. An example use of this would be to schedule a periodic daily synchronization, but also trigger additional synchronizations on demand when the user presses a button.

### System Jobs

A system background job is not bound to any particular NetBox object. A typical use case for these jobs is a general synchronization of NetBox objects from another system or housekeeping.

The `setup()` method can be used to set up a new scheduled job outside the request-response cycle. It can be safely called from the plugin's ready function and will register the new schedule right after all plugins are loaded and the database is connected.

!!! note
    The default system background job queue is `low`. It can be changed using the [`QUEUE_MAPPINGS`](../../configuration/miscellaneous.md#queue_mappings) setting when using `None` as model.

#### Example

```python title="jobs.py"
from utilities.jobs import BackgroundJob

class MyHousekeepingJob(BackgroundJob):
    class Meta:
        name = "Housekeeping"

    def run(self, *args, **kwargs):
        # your logic goes here
```
```python title="__init__.py"
from netbox.plugins import PluginConfig

class MyPluginConfig(PluginConfig):
    def ready(self):
        from .jobs import MyHousekeepingJob
        MyHousekeepingJob.setup(interval=60)
```

## Low Level API

Instead of using the high-level APIs provided by NetBox, plugins may access the task scheduler directly using the [Python RQ](https://python-rq.org/) library. This allows scheduling background tasks without the need to add [Job](../../models/core/job.md) to the database or implementing custom job handling.

## Task queues

Three task queues of differing priority are defined by default:

* High
* Default
* Low

Any tasks in the "high" queue are completed before the default queue is checked, and any tasks in the default queue are completed before those in the "low" queue.

Plugins can also add custom queues for their own needs by setting the `queues` attribute under the PluginConfig class. An example is included below:

```python
class MyPluginConfig(PluginConfig):
    name = 'myplugin'
    ...
    queues = [
        'foo',
        'bar',
    ]
```

The PluginConfig above creates two custom queues with the following names `my_plugin.foo` and `my_plugin.bar`. (The plugin's name is prepended to each queue to avoid conflicts between plugins.)

!!! warning "Configuring the RQ worker process"
    By default, NetBox's RQ worker process only services the high, default, and low queues. Plugins which introduce custom queues should advise users to either reconfigure the default worker, or run a dedicated worker specifying the necessary queues. For example:
    
    ```
    python manage.py rqworker my_plugin.foo my_plugin.bar
    ```
