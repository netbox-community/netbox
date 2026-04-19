"""
Declarative cascade registrations for virtualization models.

Replaces imperative signal handlers in virtualization/signals.py.
"""
from netbox.cascades import CascadeMethod, CascadeSpec, CascadeTiming, cascade_registry


# ──────────────────────────────────────────────────────────────────────
# VirtualDisk save/delete → update VirtualMachine.disk aggregate
# Replaces: update_virtualmachine_disk signal handler
# ──────────────────────────────────────────────────────────────────────

def _update_vm_disk(instance, **kwargs):
    """Recompute VirtualMachine.disk from aggregate VirtualDisk sizes."""
    from django.db.models import Sum
    from virtualization.models import VirtualMachine

    vm = instance.virtual_machine
    VirtualMachine.objects.filter(pk=vm.pk).update(
        disk=vm.virtualdisks.aggregate(Sum('size'))['size__sum']
    )


cascade_registry.register(
    CascadeSpec(
        source_model='virtualization.virtualdisk',
        target_model='virtualization.virtualmachine',
        timing=CascadeTiming.POST_SAVE,
        skip_on_create=False,
        handler=_update_vm_disk,
        method=CascadeMethod.CUSTOM,
        description='Update VirtualMachine.disk aggregate when VirtualDisk is saved',
    ),
    CascadeSpec(
        source_model='virtualization.virtualdisk',
        target_model='virtualization.virtualmachine',
        timing=CascadeTiming.POST_DELETE,
        skip_on_create=False,
        handler=_update_vm_disk,
        method=CascadeMethod.CUSTOM,
        description='Update VirtualMachine.disk aggregate when VirtualDisk is deleted',
    ),
)


# ──────────────────────────────────────────────────────────────────────
# Cluster save → update VirtualMachine.site
# Replaces: update_virtualmachine_site signal handler
# ──────────────────────────────────────────────────────────────────────

cascade_registry.register(
    CascadeSpec(
        source_model='virtualization.cluster',
        target_model='virtualization.virtualmachine',
        trigger_fields=frozenset({'_site'}),
        field_mapping={'site': '_site'},
        filter_spec=lambda inst: {'cluster': inst} if inst._site else {},
        description='Propagate site to VirtualMachines when Cluster site changes',
    ),
)
