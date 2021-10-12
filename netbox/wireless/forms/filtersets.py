from django import forms
from django.utils.translation import gettext as _

from dcim.models import *
from extras.forms import CustomFieldModelFilterForm
from utilities.forms import BootstrapMixin, TagFilterField


class SSIDFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
    model = PowerFeed
    field_groups = [
        ['q', 'tag'],
    ]
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    tag = TagFilterField(model)
