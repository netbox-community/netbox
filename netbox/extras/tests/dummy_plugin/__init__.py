from extras.plugins import PluginConfig


class DummyPluginConfig(PluginConfig):
    name = 'extras.tests.dummy_plugin'
    verbose_name = 'Dummy plugin'
    version = '0.0'
    description = 'For testing purposes only'
    base_url = 'dummy-plugin'
    middleware = [
        'extras.tests.dummy_plugin.middleware.DummyMiddleware'
    ]


config = DummyPluginConfig
