from netbox.plugins import PluginConfig


class DummyPluginConfig(PluginConfig):
    name = 'netbox.tests.dummy_plugin'
    verbose_name = 'Dummy plugin'
    version = '0.0'
    description = 'For testing purposes only'
    base_url = 'dummy-plugin'
    min_version = '1.0'
    max_version = '9.0'
    middleware = [
        'netbox.tests.dummy_plugin.middleware.DummyMiddleware'
    ]
    queues = [
        'testing-low',
        'testing-medium',
        'testing-high'
    ]
    events_pipeline = [
        'netbox.tests.dummy_plugin.events.process_events_queue'
    ]

    def ready(self):
        super().ready()

        from . import jobs  # noqa: F401


config = DummyPluginConfig
