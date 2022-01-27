# Background Tasks

By default, Netbox provides 3 differents [RQ](https://python-rq.org/) queues to run background jobs : *high*, *default* and *low*.
These 3 core queues can be used out-of-the-box by plugins to define background tasks.

Plugins can also define dedicated queues. These queues can be configured under the PluginConfig class `queues` attribute. An example configuration
is below:

```python
class MyPluginConfig(PluginConfig):
    name = 'myplugin'
    ...
    queues = [
        'queue1',
        'queue2',
        'queue-whatever-the-name'
    ]
```

The PluginConfig above creates 3 queues with the following names: *myplugin.queue1*, *myplugin.queue2*, *myplugin.queue-whatever-the-name*.
As you can see, the queue's name is always preprended with the plugin's name, to avoid any name clashes between different plugins.

In case you create dedicated queues for your plugin, it is strongly advised to also create a dedicated RQ worker instance. This instance should only listen to the queues defined in your plugin - to avoid impact between your background tasks and netbox internal tasks.

```
python manage.py rqworker myplugin.queue1 myplugin.queue2 myplugin.queue-whatever-the-name
```
