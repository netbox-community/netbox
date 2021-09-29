from django import forms

from dcim.choices import *
from dcim.constants import *

__all__ = (
    'InterfaceCommonForm',
)


class InterfaceCommonForm(forms.Form):
    mac_address = forms.CharField(
        empty_value=None,
        required=False,
        label='MAC address'
    )
    mtu = forms.IntegerField(
        required=False,
        min_value=INTERFACE_MTU_MIN,
        max_value=INTERFACE_MTU_MAX,
        label='MTU'
    )

    def clean(self):
        super().clean()

        parent_field = 'device' if 'device' in self.cleaned_data else 'virtual_machine'
        tagged_vlans = self.cleaned_data.get('tagged_vlans')

        # Untagged interfaces cannot be assigned tagged VLANs
        if self.cleaned_data['mode'] == InterfaceModeChoices.MODE_ACCESS and tagged_vlans:
            raise forms.ValidationError({
                'mode': "An access interface cannot have tagged VLANs assigned."
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
                    'tagged_vlans': f"The tagged VLANs ({', '.join(invalid_vlans)}) must belong to the same site as "
                                    f"the interface's parent device/VM, or they must be global"
                })
