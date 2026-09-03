from netbox.plugins import PluginConfig


class DummyPluginBConfig(PluginConfig):
    name = 'netbox.tests.dummy_plugin_b'
    verbose_name = 'Dummy plugin B'
    version = '0.0'
    description = 'For testing purposes only'
    base_url = 'dummy-plugin-b'
    min_version = '1.0'
    max_version = '9.0'


config = DummyPluginBConfig
