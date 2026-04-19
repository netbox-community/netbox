"""
Denormalization declarations for extras models.
"""
from netbox.denorm import DenormSpec, denorm_registry

# ──────────────────────────────────────────────────────────────────────
# Notification — object_repr from object
# ──────────────────────────────────────────────────────────────────────

def _notification_object_repr(instance):
    if instance.object:
        return str(instance.object)[:200]
    return instance.object_repr


denorm_registry.register(
    'extras.notification',
    DenormSpec(
        field_name='object_repr',
        compute=_notification_object_repr,
        depends_on=frozenset({'object_type', 'object_id'}),
    ),
)

# ──────────────────────────────────────────────────────────────────────
# CustomFieldChoiceSet — sort extra_choices alphabetically
# ──────────────────────────────────────────────────────────────────────

def _choiceset_sort_extra_choices(instance):
    if instance.order_alphabetically and instance.extra_choices:
        return sorted(instance.extra_choices, key=lambda x: x[0])
    return instance.extra_choices


denorm_registry.register(
    'extras.customfieldchoiceset',
    DenormSpec(
        field_name='extra_choices',
        compute=_choiceset_sort_extra_choices,
        depends_on=frozenset({'order_alphabetically', 'extra_choices'}),
    ),
)
