from django.apps import AppConfig


class ExtrasConfig(AppConfig):
    name = "extras"

    def ready(self):
        from netbox.event_rules import register_event_rule_action
        from netbox.models.features import register_models

        from . import dashboard, lookups, search, signals  # noqa: F401
        from .event_rules import NotificationAction, ScriptAction, WebhookAction

        # Register models
        register_models(*self.get_models())

        # Register core event rule actions
        register_event_rule_action(WebhookAction, is_plugin_provided=False)
        register_event_rule_action(ScriptAction, is_plugin_provided=False)
        register_event_rule_action(NotificationAction, is_plugin_provided=False)
