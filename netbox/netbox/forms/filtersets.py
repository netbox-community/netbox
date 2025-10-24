from django import forms
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from extras.choices import *
from users.models import Owner
from utilities.forms.fields import DynamicModelChoiceField
from .mixins import CustomFieldsMixin, SavedFiltersMixin

__all__ = (
    'NestedGroupModelFilterSetForm',
    'NetBoxModelFilterSetForm',
    'OrganizationalModelFilterSetForm',
    'PrimaryModelFilterSetForm',
)


class NetBoxModelFilterSetForm(CustomFieldsMixin, SavedFiltersMixin, forms.Form):
    """
    Base form for FilerSet forms. These are used to filter object lists in the NetBox UI. Note that the
    corresponding FilterSet *must* provide a `q` filter.

    Attributes:
        model: The model class associated with the form
        fieldsets: An iterable of two-tuples which define a heading and field set to display per section of
            the rendered form (optional). If not defined, the all fields will be rendered as a single section.
        selector_fields: An iterable of names of fields to display by default when rendering the form as
            a selector widget
    """
    q = forms.CharField(
        required=False,
        label=_('Search')
    )

    selector_fields = ('filter_id', 'q')

    def _get_custom_fields(self, content_type):
        return super()._get_custom_fields(content_type).exclude(
            Q(filter_logic=CustomFieldFilterLogicChoices.FILTER_DISABLED) |
            Q(type=CustomFieldTypeChoices.TYPE_JSON)
        )

    def _get_form_field(self, customfield):
        return customfield.to_form_field(set_initial=False, enforce_required=False, enforce_visibility=False)


class PrimaryModelFilterSetForm(NetBoxModelFilterSetForm):
    """
    FilterSet form for models which inherit from PrimaryModel.
    """
    owner_id = DynamicModelChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        label=_('Owner'),
    )


class OrganizationalModelFilterSetForm(NetBoxModelFilterSetForm):
    """
    FilterSet form for models which inherit from OrganizationalModel.
    """
    owner_id = DynamicModelChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        label=_('Owner'),
    )


class NestedGroupModelFilterSetForm(NetBoxModelFilterSetForm):
    """
    FilterSet form for models which inherit from NestedGroupModel.
    """
    owner_id = DynamicModelChoiceField(
        queryset=Owner.objects.all(),
        required=False,
        label=_('Owner'),
    )
