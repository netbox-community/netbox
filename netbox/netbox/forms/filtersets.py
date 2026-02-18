from django import forms
from django.utils.translation import gettext_lazy as _

from extras.choices import *
from utilities.forms.fields import QueryField
from utilities.forms.mixins import FilterModifierMixin

from .mixins import CustomFieldsMixin, OwnerFilterMixin, SavedFiltersMixin

__all__ = (
    'NestedGroupModelFilterSetForm',
    'NetBoxModelFilterSetForm',
    'OrganizationalModelFilterSetForm',
    'PrimaryModelFilterSetForm',
)


class NetBoxModelFilterSetForm(FilterModifierMixin, CustomFieldsMixin, SavedFiltersMixin, forms.Form):
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
    q = QueryField(
        required=False,
        label=_('Search')
    )

    selector_fields = ('filter_id', 'q')

    def _get_custom_fields(self, content_type):
        # Return only non-hidden custom fields for which filtering is enabled (excluding JSON fields)
        return [
            cf for cf in super()._get_custom_fields(content_type) if (
                cf.filter_logic != CustomFieldFilterLogicChoices.FILTER_DISABLED and
                cf.type != CustomFieldTypeChoices.TYPE_JSON
            )
        ]

    def _get_form_field(self, customfield):
        return customfield.to_form_field(
            set_initial=False, enforce_required=False, enforce_visibility=False, for_filterset_form=True
        )


class PrimaryModelFilterSetForm(OwnerFilterMixin, NetBoxModelFilterSetForm):
    """
    FilterSet form for models which inherit from PrimaryModel.
    """
    pass


class OrganizationalModelFilterSetForm(OwnerFilterMixin, NetBoxModelFilterSetForm):
    """
    FilterSet form for models which inherit from OrganizationalModel.
    """
    pass


class NestedGroupModelFilterSetForm(OwnerFilterMixin, NetBoxModelFilterSetForm):
    """
    FilterSet form for models which inherit from NestedGroupModel.
    """
    pass
