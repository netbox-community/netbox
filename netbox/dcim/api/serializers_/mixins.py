from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils.translation import gettext as _
from netaddr import EUI, AddrFormatError
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

_UNSET = object()

__all__ = (
    '_UNSET',
    'MACAddressShortcutMixin',
)


class MACAddressShortcutMixin:
    """
    Mixin for Interface and VMInterface serializers that adds a `mac_address` shortcut field for
    creating/updating the primary MACAddress in a single request. The validated write is centralized
    on the interface model (BaseInterface.set_primary_mac_address); this mixin is a thin adapter that
    owns the permission check, the shortcut-vs-primary_mac_address conflict guard, and translating the
    model's validation errors into API errors.
    """

    @staticmethod
    def _validate_no_mac_conflict(data, mac_address):
        # The mac_address shortcut and the primary_mac_address field both set the primary MAC. Reject
        # only when both are supplied AND they disagree, so a read-modify-write round-trip (which echoes
        # both readable fields with matching values) is accepted while a genuine conflict is rejected.
        if mac_address is _UNSET or not isinstance(data, dict) or 'primary_mac_address' not in data:
            return

        primary = data['primary_mac_address']
        primary_value = primary.mac_address if primary is not None else None
        try:
            shortcut_value = EUI(mac_address, version=48) if mac_address is not None else None
        except (AddrFormatError, ValueError, TypeError):
            # Leave an invalid shortcut value to the format check in each serializer's validate().
            return

        if shortcut_value != primary_value:
            raise serializers.ValidationError(
                _("The provided 'mac_address' and 'primary_mac_address' values conflict.")
            )

    def _check_add_mac_permission(self, instance, mac_address):
        # A submitted value that doesn't already exist on this interface will be created, which requires
        # add_macaddress. An existing value is only reassigned, so it doesn't.
        if instance is not None and instance.mac_addresses.filter(mac_address=mac_address).exists():
            return
        request = self.context.get('request')
        if request and not request.user.has_perm('dcim.add_macaddress'):
            raise PermissionDenied(_('You do not have permission to create MAC addresses.'))

    def create(self, validated_data):
        mac_address = validated_data.pop('mac_address', None)
        if mac_address is not None:
            self._check_add_mac_permission(None, mac_address)
        with transaction.atomic():
            instance = super().create(validated_data)
            if mac_address is not None:
                self._set_primary_mac(instance, mac_address)
        return instance

    def update(self, instance, validated_data):
        mac_address = validated_data.pop('mac_address', _UNSET)
        if mac_address not in (_UNSET, None):
            self._check_add_mac_permission(instance, mac_address)
        with transaction.atomic():
            instance = super().update(instance, validated_data)
            if mac_address is not _UNSET:
                self._set_primary_mac(instance, mac_address)
        return instance

    def _set_primary_mac(self, instance, mac_address):
        # Surface model/custom validation raised by the centralized operation as a DRF 400 rather than
        # a 500 (it runs after DRF's own validation phase). The viewset's discard_events_on_rollback()
        # clears any event queued for the rolled-back interface save.
        try:
            instance.set_primary_mac_address_from_value(mac_address)
        except DjangoValidationError as e:
            # Field-scoped errors (e.g. an interface-level check like qinq_svlan) keep their field key;
            # non-field errors are attributed to the mac_address shortcut that triggered the operation.
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(e.message_dict)
            raise serializers.ValidationError({'mac_address': e.messages})
