from django import forms
from django.utils.translation import gettext_lazy as _

from dcim.choices import *
from dcim.constants import *
from utilities.forms import get_field_value

__all__ = (
    'InterfaceCommonForm',
    'ModuleCommonForm'
)


class InterfaceCommonForm(forms.Form):
    mac_address = forms.CharField(
        empty_value=None,
        required=False,
        label=_('MAC address')
    )
    mtu = forms.IntegerField(
        required=False,
        min_value=INTERFACE_MTU_MIN,
        max_value=INTERFACE_MTU_MAX,
        label=_('MTU')
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

    def clean(self):
        super().clean()

        parent_field = 'device' if 'device' in self.cleaned_data else 'virtual_machine'
        tagged_vlans = self.cleaned_data.get('tagged_vlans')

        # Untagged interfaces cannot be assigned tagged VLANs
        if self.cleaned_data['mode'] == InterfaceModeChoices.MODE_ACCESS and tagged_vlans:
            raise forms.ValidationError({
                'mode': _("An access interface cannot have tagged VLANs assigned.")
            })

        # Remove all tagged VLAN assignments from "tagged all" interfaces
        elif self.cleaned_data['mode'] == InterfaceModeChoices.MODE_TAGGED_ALL:
            self.cleaned_data['tagged_vlans'] = []

        # Validate tagged VLANs; must be a global VLAN or in the same site
        elif self.cleaned_data['mode'] == InterfaceModeChoices.MODE_TAGGED and tagged_vlans:
            valid_sites = [None, self.cleaned_data[parent_field].site]
            invalid_vlans = [str(v) for v in tagged_vlans if v.site not in valid_sites]

            if invalid_vlans:
                raise forms.ValidationError({
                    'tagged_vlans': _(
                        "The tagged VLANs ({vlans}) must belong to the same site as the interface's parent device/VM, "
                        "or they must be global"
                    ).format(vlans=', '.join(invalid_vlans))
                })


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
                # Installing modules with placeholders require that the bay has a position value
                if MODULE_TOKEN in template.name and not module_bay.position:
                    raise forms.ValidationError(
                        _("Cannot install module with placeholder values in a module bay with no position defined.")
                    )

                resolved_name = template.name.replace(MODULE_TOKEN, module_bay.position)
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
