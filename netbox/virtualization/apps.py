from django.apps import AppConfig


class VirtualizationConfig(AppConfig):
    name = 'virtualization'

    def ready(self):
        from django.utils.translation import gettext as _

        from netbox.models.features import register_models
        from utilities.counters import connect_counters
        from utilities.permissions import ModelAction, register_model_actions

        from . import search, signals  # noqa: F401
        from .models import VirtualMachine

        # Register models
        register_models(*self.get_models())

        # Register counters
        connect_counters(VirtualMachine)

        # Register custom permission actions
        register_model_actions(VirtualMachine, [
            ModelAction('render_config', help_text=_('Render VM configuration')),
        ])
