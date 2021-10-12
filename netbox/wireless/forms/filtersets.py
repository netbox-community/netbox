from django import forms
from django.utils.translation import gettext as _

from extras.forms import CustomFieldModelFilterForm
from utilities.forms import BootstrapMixin, TagFilterField
from .models import WirelessLAN


class WirelessLANFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
    model = WirelessLAN
    field_groups = [
        ['q', 'tag'],
    ]
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    tag = TagFilterField(model)
