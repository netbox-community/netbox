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


def validate_vm_cluster_device(instance):
    """Device must belong to the assigned cluster."""
    if instance.cluster and instance.device:
        if instance.device not in instance.cluster.devices.all():
            raise ValidationError({
                'device': _("Device {device} does not belong to cluster {cluster}.").format(
                    device=instance.device, cluster=instance.cluster
                )
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
        name='vm_primary_ips',
        model_label='virtualization.virtualmachine',
        fields=_fs({'primary_ip4', 'primary_ip6', 'oob_ip'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_vm_primary_ips,
        queries_db=True,
        description='Primary IPs must be assigned to VM interfaces',
    ),
    ModelValidator(
        name='vm_cluster_device',
        model_label='virtualization.virtualmachine',
        fields=_fs({'cluster', 'device'}),
        category=ValidatorCategory.CROSS_MODEL,
        validate=validate_vm_cluster_device,
        queries_db=True,
        description='Device must belong to the assigned cluster',
    ),
)
