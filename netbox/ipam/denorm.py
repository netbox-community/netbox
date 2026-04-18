"""
Denormalization declarations for ipam models.
"""
from netbox.denorm import DenormSpec, denorm_registry

# ──────────────────────────────────────────────────────────────────────
# Prefix — scope cache (via CachedScopeMixin) + CIDR normalization
# ──────────────────────────────────────────────────────────────────────

def _prefix_scope_region(instance):
    if not instance.scope_type:
        return None
    from django.apps import apps
    scope_model = instance.scope_type.model_class()
    if scope_model == apps.get_model('dcim', 'region'):
        return instance.scope
    elif scope_model == apps.get_model('dcim', 'site'):
        return getattr(instance.scope, 'region', None)
    elif scope_model == apps.get_model('dcim', 'location'):
        site = getattr(instance.scope, 'site', None)
        return getattr(site, 'region', None) if site else None
    return None


def _prefix_scope_site_group(instance):
    if not instance.scope_type:
        return None
    from django.apps import apps
    scope_model = instance.scope_type.model_class()
    if scope_model == apps.get_model('dcim', 'sitegroup'):
        return instance.scope
    elif scope_model == apps.get_model('dcim', 'site'):
        return getattr(instance.scope, 'group', None)
    elif scope_model == apps.get_model('dcim', 'location'):
        site = getattr(instance.scope, 'site', None)
        return getattr(site, 'group', None) if site else None
    return None


def _prefix_scope_site(instance):
    if not instance.scope_type:
        return None
    from django.apps import apps
    scope_model = instance.scope_type.model_class()
    if scope_model == apps.get_model('dcim', 'site'):
        return instance.scope
    elif scope_model == apps.get_model('dcim', 'location'):
        return getattr(instance.scope, 'site', None)
    return None


def _prefix_scope_location(instance):
    if not instance.scope_type:
        return None
    from django.apps import apps
    scope_model = instance.scope_type.model_class()
    if scope_model == apps.get_model('dcim', 'location'):
        return instance.scope
    return None


# Register scope cache for all CachedScopeMixin models
_scope_specs = [
    DenormSpec(field_name='_region', compute=_prefix_scope_region,
               depends_on=frozenset({'scope_type', 'scope_id'})),
    DenormSpec(field_name='_site_group', compute=_prefix_scope_site_group,
               depends_on=frozenset({'scope_type', 'scope_id'})),
    DenormSpec(field_name='_site', compute=_prefix_scope_site,
               depends_on=frozenset({'scope_type', 'scope_id'})),
    DenormSpec(field_name='_location', compute=_prefix_scope_location,
               depends_on=frozenset({'scope_type', 'scope_id'})),
]

for model_label in ['ipam.prefix', 'virtualization.cluster', 'wireless.wirelesslan']:
    denorm_registry.register(model_label, *_scope_specs)

# ──────────────────────────────────────────────────────────────────────
# IPRange — size from start/end
# ──────────────────────────────────────────────────────────────────────

denorm_registry.register(
    'ipam.iprange',
    DenormSpec(
        field_name='size',
        compute=lambda inst: int(inst.end_address.ip - inst.start_address.ip) + 1,
        depends_on=frozenset({'start_address', 'end_address'}),
    ),
)

# ──────────────────────────────────────────────────────────────────────
# VLANGroup — _total_vlan_ids from vid_ranges
# ──────────────────────────────────────────────────────────────────────

def _vlangroup_total_ids(instance):
    total = 0
    if instance.vid_ranges:
        for vid_range in instance.vid_ranges:
            total += vid_range.upper - vid_range.lower
    return total


denorm_registry.register(
    'ipam.vlangroup',
    DenormSpec(
        field_name='_total_vlan_ids',
        compute=_vlangroup_total_ids,
        depends_on=frozenset({'vid_ranges'}),
    ),
)

# ──────────────────────────────────────────────────────────────────────
# IPAddress — dns_name lowercase
# ──────────────────────────────────────────────────────────────────────

denorm_registry.register(
    'ipam.ipaddress',
    DenormSpec(
        field_name='dns_name',
        compute=lambda inst: inst.dns_name.lower() if inst.dns_name else '',
        depends_on=frozenset({'dns_name'}),
    ),
)

# ──────────────────────────────────────────────────────────────────────
# Prefix — CIDR normalization
# ──────────────────────────────────────────────────────────────────────

def _prefix_normalize_cidr(instance):
    import netaddr
    if isinstance(instance.prefix, netaddr.IPNetwork):
        return instance.prefix.cidr
    return instance.prefix


denorm_registry.register(
    'ipam.prefix',
    DenormSpec(
        field_name='prefix',
        compute=_prefix_normalize_cidr,
        depends_on=frozenset({'prefix'}),
    ),
)
