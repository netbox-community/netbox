from django import forms
from django.utils.translation import gettext_lazy as _

from utilities.forms.fields import DynamicModelChoiceField

from ..models import DataFile, DataSource

__all__ = (
    'SyncedDataMixin',
)


class SyncedDataMixin(forms.Form):
    data_source = DynamicModelChoiceField(
        queryset=DataSource.objects.all(),
        required=False,
        label=_('Data source')
    )
    data_file = DynamicModelChoiceField(
        queryset=DataFile.objects.all(),
        required=False,
        label=_('File'),
        query_params={
            'source_id': '$data_source',
        }
    )
