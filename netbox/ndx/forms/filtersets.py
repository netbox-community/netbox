from django import forms
from django.utils.translation import gettext_lazy as _

from core.models import ObjectType
from ndx.choices import ImportRecordSourceChoices
from ndx.importers import get_importers
from ndx.models import ImportRecord
from netbox.forms.mixins import SavedFiltersMixin
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES, FilterForm, add_blank_choice
from utilities.forms.fields import ContentTypeMultipleChoiceField
from utilities.forms.rendering import FieldSet

__all__ = (
    'CatalogFilterForm',
    'ImportRecordFilterForm',
)


def get_entry_type_choices():
    return [(entry_type, importer.label) for entry_type, importer in get_importers().items()]


class ImportRecordFilterForm(SavedFiltersMixin, FilterForm):
    model = ImportRecord
    fieldsets = (
        FieldSet('q', 'filter_id'),
        FieldSet('entry_type', 'object_type_id', 'vendor_slug', 'source', name=_('Catalog Entry')),
        FieldSet('update_available', 'has_enrichment', name=_('Status')),
    )
    entry_type = forms.MultipleChoiceField(
        label=_('Entry type'),
        choices=get_entry_type_choices,
        required=False
    )
    object_type_id = ContentTypeMultipleChoiceField(
        label=_('Object type'),
        queryset=ObjectType.objects.public(),
        required=False
    )
    vendor_slug = forms.CharField(
        label=_('Vendor slug'),
        required=False
    )
    source = forms.MultipleChoiceField(
        label=_('Source'),
        choices=ImportRecordSourceChoices,
        required=False
    )
    update_available = forms.NullBooleanField(
        label=_('Update available'),
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    has_enrichment = forms.NullBooleanField(
        label=_('Has enrichment'),
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )


class CatalogFilterForm(forms.Form):
    """
    Search and filter entries in the NDX catalog.
    """
    q = forms.CharField(
        label=_('Search'),
        required=False
    )
    vendor = forms.ChoiceField(
        label=_('Vendor'),
        required=False
    )
    type = forms.ChoiceField(
        label=_('Type'),
        choices=lambda: add_blank_choice(get_entry_type_choices()),
        required=False
    )

    def __init__(self, *args, vendors=None, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [
            (vendor.get('slug'), vendor.get('display_name') or vendor.get('slug')) for vendor in vendors or []
        ]
        # Retain a selected vendor which isn't listed (e.g. because the list of vendors couldn't be retrieved)
        if self.is_bound and (vendor := self.data.get('vendor')) and vendor not in dict(choices):
            choices.append((vendor, vendor))
        self.fields['vendor'].choices = add_blank_choice(choices)
