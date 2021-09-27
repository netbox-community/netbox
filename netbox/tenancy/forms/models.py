from extras.forms import CustomFieldModelForm
from extras.models import Tag
from tenancy.models import Tenant, TenantGroup
from utilities.forms import (
    BootstrapMixin, CommentField, DynamicModelChoiceField, DynamicModelMultipleChoiceField, SlugField,
)

__all__ = (
    'TenantForm',
    'TenantGroupForm',
)


class TenantGroupForm(BootstrapMixin, CustomFieldModelForm):
    parent = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False
    )
    slug = SlugField()

    class Meta:
        model = TenantGroup
        fields = [
            'parent', 'name', 'slug', 'description',
        ]


class TenantForm(BootstrapMixin, CustomFieldModelForm):
    slug = SlugField()
    group = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False
    )
    comments = CommentField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = Tenant
        fields = (
            'name', 'slug', 'group', 'description', 'comments', 'tags',
        )
        fieldsets = (
            ('Tenant', ('name', 'slug', 'group', 'description', 'tags')),
        )
