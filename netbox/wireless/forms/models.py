from dcim.constants import *
from dcim.models import *
from extras.forms import CustomFieldModelForm
from extras.models import Tag
from ipam.models import VLAN
from utilities.forms import BootstrapMixin, DynamicModelChoiceField, DynamicModelMultipleChoiceField
from wireless.models import SSID

__all__ = (
    'SSIDForm',
)


class SSIDForm(BootstrapMixin, CustomFieldModelForm):
    vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = SSID
        fields = [
            'name', 'description', 'vlan', 'tags',
        ]
        fieldsets = (
            ('SSID', ('name', 'description', 'tags')),
            ('VLAN', ('vlan',)),
        )
