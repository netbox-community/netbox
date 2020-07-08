from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdmin_
from django.contrib.auth.models import Group, User
from django.core.exceptions import FieldError, ValidationError

from extras.admin import order_content_types
from .models import AdminGroup, AdminUser, ObjectPermission, Token, UserConfig


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

    def user_count(self, obj):
        return obj.user_set.count()


class UserConfigInline(admin.TabularInline):
    model = UserConfig
    readonly_fields = ('data',)
    can_delete = False
    verbose_name = 'Preferences'


class ObjectPermissionInline(admin.TabularInline):
    model = AdminUser.object_permissions.through
    fields = ['object_types', 'actions', 'constraints']
    readonly_fields = fields
    extra = 0
    verbose_name = 'Permission'

    def object_types(self, instance):
        return ', '.join(instance.objectpermission.object_types.values_list('model', flat=True))

    def actions(self, instance):
        return ', '.join(instance.objectpermission.actions)

    def constraints(self, instance):
        return instance.objectpermission.constraints

    def has_add_permission(self, request, obj):
        # Don't allow the creation of new ObjectPermission assignments via this form
        return False


@admin.register(AdminUser)
class UserAdmin(UserAdmin_):
    list_display = [
        'username', 'email', 'first_name', 'last_name', 'is_superuser', 'is_staff', 'is_active'
    ]
    fieldsets = (
        (None, {'fields': ('username', 'password', 'first_name', 'last_name', 'email')}),
        ('Groups', {'fields': ('groups',)}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    inlines = [ObjectPermissionInline, UserConfigInline]
    filter_horizontal = ('groups',)


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
                           'to match all objects of this type.'
        }
        labels = {
            'actions': 'Additional actions'
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
        object_types = self.cleaned_data['object_types']
        constraints = self.cleaned_data['constraints']

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
        if constraints:
            for ct in object_types:
                model = ct.model_class()
                try:
                    model.objects.filter(**constraints).exists()
                except FieldError as e:
                    raise ValidationError({
                        'constraints': f'Invalid filter for {model}: {e}'
                    })


@admin.register(ObjectPermission)
class ObjectPermissionAdmin(admin.ModelAdmin):
    actions = ('enable', 'disable')
    fieldsets = (
        (None, {
            'fields': ('name', 'enabled')
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
            'fields': ('constraints',)
        }),
    )
    filter_horizontal = ('object_types', 'groups', 'users')
    form = ObjectPermissionForm
    list_display = [
        'get_name', 'enabled', 'list_models', 'list_users', 'list_groups', 'actions', 'constraints',
    ]
    list_filter = [
        'groups', 'users'
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).unrestricted().prefetch_related('object_types', 'users', 'groups')

    def get_name(self, obj):
        return obj.name or f'Permission #{obj.pk}'
    get_name.short_description = 'Name'

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
