from django.db import transaction
from django.utils.translation import gettext as _
from rest_framework.exceptions import PermissionDenied

from dcim.models import MACAddress

_UNSET = object()

__all__ = (
    '_UNSET',
    'MACAddressShortcutMixin',
)


class MACAddressShortcutMixin:
    """
    Mixin for Interface and VMInterface serializers that adds a write-only `mac_address` shortcut
    field for creating/updating the primary MACAddress in a single request.
    """

    def create(self, validated_data):
        mac_address = validated_data.pop('mac_address', None)
        if mac_address is not None:
            request = self.context.get('request')
            if request and not request.user.has_perm('dcim.add_macaddress'):
                raise PermissionDenied(_('You do not have permission to create MAC addresses.'))
        with transaction.atomic():
            instance = super().create(validated_data)
            if mac_address is not None:
                mac = MACAddress.objects.create(mac_address=mac_address, assigned_object=instance)
                instance.primary_mac_address = mac
                instance.save()
                instance.__dict__.pop('mac_address', None)
        return instance

    def update(self, instance, validated_data):
        mac_address = validated_data.pop('mac_address', _UNSET)

        # Check permission and locate any existing MAC before any writes.
        if mac_address not in (_UNSET, None):
            existing_mac = instance.mac_addresses.filter(mac_address=mac_address).first()
            if existing_mac is None:
                request = self.context.get('request')
                if request and not request.user.has_perm('dcim.add_macaddress'):
                    raise PermissionDenied(_('You do not have permission to create MAC addresses.'))
        else:
            existing_mac = None

        with transaction.atomic():
            instance = super().update(instance, validated_data)
            if mac_address is _UNSET:
                pass
            elif mac_address is None:
                if instance.primary_mac_address_id is not None:
                    instance.snapshot()
                    instance.primary_mac_address = None
                    instance.save()
            else:
                # Find-or-create: prefer existing MAC on this interface; create only if absent.
                mac = existing_mac
                if mac is None:
                    mac = MACAddress.objects.create(mac_address=mac_address, assigned_object=instance)
                if instance.primary_mac_address_id != mac.pk:
                    instance.snapshot()
                    instance.primary_mac_address = mac
                    instance.save()

        instance.__dict__.pop('mac_address', None)
        return instance
