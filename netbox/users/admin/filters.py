from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from users.models import ObjectPermission

__all__ = (
    'ActionListFilter',
    'ObjectTypeListFilter',
)


class ActionListFilter(admin.SimpleListFilter):
    title = 'action'
    parameter_name = 'action'

    def lookups(self, request, model_admin):
        options = set()
        for action_list in ObjectPermission.objects.values_list('actions', flat=True).distinct():
            options.update(action_list)
        return [
            (action, action) for action in sorted(options)
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(actions=[self.value()])


class ObjectTypeListFilter(admin.SimpleListFilter):
    title = 'object type'
    parameter_name = 'object_type'

    def lookups(self, request, model_admin):
        object_types = ObjectPermission.objects.values_list('object_types__pk', flat=True).distinct()
        content_types = ContentType.objects.filter(pk__in=object_types).order_by('app_label', 'model')
        return [
            (ct.pk, ct) for ct in content_types
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(object_types=self.value())
