"""
Extracted, composable validators for virtualization models.
"""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from netbox.validators import ModelValidator, ValidatorCategory, validator_registry

_fs = frozenset


def validate_cluster_host_sites(instance):
    """Host devices must match cluster's scope site/location."""
    if not instance.pk:
        return
    from dcim.models import Device
    hosts = Device.objects.filter(cluster=instance)
    if instance._site:
        mismatched = hosts.exclude(site=instance._site)
        if mismatched.exists():
            raise ValidationError({
                'scope': _(
                    "Cannot change cluster scope; {count} host device(s) are assigned to a different site."
                ).format(count=mismatched.count())
            })
    if instance._location:
        mismatched = hosts.exclude(location=instance._location)
        if mismatched.exists():
            raise ValidationError({
                'scope': _(
                    "Cannot change cluster scope; {count} host device(s) are assigned to a different location."
                ).format(count=mismatched.count())
            })


def validate_vm_site_cluster(instance):
    if not instance.site and not instance.cluster:
        raise ValidationError({
            'cluster': _('A virtual machine must be assigned to a site and/or cluster.')
        })


def validate_vm_primary_ips(instance):
    """Primary IPs must be assigned to a VM interface."""
    for field in ('primary_ip4', 'primary_ip6', 'oob_ip'):
        ip = getattr(instance, field, None)
        if not ip:
            continue
        if not hasattr(ip, 'assigned_object') or ip.assigned_object is None:
            raise ValidationError({
                field: _("The specified IP address ({ip}) is not assigned to this VM.").format(ip=ip)
            })
        iface = ip.assigned_object
        if hasattr(iface, 'virtual_machine') and iface.virtual_machine_id == instance.pk:
            continue
        if ip.nat_inside and hasattr(ip.nat_inside, 'assigned_object'):
            inner = ip.nat_inside.assigned_object
            if hasattr(inner, 'virtual_machine') and inner.virtual_machine_id == instance.pk:
                continue
        raise ValidationError({
            field: _("The specified IP address ({ip}) is not assigned to this VM.").format(ip=ip),
        })


def validate_vm_cluster_site_consistency(instance):
    """Cluster site must match VM site."""
    if instance.cluster and instance.site and instance.cluster._site and instance.cluster._site != instance.site:
        raise ValidationError({
            'cluster': _(
                'The selected cluster ({cluster}) is not assigned to this site ({site}).'
            ).format(cluster=instance.cluster, site=instance.site)
        })


def validate_vm_device_cluster(instance):
    """Must specify cluster when assigning device; device must be in cluster."""
    if instance.device and not instance.cluster:
        raise ValidationError({
            'device': _('Must specify a cluster when assigning a host device.')
        })
    if instance.device and instance.cluster and instance.device not in instance.cluster.devices.all():
        raise ValidationError({
            'device': _(
                "The selected device ({device}) is not assigned to this cluster ({cluster})."
            ).format(device=instance.device, cluster=instance.cluster)
        })


def validate_vm_disk_aggregate(instance):
    """Disk size must match aggregate of virtual disks."""
    if instance._state.adding:
        return
    from django.db.models import Sum
    total_disk = instance.virtualdisks.aggregate(Sum('size', default=0))['size__sum']
    if total_disk and instance.disk is None:
        instance.disk = total_disk
    elif total_disk and instance.disk != total_disk:
        raise ValidationError({
            'disk': _(
                "The specified disk size ({size}) must match the aggregate size of assigned virtual disks "
                "({total_size})."
            ).format(size=instance.disk, total_size=total_disk)
        })


def validate_vm_primary_ip_family(instance):
    """Primary IP address versions must be correct."""
    for family in (4, 6):
        field = f'primary_ip{family}'
        ip = getattr(instance, field)
        if ip is not None and ip.address.version != family:
            raise ValidationError({
                field: _(
                    "Must be an IPv{family} address. ({ip} is an IPv{version} address.)"
                ).format(family=family, ip=ip, version=ip.address.version)
            })


def validate_vm_primary_ip_assignment(instance):
    """Primary IPs must be assigned to a VM interface."""
    interfaces = instance.interfaces.all() if instance.pk else None
    for family in (4, 6):
        field = f'primary_ip{family}'
        ip = getattr(instance, field)
        if ip is not None:
            if ip.assigned_object in interfaces:
                pass
            elif ip.nat_inside is not None and ip.nat_inside.assigned_object in interfaces:
                pass
            else:
                raise ValidationError({
                    field: _("The specified IP address ({ip}) is not assigned to this VM.").format(ip=ip),
                })


validator_registry.register('virtualization.cluster',
    ModelValidator(
        name='cluster_host_sites',
        model_label='virtualization.cluster',
        fields=_fs({'scope_type', 'scope_id'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_cluster_host_sites,
        queries_db=True,
        description='Host devices must match cluster scope',
    ),
)

validator_registry.register('virtualization.virtualmachine',
    ModelValidator(
        name='vm_site_cluster',
        model_label='virtualization.virtualmachine',
        fields=_fs({'site', 'cluster'}),
        category=ValidatorCategory.CROSS_FIELD,
        validate=validate_vm_site_cluster,
        description='VM must have a site and/or cluster',
    ),
    ModelValidator(
        name='vm_cluster_site_consistency',
        model_label='virtualization.virtualmachine',
        fields=_fs({'cluster', 'site'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_vm_cluster_site_consistency,
        queries_db=True,
        description='Cluster site must match VM site',
    ),
    ModelValidator(
        name='vm_device_cluster',
        model_label='virtualization.virtualmachine',
        fields=_fs({'device', 'cluster'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_vm_device_cluster,
        queries_db=True,
        description='Must have cluster when assigning device; device must be in cluster',
    ),
    ModelValidator(
        name='vm_disk_aggregate',
        model_label='virtualization.virtualmachine',
        fields=_fs({'disk'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_vm_disk_aggregate,
        queries_db=True,
        description='Disk size must match aggregate virtual disk sizes',
    ),
    ModelValidator(
        name='vm_primary_ip_family',
        model_label='virtualization.virtualmachine',
        fields=_fs({'primary_ip4', 'primary_ip6'}),
        category=ValidatorCategory.FIELD,
        validate=validate_vm_primary_ip_family,
        description='Primary IP version must match field family',
    ),
    ModelValidator(
        name='vm_primary_ip_assignment',
        model_label='virtualization.virtualmachine',
        fields=_fs({'primary_ip4', 'primary_ip6'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_vm_primary_ip_assignment,
        queries_db=True,
        description='Primary IPs must be assigned to VM interfaces',
    ),
)
