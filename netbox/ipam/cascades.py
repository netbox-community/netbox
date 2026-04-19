"""
Declarative cascade registrations for ipam models.

Replaces imperative signal handlers in ipam/signals.py.
"""
from netbox.cascades import CascadeMethod, CascadeSpec, CascadeTiming, cascade_registry


# ──────────────────────────────────────────────────────────────────────
# IPAddress delete → clear primary_ip on Device/VirtualMachine
# Replaces: clear_primary_ip signal handler
# ──────────────────────────────────────────────────────────────────────

def _clear_primary_ip(instance, **kwargs):
    """When an IPAddress is deleted, clear primary_ip4/ip6 on any Device/VM that used it."""
    from dcim.models import Device
    from virtualization.models import VirtualMachine

    field_name = f'primary_ip{instance.family}'
    if device := Device.objects.filter(**{field_name: instance}).first():
        device.snapshot()
        setattr(device, field_name, None)
        device.save()
    if vm := VirtualMachine.objects.filter(**{field_name: instance}).first():
        vm.snapshot()
        setattr(vm, field_name, None)
        vm.save()


cascade_registry.register(
    CascadeSpec(
        source_model='ipam.ipaddress',
        target_model='dcim.device',
        timing=CascadeTiming.PRE_DELETE,
        method=CascadeMethod.CUSTOM,
        handler=_clear_primary_ip,
        skip_on_create=False,
        description='Clear primary_ip4/ip6 on Device/VM when IPAddress is deleted',
    ),
)


# ──────────────────────────────────────────────────────────────────────
# IPAddress delete → clear oob_ip on Device
# Replaces: clear_oob_ip signal handler
# ──────────────────────────────────────────────────────────────────────

def _clear_oob_ip(instance, **kwargs):
    """When an IPAddress is deleted, clear oob_ip on any Device that used it."""
    from dcim.models import Device

    if device := Device.objects.filter(oob_ip=instance).first():
        device.snapshot()
        device.oob_ip = None
        device.save()


cascade_registry.register(
    CascadeSpec(
        source_model='ipam.ipaddress',
        target_model='dcim.device',
        timing=CascadeTiming.PRE_DELETE,
        method=CascadeMethod.CUSTOM,
        handler=_clear_oob_ip,
        skip_on_create=False,
        description='Clear oob_ip on Device when IPAddress is deleted',
    ),
)
