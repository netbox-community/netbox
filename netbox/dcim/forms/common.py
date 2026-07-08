from django import forms
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from netaddr import EUI, AddrFormatError

from dcim.choices import *
from dcim.constants import *
from dcim.models import MACAddress
from dcim.utils import get_module_bay_positions, resolve_module_placeholder
from netbox.context import current_request
from utilities.forms import get_field_value

__all__ = (
    'InterfaceCommonForm',
    'ModuleCommonForm'
)


class InterfaceCommonForm(forms.Form):
    mtu = forms.IntegerField(
        required=False,
        min_value=INTERFACE_MTU_MIN,
        max_value=INTERFACE_MTU_MAX,
        label=_('MTU')
    )
    mac_address = forms.CharField(
        required=False,
        empty_value=None,
        label=_('MAC address'),
        help_text=_('Enter a MAC address to create and assign it as the primary MAC in one step.')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Determine the selected 802.1Q mode
        interface_mode = get_field_value(self, 'mode')

        # Delete VLAN tagging fields which are not relevant for the selected mode
        if interface_mode in (InterfaceModeChoices.MODE_ACCESS, InterfaceModeChoices.MODE_TAGGED_ALL):
            del self.fields['tagged_vlans']
        elif not interface_mode:
            del self.fields['vlan_group']
            del self.fields['untagged_vlan']
            del self.fields['tagged_vlans']
        if interface_mode != InterfaceModeChoices.MODE_Q_IN_Q:
            del self.fields['qinq_svlan']

        if self.instance and self.instance.pk and self.instance.primary_mac_address:
            # Pre-populate mac_address with the current primary MAC string so it round-trips cleanly
            self.fields['mac_address'].initial = str(self.instance.primary_mac_address.mac_address)

    def clean(self):
        super().clean()

        mac_address = self.cleaned_data.get('mac_address')
        if mac_address:
            try:
                EUI(mac_address, version=48)
            except (AddrFormatError, ValueError, TypeError):
                raise forms.ValidationError({
                    'mac_address': _('Enter a valid MAC address (e.g. 00:11:22:33:44:55).')
                })
            # Require add_macaddress permission when a MAC value is provided (it may need to be created).
            request = current_request.get()
            if request is not None and not request.user.has_perm('dcim.add_macaddress'):
                raise forms.ValidationError({
                    'mac_address': _('You do not have permission to create MAC addresses.')
                })
        parent_field = 'device' if 'device' in self.cleaned_data else 'virtual_machine'
        if 'tagged_vlans' in self.fields.keys():
            tagged_vlans = self.cleaned_data.get('tagged_vlans') if self.is_bound else \
                self.get_initial_for_field(self.fields['tagged_vlans'], 'tagged_vlans')
        else:
            tagged_vlans = []

        # Validate tagged VLANs; must be a global VLAN or in the same site
        if self.cleaned_data['mode'] == InterfaceModeChoices.MODE_TAGGED and tagged_vlans:
            valid_sites = [None, self.cleaned_data[parent_field].site]
            invalid_vlans = [str(v) for v in tagged_vlans if v.site not in valid_sites]

            if invalid_vlans:
                raise forms.ValidationError({
                    'tagged_vlans': _(
                        "The tagged VLANs ({vlans}) must belong to the same site as the interface's parent device/VM, "
                        "or they must be global"
                    ).format(vlans=', '.join(invalid_vlans))
                })
        # Validate mode change
        if self.instance.pk and (self.instance.mode != self.cleaned_data['mode']):
            if 'untagged_vlan' not in self.cleaned_data and self.instance.untagged_vlan is not None:
                self.instance.untagged_vlan = None
            if 'tagged_vlans' not in self.cleaned_data and self.instance.tagged_vlans is not None:
                self.instance.tagged_vlans.clear()

    def save(self, commit=True):
        instance = super().save(commit=commit)

        if not commit or 'mac_address' not in self.changed_data:
            return instance

        mac_address = self.cleaned_data.get('mac_address')

        with transaction.atomic():
            if mac_address:
                # Find an existing MACAddress on this interface with the target value, or create one.
                # Using find-or-create avoids duplicating a MAC that already exists on this interface.
                mac = instance.mac_addresses.filter(mac_address=mac_address).first()
                if mac is None:
                    mac = MACAddress(mac_address=mac_address, assigned_object=instance)
                    mac.save()
                if instance.primary_mac_address_id != mac.pk:
                    instance.snapshot()
                    instance.primary_mac_address = mac
                    instance.save()
            else:
                if instance.primary_mac_address_id is not None:
                    instance.snapshot()
                    instance.primary_mac_address = None
                    instance.save()

        instance.__dict__.pop('mac_address', None)
        return instance


class ModuleCommonForm(forms.Form):

    def clean(self):
        super().clean()

        replicate_components = self.cleaned_data.get('replicate_components')
        adopt_components = self.cleaned_data.get('adopt_components')
        device = self.cleaned_data.get('device')
        module_type = self.cleaned_data.get('module_type')
        module_bay = self.cleaned_data.get('module_bay')

        if adopt_components:
            self.instance._adopt_components = True

        # Bail out if we are not installing a new module or if we are not replicating components (or if
        # validation has already failed)
        if self.errors or self.instance.pk or not replicate_components:
            self.instance._disable_replication = True
            return

        positions = get_module_bay_positions(module_bay)

        for templates, component_attribute in [
                ("consoleporttemplates", "consoleports"),
                ("consoleserverporttemplates", "consoleserverports"),
                ("interfacetemplates", "interfaces"),
                ("powerporttemplates", "powerports"),
                ("poweroutlettemplates", "poweroutlets"),
                ("rearporttemplates", "rearports"),
                ("frontporttemplates", "frontports")
        ]:
            # Prefetch installed components
            installed_components = {
                component.name: component for component in getattr(device, component_attribute).all()
            }

            # Get the templates for the module type.
            for template in getattr(module_type, templates).all():
                resolved_name = template.name
                if MODULE_TOKEN in template.name:
                    if not module_bay.position:
                        raise forms.ValidationError(
                            _("Cannot install module with placeholder values in a module bay with no position defined.")
                        )
                    try:
                        resolved_name = resolve_module_placeholder(template.name, positions)
                    except ValueError as e:
                        raise forms.ValidationError(str(e))

                existing_item = installed_components.get(resolved_name)

                # It is not possible to adopt components already belonging to a module
                if adopt_components and existing_item and existing_item.module:
                    raise forms.ValidationError(
                        _("Cannot adopt {model} {name} as it already belongs to a module").format(
                            model=template.component_model.__name__,
                            name=resolved_name
                        )
                    )

                # If we are not adopting components we error if the component exists
                if not adopt_components and resolved_name in installed_components:
                    raise forms.ValidationError(
                        _("A {model} named {name} already exists").format(
                            model=template.component_model.__name__,
                            name=resolved_name
                        )
                    )
