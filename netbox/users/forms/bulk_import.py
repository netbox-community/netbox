from django import forms

from circuits.choices import CircuitStatusChoices
from circuits.models import *
from dcim.models import Site
from django.utils.translation import gettext as _
from netbox.forms import NetBoxModelImportForm
from tenancy.models import Tenant
from utilities.forms import BootstrapMixin
from utilities.forms.fields import CSVChoiceField, CSVModelChoiceField, SlugField

__all__ = (
    'UserImportForm',
)


class UserImportForm(NetBoxModelImportForm):
    slug = SlugField()

    class Meta:
        model = Provider
        fields = (
            'name', 'slug', 'description', 'comments', 'tags',
        )
