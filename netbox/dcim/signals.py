from __future__ import unicode_literals

from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import VCMembership


@receiver(post_delete, sender=VCMembership)
def delete_empty_vc(instance, **kwargs):
    """
    When the last VCMembership of a VirtualChassis has been deleted, delete the VirtualChassis as well.
    """
    pass
    # virtual_chassis = instance.virtual_chassis
    # if not VCMembership.objects.filter(virtual_chassis=virtual_chassis).exists():
    #     virtual_chassis.delete()
