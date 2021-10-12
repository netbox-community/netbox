from extras.forms import CustomFieldModelCSVForm
from ipam.models import VLAN
from utilities.forms import CSVModelChoiceField
from wireless.models import SSID

__all__ = (
    'SSIDCSVForm',
)


class SSIDCSVForm(CustomFieldModelCSVForm):
    vlan = CSVModelChoiceField(
        queryset=VLAN.objects.all(),
        to_field_name='name',
        help_text='Bridged VLAN'
    )

    class Meta:
        model = SSID
        fields = ('name', 'description', 'vlan')
