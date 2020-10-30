from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdmin_
from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldError, ValidationError
from django.db.models import Q

from extras.admin import order_content_types
from .models import AdminGroup, AdminUser, ObjectPermission, Token, UserConfig


#
# Inline models
#

class ObjectPermissionInline(admin.TabularInline):
    exclude = None
    extra = 3
    readonly_fields = ['object_types', 'actions', 'constraints']
    verbose_name = 'Permission'
    verbose_name_plural = 'Permissions'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('objectpermission__object_types').nocache()

    @staticmethod
    def object_types(instance):
        # Don't call .values_list() here because we want to reference the pre-fetched object_types
        return ', '.join([ot.name for ot in instance.objectpermission.object_types.all()])

    @staticmethod
    def actions(instance):
        return ', '.join(instance.objectpermission.actions)

    @staticmethod
    def constraints(instance):
        return instance.objectpermission.constraints


class GroupObjectPermissionInline(ObjectPermissionInline):
    model = AdminGroup.object_permissions.through


class UserObjectPermissionInline(ObjectPermissionInline):
    model = AdminUser.object_permissions.through


class UserConfigInline(admin.TabularInline):
    model = UserConfig
    readonly_fields = ('data',)
    can_delete = False
    verbose_name = 'Preferences'


#
# Users & groups
#

# Unregister the built-in GroupAdmin and UserAdmin classes so that we can use our custom admin classes below
admin.site.unregister(Group)
admin.site.unregister(User)


@admin.register(AdminGroup)
class GroupAdmin(admin.ModelAdmin):
    fields = ('name',)
    list_display = ('name', 'user_count')
    ordering = ('name',)
    search_fields = ('name',)
    inlines = [GroupObjectPermissionInline]

    @staticmethod
    def user_count(obj):
        return obj.user_set.count()


@admin.register(AdminUser)
class UserAdmin(UserAdmin_):
    list_display = [
        'username', 'email', 'first_name', 'last_name', 'is_superuser', 'is_staff', 'is_active'
    ]
    fieldsets = (
        (None, {'fields': ('username', 'password', 'first_name', 'last_name', 'email')}),
        ('Groups', {'fields': ('groups',)}),
        ('Status', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    filter_horizontal = ('groups',)

    def get_inlines(self, request, obj):
        if obj is not None:
            return (UserObjectPermissionInline, UserConfigInline)
        return ()


#
# REST API tokens
#

class TokenAdminForm(forms.ModelForm):
    key = forms.CharField(
        required=False,
        help_text="If no key is provided, one will be generated automatically."
    )

    class Meta:
        fields = [
            'user', 'key', 'write_enabled', 'expires', 'description'
        ]
        model = Token


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    form = TokenAdminForm
    list_display = [
        'key', 'user', 'created', 'expires', 'write_enabled', 'description'
    ]


#
# Permissions
#

class ObjectPermissionForm(forms.ModelForm):
    can_view = forms.BooleanField(required=False)
    can_add = forms.BooleanField(required=False)
    can_change = forms.BooleanField(required=False)
    can_delete = forms.BooleanField(required=False)

    class Meta:
        model = ObjectPermission
        exclude = []
        help_texts = {
            'actions': 'Actions granted in addition to those listed above',
            'constraints': 'JSON expression of a queryset filter that will return only permitted objects. Leave null '
                           'to match all objects of this type. A list of multiple objects will result in a logical OR '
                           'operation.'
        }
        labels = {
            'actions': 'Additional actions'
        }
        widgets = {
            'constraints': forms.Textarea(attrs={'class': 'vLargeTextField'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make the actions field optional since the admin form uses it only for non-CRUD actions
        self.fields['actions'].required = False

        # Format ContentType choices
        order_content_types(self.fields['object_types'])
        self.fields['object_types'].choices.insert(0, ('', '---------'))

        # Order group and user fields
        self.fields['groups'].queryset = self.fields['groups'].queryset.order_by('name')
        self.fields['users'].queryset = self.fields['users'].queryset.order_by('username')

        # Check the appropriate checkboxes when editing an existing ObjectPermission
        if self.instance.pk:
            for action in ['view', 'add', 'change', 'delete']:
                if action in self.instance.actions:
                    self.fields[f'can_{action}'].initial = True
                    self.instance.actions.remove(action)

    def clean(self):
        object_types = self.cleaned_data.get('object_types')
        constraints = self.cleaned_data.get('constraints')

        # Append any of the selected CRUD checkboxes to the actions list
        if not self.cleaned_data.get('actions'):
            self.cleaned_data['actions'] = list()
        for action in ['view', 'add', 'change', 'delete']:
            if self.cleaned_data[f'can_{action}'] and action not in self.cleaned_data['actions']:
                self.cleaned_data['actions'].append(action)

        # At least one action must be specified
        if not self.cleaned_data['actions']:
            raise ValidationError("At least one action must be selected.")

        # Validate the specified model constraints by attempting to execute a query. We don't care whether the query
        # returns anything; we just want to make sure the specified constraints are valid.
        if object_types and constraints:
            # Normalize the constraints to a list of dicts
            if type(constraints) is not list:
                constraints = [constraints]
            for ct in object_types:
                model = ct.model_class()
                try:
                    model.objects.filter(*[Q(**c) for c in constraints]).exists()
                except FieldError as e:
                    raise ValidationError({
                        'constraints': f'Invalid filter for {model}: {e}'
                    })


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
        object_types = ObjectPermission.objects.values_list('id', flat=True).distinct()
        content_types = ContentType.objects.filter(pk__in=object_types).order_by('app_label', 'model')
        return [
            (ct.pk, ct) for ct in content_types
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(object_types=self.value())


@admin.register(ObjectPermission)
class ObjectPermissionAdmin(admin.ModelAdmin):
    actions = ('enable', 'disable')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'enabled')
        }),
        ('Actions', {
            'fields': (('can_view', 'can_add', 'can_change', 'can_delete'), 'actions')
        }),
        ('Objects', {
            'fields': ('object_types',)
        }),
        ('Assignment', {
            'fields': ('groups', 'users')
        }),
        ('Constraints', {
            'fields': ('constraints',),
            'classes': ('monospace',)
        }),
    )
    filter_horizontal = ('object_types', 'groups', 'users')
    form = ObjectPermissionForm
    list_display = [
        'name', 'enabled', 'list_models', 'list_users', 'list_groups', 'actions', 'constraints', 'description',
    ]
    list_filter = [
        'enabled', ActionListFilter, ObjectTypeListFilter, 'groups', 'users'
    ]
    search_fields = ['actions', 'constraints', 'description', 'name']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('object_types', 'users', 'groups')

    def list_models(self, obj):
        return ', '.join([f"{ct}" for ct in obj.object_types.all()])
    list_models.short_description = 'Models'

    def list_users(self, obj):
        return ', '.join([u.username for u in obj.users.all()])
    list_users.short_description = 'Users'

    def list_groups(self, obj):
        return ', '.join([g.name for g in obj.groups.all()])
    list_groups.short_description = 'Groups'

    #
    # Admin actions
    #

    def enable(self, request, queryset):
        updated = queryset.update(enabled=True)
        self.message_user(request, f"Enabled {updated} permissions")

    def disable(self, request, queryset):
        updated = queryset.update(enabled=False)
        self.message_user(request, f"Disabled {updated} permissions")
