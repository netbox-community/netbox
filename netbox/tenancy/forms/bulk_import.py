from extras.forms import CustomFieldModelCSVForm
from tenancy.models import *
from utilities.forms import CSVModelChoiceField, SlugField

__all__ = (
    'ContactCSVForm',
    'ContactGroupCSVForm',
    'ContactRoleCSVForm',
    'TenantCSVForm',
    'TenantGroupCSVForm',
)


#
# Tenants
#

class TenantGroupCSVForm(CustomFieldModelCSVForm):
    parent = CSVModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Parent group'
    )
    slug = SlugField()

    class Meta:
        model = TenantGroup
        fields = ('name', 'slug', 'parent', 'description')


class TenantCSVForm(CustomFieldModelCSVForm):
    slug = SlugField()
    group = CSVModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned group'
    )

    class Meta:
        model = Tenant
        fields = ('name', 'slug', 'group', 'description', 'comments')


#
# Contacts
#

class ContactGroupCSVForm(CustomFieldModelCSVForm):
    parent = CSVModelChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Parent group'
    )
    slug = SlugField()

    class Meta:
        model = ContactGroup
        fields = ('name', 'slug', 'parent', 'description')


class ContactRoleCSVForm(CustomFieldModelCSVForm):
    slug = SlugField()

    class Meta:
        model = ContactRole
        fields = ('name', 'slug', 'description')


class ContactCSVForm(CustomFieldModelCSVForm):
    slug = SlugField()
    group = CSVModelChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned group'
    )

    class Meta:
        model = Contact
        fields = ('name', 'title', 'phone', 'email', 'address', 'group', 'comments')
