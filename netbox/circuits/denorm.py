"""
Denormalization declarations for circuits models.
"""
from netbox.denorm import DenormSpec, denorm_registry


def _ct_provider_network(instance):
    if not instance.termination_type:
        return None
    from django.apps import apps
    if instance.termination_type.model_class() == apps.get_model('circuits', 'providernetwork'):
        return instance.termination
    return None


def _ct_region(instance):
    if not instance.termination_type:
        return None
    from django.apps import apps
    tt = instance.termination_type.model_class()
    if tt == apps.get_model('dcim', 'region'):
        return instance.termination
    elif tt == apps.get_model('dcim', 'site'):
        return getattr(instance.termination, 'region', None)
    elif tt == apps.get_model('dcim', 'location'):
        site = getattr(instance.termination, 'site', None)
        return getattr(site, 'region', None) if site else None
    return None


def _ct_site_group(instance):
    if not instance.termination_type:
        return None
    from django.apps import apps
    tt = instance.termination_type.model_class()
    if tt == apps.get_model('dcim', 'sitegroup'):
        return instance.termination
    elif tt == apps.get_model('dcim', 'site'):
        return getattr(instance.termination, 'group', None)
    elif tt == apps.get_model('dcim', 'location'):
        site = getattr(instance.termination, 'site', None)
        return getattr(site, 'group', None) if site else None
    return None


def _ct_site(instance):
    if not instance.termination_type:
        return None
    from django.apps import apps
    tt = instance.termination_type.model_class()
    if tt == apps.get_model('dcim', 'site'):
        return instance.termination
    elif tt == apps.get_model('dcim', 'location'):
        return getattr(instance.termination, 'site', None)
    return None


def _ct_location(instance):
    if not instance.termination_type:
        return None
    from django.apps import apps
    if instance.termination_type.model_class() == apps.get_model('dcim', 'location'):
        return instance.termination
    return None


denorm_registry.register(
    'circuits.circuittermination',
    DenormSpec(field_name='_provider_network', compute=_ct_provider_network,
               depends_on=frozenset({'termination_type', 'termination_id'})),
    DenormSpec(field_name='_region', compute=_ct_region,
               depends_on=frozenset({'termination_type', 'termination_id'})),
    DenormSpec(field_name='_site_group', compute=_ct_site_group,
               depends_on=frozenset({'termination_type', 'termination_id'})),
    DenormSpec(field_name='_site', compute=_ct_site,
               depends_on=frozenset({'termination_type', 'termination_id'})),
    DenormSpec(field_name='_location', compute=_ct_location,
               depends_on=frozenset({'termination_type', 'termination_id'})),
)
