from django import forms

from users.models import NetBoxGroup
from netbox.forms import NetBoxModelImportForm

__all__ = (
    'GroupImportForm',
)


class GroupImportForm(NetBoxModelImportForm):

    class Meta:
        model = NetBoxGroup
        fields = (
            'name',
        )
