from collections import defaultdict

from django.core.checks import Tags, Warning, register

from netbox.event_rules import get_event_rule_action

from .models import EventRule

__all__ = (
    'check_event_rule_actions',
)


@register(Tags.models)
def check_event_rule_actions(app_configs, **kwargs):
    """
    Warn about any EventRules whose action_type is not currently registered (e.g. because the
    plugin which provides it is not installed).
    """
    warnings = []
    unavailable = defaultdict(list)

    for event_rule in EventRule.objects.only('id', 'name', 'action_type'):
        if get_event_rule_action(event_rule.action_type) is None:
            unavailable[event_rule.action_type].append(event_rule.name)

    for action_type, names in unavailable.items():
        shown_names = ", ".join(names[:10])
        if len(names) > 10:
            shown_names += f", and {len(names) - 10} more"
        warnings.append(
            Warning(
                f'{len(names)} event rule(s) reference the unregistered action type "{action_type}": '
                f'{shown_names}',
                hint='Install/enable the plugin providing this action type, or update the affected event rule(s).',
                id='extras.W001',
            )
        )

    return warnings
