from django import forms

from users.models import *
from django.utils.translation import gettext as _
from netbox.forms import NetBoxModelImportForm
from utilities.forms import BootstrapMixin
from utilities.forms.fields import CSVChoiceField, CSVModelChoiceField, SlugField

__all__ = (
    'GroupImportForm',
    'ObjectPermissionImportForm',
    'UserImportForm',
)


class UserImportForm(NetBoxModelImportForm):
    slug = SlugField()

    class Meta:
        model = NetBoxUser
        fields = (
            'email',
        )


class GroupImportForm(NetBoxModelImportForm):
    slug = SlugField()

    class Meta:
        model = NetBoxGroup
        fields = (
            'name',
        )


class ObjectPermissionImportForm(NetBoxModelImportForm):
    slug = SlugField()

    class Meta:
        model = ObjectPermission
        fields = (
            'name',
        )
