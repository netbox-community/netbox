"""
Validators for ipam models.

Original field-level validators are preserved below. Composable model-level
validators for the validator registry follow.
"""
from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator, RegexValidator
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from netbox.validators import ModelValidator, ValidatorCategory, validator_registry

_fs = frozenset


# ──────────────────────────────────────────────────────────────────────
# Original field-level validators (from upstream NetBox)
# ──────────────────────────────────────────────────────────────────────

def prefix_validator(prefix):
    if prefix.ip != prefix.cidr.ip:
        raise ValidationError(
            _("{prefix} is not a valid prefix. Did you mean {suggested}?").format(
                prefix=prefix, suggested=prefix.cidr
            )
        )


class MaxPrefixLengthValidator(BaseValidator):
    message = _('The prefix length must be less than or equal to %(limit_value)s.')
    code = 'max_prefix_length'

    def compare(self, a, b):
        return a.prefixlen > b


class MinPrefixLengthValidator(BaseValidator):
    message = _('The prefix length must be greater than or equal to %(limit_value)s.')
    code = 'min_prefix_length'

    def compare(self, a, b):
        return a.prefixlen < b


DNSValidator = RegexValidator(
    regex=r'^([0-9A-Za-z_-]+|\*)(\.[0-9A-Za-z_-]+)*\.?$',
    message=_('Only alphanumeric characters, asterisks, hyphens, periods, and underscores are allowed in DNS names'),
    code='invalid'
)


# ──────────────────────────────────────────────────────────────────────
# Composable model-level validators (Phase 3)
# ──────────────────────────────────────────────────────────────────────


# ──────────────────────────────────────────────────────────────────────
# Aggregate
# ──────────────────────────────────────────────────────────────────────

def validate_aggregate_mask(instance):
    if instance.prefix and instance.prefix.prefixlen == 0:
        raise ValidationError({
            'prefix': _("Cannot create aggregate with /0 mask.")
        })


def validate_aggregate_no_overlap(instance):
    """Aggregates cannot overlap each other."""
    if not instance.prefix:
        return
    from ipam.models import Aggregate
    covering = Aggregate.objects.filter(
        prefix__net_contains_or_equals=str(instance.prefix)
    )
    if instance.pk:
        covering = covering.exclude(pk=instance.pk)
    if covering.exists():
        raise ValidationError({
            'prefix': _(
                "Aggregates cannot overlap. {prefix} is already covered by an existing aggregate ({aggregate})."
            ).format(prefix=instance.prefix, aggregate=covering[0])
        })

    covered = Aggregate.objects.filter(prefix__net_contained=str(instance.prefix))
    if instance.pk:
        covered = covered.exclude(pk=instance.pk)
    if covered.exists():
        raise ValidationError({
            'prefix': _(
                "Prefixes cannot overlap aggregates. {prefix} covers an existing aggregate ({aggregate})."
            ).format(prefix=instance.prefix, aggregate=covered[0])
        })


validator_registry.register('ipam.aggregate',
    ModelValidator(
        name='aggregate_mask',
        model_label='ipam.aggregate',
        fields=_fs({'prefix'}),
        category=ValidatorCategory.FIELD,
        validate=validate_aggregate_mask,
        description='Aggregate cannot use /0 mask',
    ),
    ModelValidator(
        name='aggregate_no_overlap',
        model_label='ipam.aggregate',
        fields=_fs({'prefix'}),
        category=ValidatorCategory.UNIQUENESS,
        validate=validate_aggregate_no_overlap,
        queries_db=True,
        description='Aggregates cannot overlap or cover each other',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# Prefix
# ──────────────────────────────────────────────────────────────────────

def validate_prefix_mask(instance):
    if instance.prefix and instance.prefix.prefixlen == 0:
        raise ValidationError({
            'prefix': _("Cannot create prefix with /0 mask.")
        })


def validate_prefix_unique(instance):
    """Enforce unique prefix in VRF if configured."""
    if not instance.prefix:
        return
    from netbox.config import get_config
    if (instance.vrf is None and get_config().ENFORCE_GLOBAL_UNIQUE) or \
       (instance.vrf and instance.vrf.enforce_unique):
        duplicate_prefixes = instance.get_duplicates()
        if duplicate_prefixes:
            table = _("VRF {vrf}").format(vrf=instance.vrf) if instance.vrf else _("global table")
            raise ValidationError({
                'prefix': _("Duplicate prefix found in {table}: {prefix}").format(
                    table=table, prefix=duplicate_prefixes.first(),
                )
            })


validator_registry.register('ipam.prefix',
    ModelValidator(
        name='prefix_mask',
        model_label='ipam.prefix',
        fields=_fs({'prefix'}),
        category=ValidatorCategory.FIELD,
        validate=validate_prefix_mask,
        description='Prefix cannot use /0 mask',
    ),
    ModelValidator(
        name='prefix_unique',
        model_label='ipam.prefix',
        fields=_fs({'prefix', 'vrf'}),
        category=ValidatorCategory.UNIQUENESS,
        validate=validate_prefix_unique,
        queries_db=True,
        description='Duplicate prefix check within VRF',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# IPRange
# ──────────────────────────────────────────────────────────────────────

def validate_iprange_family(instance):
    if instance.start_address and instance.end_address:
        if instance.start_address.version != instance.end_address.version:
            raise ValidationError({
                'end_address': _("Starting and ending IP address must both be IPv4 or IPv6")
            })


def validate_iprange_order(instance):
    if instance.start_address and instance.end_address:
        if not instance.end_address > instance.start_address:
            raise ValidationError({
                'end_address': _(
                    "Ending address must be greater than the starting address ({start_address})"
                ).format(start_address=instance.start_address)
            })


def validate_iprange_max_size(instance):
    if instance.start_address and instance.end_address:
        MAX_SIZE = 2 ** 32 - 1
        if int(instance.end_address.ip - instance.start_address.ip) + 1 > MAX_SIZE:
            raise ValidationError(
                _("Defined range exceeds maximum supported size ({max_size})").format(max_size=MAX_SIZE)
            )


def validate_iprange_no_overlap(instance):
    """IP ranges cannot overlap within the same VRF."""
    if not (instance.start_address and instance.end_address):
        return
    from ipam.models import IPRange
    overlapping = (
        IPRange.objects.exclude(pk=instance.pk)
        .filter(vrf=instance.vrf)
        .filter(
            Q(
                start_address__host__inet__gte=instance.start_address.ip,
                start_address__host__inet__lte=instance.end_address.ip,
            ) |
            Q(
                end_address__host__inet__gte=instance.start_address.ip,
                end_address__host__inet__lte=instance.end_address.ip,
            ) |
            Q(
                start_address__host__inet__lte=instance.start_address.ip,
                end_address__host__inet__gte=instance.end_address.ip,
            )
        )
    )
    if overlapping.exists():
        raise ValidationError(
            _("Defined addresses overlap with range {overlapping_range} in VRF {vrf}").format(
                overlapping_range=overlapping.first(), vrf=instance.vrf
            ))


def validate_iprange_prefix_match(instance):
    if instance.start_address and instance.end_address:
        if instance.start_address.prefixlen != instance.end_address.prefixlen:
            raise ValidationError({
                'end_address': _("Starting and ending IP address masks must match")
            })


validator_registry.register('ipam.iprange',
    ModelValidator(
        name='iprange_prefix_match',
        model_label='ipam.iprange',
        fields=_fs({'start_address', 'end_address'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_iprange_prefix_match,
        description='Start and end address masks must match',
    ),
    ModelValidator(
        name='iprange_family',
        model_label='ipam.iprange',
        fields=_fs({'start_address', 'end_address'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_iprange_family,
        description='Start and end address must be same family',
    ),
    ModelValidator(
        name='iprange_order',
        model_label='ipam.iprange',
        fields=_fs({'start_address', 'end_address'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_iprange_order,
        description='End address must be greater than start',
    ),
    ModelValidator(
        name='iprange_max_size',
        model_label='ipam.iprange',
        fields=_fs({'start_address', 'end_address'}),
        category=ValidatorCategory.FIELD,
        validate=validate_iprange_max_size,
        description='Range cannot exceed max size',
    ),
    ModelValidator(
        name='iprange_no_overlap',
        model_label='ipam.iprange',
        fields=_fs({'start_address', 'end_address', 'vrf'}),
        category=ValidatorCategory.UNIQUENESS,
        validate=validate_iprange_no_overlap,
        queries_db=True,
        description='IP ranges cannot overlap within same VRF',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# IPAddress
# ──────────────────────────────────────────────────────────────────────

def validate_ipaddress_unique(instance):
    """Enforce unique IPs within VRF if configured."""
    if not instance.address:
        return
    from netbox.config import get_config
    if (instance.vrf is None and get_config().ENFORCE_GLOBAL_UNIQUE) or \
       (instance.vrf and instance.vrf.enforce_unique):
        duplicate_ips = instance.get_duplicates()
        if duplicate_ips:
            table = _("VRF {vrf}").format(vrf=instance.vrf) if instance.vrf else _("global table")
            raise ValidationError({
                'address': _("Duplicate IP address found in {table}: {ip}").format(
                    table=table, ip=duplicate_ips.first(),
                )
            })


def validate_ipaddress_assigned_object(instance):
    """IP cannot be reassigned while used as primary/OOB."""
    if not instance.pk or not instance.assigned_object_id:
        return
    original_assigned_type = instance._original_assigned_object_type_id
    original_assigned_id = instance._original_assigned_object_id
    if not original_assigned_type or not original_assigned_id:
        return
    if (instance.assigned_object_type_id == original_assigned_type and
            instance.assigned_object_id == original_assigned_id):
        return
    from dcim.models import Device
    from virtualization.models import VirtualMachine
    for model in (Device, VirtualMachine):
        for field in ('primary_ip4', 'primary_ip6', 'oob_ip'):
            if not hasattr(model, field):
                continue
            try:
                model.objects.get(**{field: instance.pk})
                raise ValidationError({
                    'assigned_object': _(
                        "Cannot reassign IP address while in use as a primary/OOB IP."
                    )
                })
            except model.DoesNotExist:
                pass


def validate_ipaddress_mask(instance):
    if instance.address and instance.address.prefixlen == 0:
        raise ValidationError({'address': _("Cannot create IP address with /0 mask.")})


def validate_ipaddress_network_broadcast(instance):
    """Cannot assign network ID or broadcast address to an interface."""
    if not instance.address or not instance.assigned_object:
        return
    if instance.address.ip == instance.address.network:
        msg = _("{ip} is a network ID, which may not be assigned to an interface.").format(ip=instance.address.ip)
        if instance.address.version == 4 and instance.address.prefixlen not in (31, 32):
            raise ValidationError(msg)
        if instance.address.version == 6 and instance.address.prefixlen not in (127, 128):
            raise ValidationError(msg)
    if (instance.address.version == 4 and instance.address.ip == instance.address.broadcast and
            instance.address.prefixlen not in (31, 32)):
        raise ValidationError(
            _("{ip} is a broadcast address, which may not be assigned to an interface.").format(ip=instance.address.ip)
        )


def validate_ipaddress_unique_with_roles(instance):
    """Enforce unique IP space, with exception for non-unique roles."""
    if not instance.address:
        return
    from ipam.constants import IPADDRESS_ROLES_NONUNIQUE
    from netbox.config import get_config
    if (instance.vrf is None and get_config().ENFORCE_GLOBAL_UNIQUE) or (instance.vrf and instance.vrf.enforce_unique):
        duplicate_ips = instance.get_duplicates()
        if duplicate_ips and (
                instance.role not in IPADDRESS_ROLES_NONUNIQUE or
                any(dip.role not in IPADDRESS_ROLES_NONUNIQUE for dip in duplicate_ips)
        ):
            table = _("VRF {vrf}").format(vrf=instance.vrf) if instance.vrf else _("global table")
            raise ValidationError({
                'address': _("Duplicate IP address found in {table}: {ipaddress}").format(
                    table=table, ipaddress=duplicate_ips.first(),
                )
            })


def validate_ipaddress_in_populated_range(instance):
    """Disallow creating IPs inside a range with mark_populated=True."""
    if instance.pk or not instance.address:
        return
    from ipam.models import IPRange
    parent_range_qs = IPRange.objects.filter(
        start_address__lte=instance.address,
        end_address__gte=instance.address,
        vrf=instance.vrf,
        mark_populated=True
    )
    if parent_range := parent_range_qs.first():
        raise ValidationError({
            'address': _(
                "Cannot create IP address {ip} inside range {range}."
            ).format(ip=instance.address, range=parent_range)
        })


def validate_ipaddress_primary_reassignment(instance):
    """Cannot reassign IP while it is primary or OOB for a parent."""
    if not instance._original_assigned_object_id or not instance._original_assigned_object_type_id:
        return
    from django.contrib.contenttypes.models import ContentType
    parent = getattr(instance.assigned_object, 'parent_object', None)
    ct = ContentType.objects.get_for_id(instance._original_assigned_object_type_id)
    original_assigned_object = ct.get_object_for_this_type(pk=instance._original_assigned_object_id)
    original_parent = getattr(original_assigned_object, 'parent_object', None)

    is_primary = False
    if instance.family == 4 and hasattr(original_parent, 'primary_ip4'):
        if original_parent.primary_ip4_id == instance.pk:
            is_primary = True
    if instance.family == 6 and hasattr(original_parent, 'primary_ip6'):
        if original_parent.primary_ip6_id == instance.pk:
            is_primary = True

    if is_primary and (parent != original_parent):
        raise ValidationError(
            _("Cannot reassign IP address while it is designated as the primary IP for the parent object")
        )

    if hasattr(original_parent, 'oob_ip') and original_parent.oob_ip_id == instance.pk:
        if parent != original_parent:
            raise ValidationError(
                _("Cannot reassign IP address while it is designated as the OOB IP for the parent object")
            )


def validate_ipaddress_slaac_status(instance):
    from ipam.choices import IPAddressStatusChoices
    if instance.status == IPAddressStatusChoices.STATUS_SLAAC and instance.family != 6:
        raise ValidationError({
            'status': _("Only IPv6 addresses can be assigned SLAAC status")
        })


validator_registry.register('ipam.ipaddress',
    ModelValidator(
        name='ipaddress_mask',
        model_label='ipam.ipaddress',
        fields=_fs({'address'}),
        category=ValidatorCategory.FIELD,
        validate=validate_ipaddress_mask,
        description='IP address cannot use /0 mask',
    ),
    ModelValidator(
        name='ipaddress_network_broadcast',
        model_label='ipam.ipaddress',
        fields=_fs({'address', 'assigned_object_type', 'assigned_object_id'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_ipaddress_network_broadcast,
        description='Network ID and broadcast address cannot be assigned to interfaces',
    ),
    ModelValidator(
        name='ipaddress_unique_with_roles',
        model_label='ipam.ipaddress',
        fields=_fs({'address', 'vrf', 'role'}),
        category=ValidatorCategory.UNIQUENESS,
        validate=validate_ipaddress_unique_with_roles,
        queries_db=True,
        description='Duplicate IP check within VRF with role exceptions',
    ),
    ModelValidator(
        name='ipaddress_in_populated_range',
        model_label='ipam.ipaddress',
        fields=_fs({'address', 'vrf'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_ipaddress_in_populated_range,
        queries_db=True,
        description='Cannot create IP inside a populated IP range',
    ),
    ModelValidator(
        name='ipaddress_primary_reassignment',
        model_label='ipam.ipaddress',
        fields=_fs({'assigned_object_type', 'assigned_object_id'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_ipaddress_primary_reassignment,
        queries_db=True,
        description='Cannot reassign IP while in use as primary/OOB',
    ),
    ModelValidator(
        name='ipaddress_slaac_status',
        model_label='ipam.ipaddress',
        fields=_fs({'status'}),
        category=ValidatorCategory.FIELD,
        validate=validate_ipaddress_slaac_status,
        description='SLAAC status only for IPv6',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# VLAN
# ──────────────────────────────────────────────────────────────────────

def validate_vlan_vid_in_group(instance):
    """VLAN VID must be within the group's allowed ranges."""
    if instance.group and instance.vid:
        if instance.vid not in instance.group.get_available_vids():
            from ipam.models import VLAN
            if not VLAN.objects.filter(pk=instance.pk, group=instance.group, vid=instance.vid).exists():
                raise ValidationError({
                    'vid': _(
                        "VID {vid} is not allowed in VLAN group {group}."
                    ).format(vid=instance.vid, group=instance.group)
                })


def validate_vlan_group_site(instance):
    """VLAN assigned to group and site must be consistent."""
    from django.contrib.contenttypes.models import ContentType
    from dcim.models import Site, SiteGroup
    if instance.group and instance.site and instance.group.scope_type == ContentType.objects.get_for_model(Site):
        if instance.site != instance.group.scope:
            raise ValidationError(
                _(
                    "VLAN is assigned to group {group} (scope: {scope}); cannot also assign to site {site}."
                ).format(group=instance.group, scope=instance.group.scope, site=instance.site)
            )
    if instance.group and instance.site and instance.group.scope_type == ContentType.objects.get_for_model(SiteGroup):
        if instance.site not in instance.group.scope.sites.all():
            raise ValidationError(
                _(
                    "The assigned site {site} is not a member of the assigned group {group} (scope: {scope})."
                ).format(group=instance.group, scope=instance.group.scope, site=instance.site)
            )


def validate_vlan_vid_in_group_ranges(instance):
    """VLAN VID must fall within the group's configured VID ranges."""
    if instance.group:
        from utilities.data import ranges_to_string
        if not any([instance.vid in r for r in instance.group.vid_ranges]):
            raise ValidationError({
                'vid': _(
                    "VID must be in ranges {ranges} for VLANs in group {group}"
                ).format(ranges=ranges_to_string(instance.group.vid_ranges), group=instance.group)
            })


def validate_vlan_qinq(instance):
    from ipam.choices import VLANQinQRoleChoices
    if instance.qinq_svlan and instance.qinq_role != VLANQinQRoleChoices.ROLE_CUSTOMER:
        raise ValidationError({
            'qinq_svlan': _("Only Q-in-Q customer VLANs maybe assigned to a service VLAN.")
        })
    if instance.qinq_role == VLANQinQRoleChoices.ROLE_CUSTOMER and not instance.qinq_svlan:
        raise ValidationError({
            'qinq_role': _("A Q-in-Q customer VLAN must be assigned to a service VLAN.")
        })


validator_registry.register('ipam.vlan',
    ModelValidator(
        name='vlan_group_site',
        model_label='ipam.vlan',
        fields=_fs({'group', 'site'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_vlan_group_site,
        queries_db=True,
        description='VLAN group scope must be consistent with assigned site',
    ),
    ModelValidator(
        name='vlan_vid_in_group_ranges',
        model_label='ipam.vlan',
        fields=_fs({'vid', 'group'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_vlan_vid_in_group_ranges,
        queries_db=True,
        description='VLAN VID must be within group VID ranges',
    ),
    ModelValidator(
        name='vlan_qinq',
        model_label='ipam.vlan',
        fields=_fs({'qinq_svlan', 'qinq_role'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_vlan_qinq,
        description='Q-in-Q role and SVLAN assignment consistency',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# VLANGroup
# ──────────────────────────────────────────────────────────────────────

def validate_vlangroup_vid_ranges(instance):
    from utilities.data import check_ranges_overlap
    if instance.vid_ranges and check_ranges_overlap(instance.vid_ranges):
        raise ValidationError({'vid_ranges': _("Ranges cannot overlap.")})


def validate_vlangroup_scope(instance):
    if instance.scope_type and not instance.scope_id:
        raise ValidationError(_("Cannot set scope_type without scope_id."))
    if instance.scope_id and not instance.scope_type:
        raise ValidationError(_("Cannot set scope_id without scope_type."))


def validate_vlangroup_vid_range_bounds(instance):
    """VID range boundaries must be within min/max and properly ordered."""
    from ipam.constants import VLAN_VID_MIN, VLAN_VID_MAX
    for vid_range in instance.vid_ranges:
        lower_vid = vid_range.lower if vid_range.lower_inc else vid_range.lower + 1
        upper_vid = vid_range.upper if vid_range.upper_inc else vid_range.upper - 1
        if lower_vid < VLAN_VID_MIN:
            raise ValidationError({
                'vid_ranges': _("Starting VLAN ID in range ({value}) cannot be less than {minimum}").format(
                    value=lower_vid, minimum=VLAN_VID_MIN
                )
            })
        if upper_vid > VLAN_VID_MAX:
            raise ValidationError({
                'vid_ranges': _("Ending VLAN ID in range ({value}) cannot exceed {maximum}").format(
                    value=upper_vid, maximum=VLAN_VID_MAX
                )
            })
        if lower_vid > upper_vid:
            raise ValidationError({
                'vid_ranges': _(
                    "Ending VLAN ID in range must be greater than or equal to the starting VLAN ID ({range})"
                ).format(range=f'{lower_vid}-{upper_vid}')
            })


validator_registry.register('ipam.vlangroup',
    ModelValidator(
        name='vlangroup_scope',
        model_label='ipam.vlangroup',
        fields=_fs({'scope_type', 'scope_id'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_vlangroup_scope,
        description='Scope type and scope ID must both be set or unset',
    ),
    ModelValidator(
        name='vlangroup_vid_range_bounds',
        model_label='ipam.vlangroup',
        fields=_fs({'vid_ranges'}),
        category=ValidatorCategory.FIELD,
        validate=validate_vlangroup_vid_range_bounds,
        description='VID range boundaries must be valid and ordered',
    ),
    ModelValidator(
        name='vlangroup_vid_ranges_overlap',
        model_label='ipam.vlangroup',
        fields=_fs({'vid_ranges'}),
        category=ValidatorCategory.FIELD,
        validate=validate_vlangroup_vid_ranges,
        description='VID ranges cannot overlap',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# ASNRange
# ──────────────────────────────────────────────────────────────────────

def validate_asnrange_order(instance):
    if instance.start and instance.end:
        if instance.end < instance.start:
            raise ValidationError({
                'end': _("Ending ASN must be greater than or equal to starting ASN.")
            })


validator_registry.register('ipam.asnrange',
    ModelValidator(
        name='asnrange_order',
        model_label='ipam.asnrange',
        fields=_fs({'start', 'end'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_asnrange_order,
        description='End ASN must be >= start ASN',
    ),
)
