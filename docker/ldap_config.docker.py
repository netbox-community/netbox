from .configuration import read_configurations

_loaded_configurations = read_configurations(
    config_dir="/etc/netbox/config/ldap/",
    config_module="netbox.configuration.ldap",
    main_config="ldap_config",
)


def __getattr__(name):
    for config in _loaded_configurations:
        try:
            return getattr(config, name)
        except:
            pass
    raise AttributeError


def __dir__():
    names = []
    for config in _loaded_configurations:
        names.extend(config.__dir__())
    return names
