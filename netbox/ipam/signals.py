from django.db.models.signals import pre_delete
from django.dispatch import receiver

from dcim.models import Device
from virtualization.models import VirtualMachine
from .models import IPAddress


@receiver(pre_delete, sender=IPAddress)
def clear_primary_ip(instance, **kwargs):
    """
    When an IPAddress is deleted, trigger save() on any Devices/VirtualMachines for which it
    was a primary IP.
    """
    field_name = f'primary_ip{instance.family}'
    device = Device.objects.filter(**{field_name: instance}).first()
    if device:
        device.save()
    virtualmachine = VirtualMachine.objects.filter(**{field_name: instance}).first()
    if virtualmachine:
        virtualmachine.save()
