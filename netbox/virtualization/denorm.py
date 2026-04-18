"""
Denormalization declarations for virtualization models.
"""
from netbox.denorm import DenormSpec, denorm_registry


def _vm_default_site(instance):
    """Assign site from cluster if not already set."""
    if instance.cluster and not instance.site:
        return instance.cluster._site
    return instance.site


denorm_registry.register(
    'virtualization.virtualmachine',
    DenormSpec(
        field_name='site',
        compute=_vm_default_site,
        depends_on=frozenset({'cluster', 'site'}),
    ),
)
