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
        if interface_mode != InterfaceModeChoices.MODE_Q_IN_Q:
            del self.fields['qinq_svlan']

        if self.instance and self.instance.pk:
            filter_name = f'{self._meta.model._meta.model_name}_id'
            self.fields['primary_mac_address'].widget.add_query_param(filter_name, self.instance.pk)

    def clean(self):
        super().clean()
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


class ModuleCommonForm(forms.Form):

    def _get_module_bay_tree(self, module_bay):
        module_bays = []
        while module_bay:
            module_bays.append(module_bay)
            if module_bay.module:
                module_bay = module_bay.module.module_bay
            else:
                module_bay = None

        module_bays.reverse()
        return module_bays

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

        module_bays = self._get_module_bay_tree(module_bay)

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
                # Installing modules with placeholders require that the bay has a position value
                if MODULE_TOKEN in template.name:
                    if not module_bay.position:
                        raise forms.ValidationError(
                            _("Cannot install module with placeholder values in a module bay with no position defined.")
                        )

                    if len(module_bays) != template.name.count(MODULE_TOKEN):
                        raise forms.ValidationError(
                            _(
                                "Cannot install module with placeholder values in a module bay tree {level} in tree "
                                "but {tokens} placeholders given."
                            ).format(
                                level=len(module_bays), tokens=template.name.count(MODULE_TOKEN)
                            )
                        )

                    for module_bay in module_bays:
                        resolved_name = resolved_name.replace(MODULE_TOKEN, module_bay.position, 1)

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
