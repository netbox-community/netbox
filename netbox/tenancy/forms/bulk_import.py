from extras.forms import CustomFieldModelCSVForm
from tenancy.models import Tenant, TenantGroup
from utilities.forms import CSVModelChoiceField, SlugField

__all__ = (
    'TenantCSVForm',
    'TenantGroupCSVForm',
)


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
