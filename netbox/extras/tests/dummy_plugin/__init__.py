from extras.plugins import PluginConfig


class DummyPluginConfig(PluginConfig):
    name = 'extras.tests.dummy_plugin'
    verbose_name = 'Dummy plugin'
    version = '0.0'
    description = 'For testing purposes only'
    base_url = 'dummy-plugin'
    min_version = '1.0'
    max_version = '9.0'
    middleware = [
        'extras.tests.dummy_plugin.middleware.DummyMiddleware'
    ]
    queues = [
        'testing-low',
        'testing-medium',
        'testing-high'
    ]


config = DummyPluginConfig
