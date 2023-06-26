from django import forms

from users.models import *
from django.utils.translation import gettext as _
from netbox.forms import NetBoxModelImportForm
from utilities.forms import BootstrapMixin
from utilities.forms.fields import CSVChoiceField, CSVModelChoiceField, SlugField

__all__ = (
    'GroupImportForm',
)


class GroupImportForm(NetBoxModelImportForm):

    class Meta:
        model = NetBoxGroup
        fields = (
            'name',
        )
