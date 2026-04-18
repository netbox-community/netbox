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


validator_registry.register('ipam.iprange',
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


validator_registry.register('ipam.ipaddress',
    ModelValidator(
        name='ipaddress_unique',
        model_label='ipam.ipaddress',
        fields=_fs({'address', 'vrf'}),
        category=ValidatorCategory.UNIQUENESS,
        validate=validate_ipaddress_unique,
        queries_db=True,
        description='Duplicate IP check within VRF',
    ),
    ModelValidator(
        name='ipaddress_assigned_object',
        model_label='ipam.ipaddress',
        fields=_fs({'assigned_object_type', 'assigned_object_id'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_ipaddress_assigned_object,
        queries_db=True,
        description='Cannot reassign IP while in use as primary/OOB',
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


validator_registry.register('ipam.vlan',
    ModelValidator(
        name='vlan_vid_in_group',
        model_label='ipam.vlan',
        fields=_fs({'vid', 'group'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_vlan_vid_in_group,
        queries_db=True,
        description='VLAN VID must be within group ranges',
    ),
)

# ──────────────────────────────────────────────────────────────────────
# VLANGroup
# ──────────────────────────────────────────────────────────────────────

def validate_vlangroup_vid_ranges(instance):
    from ipam.utils import check_ranges_overlap
    if instance.vid_ranges and check_ranges_overlap(instance.vid_ranges):
        raise ValidationError({'vid_ranges': _("Ranges cannot overlap.")})


validator_registry.register('ipam.vlangroup',
    ModelValidator(
        name='vlangroup_vid_ranges',
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
