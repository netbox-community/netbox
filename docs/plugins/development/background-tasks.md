# Background Tasks

NetBox supports the queuing of tasks that need to be performed in the background, decoupled from the request-response cycle, using the [Python RQ](https://python-rq.org/) library. Three task queues of differing priority are defined by default:

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
