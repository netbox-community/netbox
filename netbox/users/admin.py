from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdmin_
from django.contrib.auth.models import Group as StockGroup, User as StockUser
from django.core.exceptions import FieldError, ValidationError

from extras.admin import order_content_types
from .models import AdminGroup, AdminUser, ObjectPermission, Token, UserConfig


#
# Users & groups
#

# Unregister the built-in GroupAdmin and UserAdmin classes so that we can use our custom admin classes below
admin.site.unregister(StockGroup)
admin.site.unregister(StockUser)


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


@admin.register(AdminUser)
class UserAdmin(UserAdmin_):
    list_display = [
        'username', 'email', 'first_name', 'last_name', 'is_superuser', 'is_staff', 'is_active'
    ]
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    inlines = (UserConfigInline,)


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
            'actions': 'Actions granted in addition to those listed above'
        }
        labels = {
            'actions': 'Additional actions'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make the actions field optional since the admin form uses it only for non-CRUD actions
        self.fields['actions'].required = False

        # Format ContentType choices
        order_content_types(self.fields['content_types'])
        self.fields['content_types'].choices.insert(0, ('', '---------'))

        # Check the appropriate checkboxes when editing an existing ObjectPermission
        if self.instance:
            for action in ['view', 'add', 'change', 'delete']:
                if action in self.instance.actions:
                    self.fields[f'can_{action}'].initial = True
                    self.instance.actions.remove(action)

    def clean(self):
        content_types = self.cleaned_data['content_types']
        attrs = self.cleaned_data['attrs']

        # Append any of the selected CRUD checkboxes to the actions list
        if not self.cleaned_data.get('actions'):
            self.cleaned_data['actions'] = list()
        for action in ['view', 'add', 'change', 'delete']:
            if self.cleaned_data[f'can_{action}'] and action not in self.cleaned_data['actions']:
                self.cleaned_data['actions'].append(action)

        # At least one action must be specified
        if not self.cleaned_data['actions']:
            raise ValidationError("At least one action must be selected.")

        # Validate the specified model attributes by attempting to execute a query. We don't care whether the query
        # returns anything; we just want to make sure the specified attributes are valid.
        if attrs:
            for ct in content_types:
                model = ct.model_class()
                try:
                    model.objects.filter(**attrs).exists()
                except FieldError as e:
                    raise ValidationError({
                        'attrs': f'Invalid attributes for {model}: {e}'
                    })


@admin.register(ObjectPermission)
class ObjectPermissionAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Objects', {
            'fields': ('content_types',)
        }),
        ('Assignment', {
            'fields': (('groups', 'users'),)
        }),
        ('Actions', {
            'fields': (('can_view', 'can_add', 'can_change', 'can_delete'), 'actions')
        }),
        ('Constraints', {
            'fields': ('attrs',)
        }),
    )
    form = ObjectPermissionForm
    list_display = [
        'list_models', 'list_users', 'list_groups', 'actions', 'attrs',
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('content_types', 'users', 'groups')

    def list_models(self, obj):
        return ', '.join([f"{ct}" for ct in obj.content_types.all()])
    list_models.short_description = 'Models'

    def list_users(self, obj):
        return ', '.join([u.username for u in obj.users.all()])
    list_users.short_description = 'Users'

    def list_groups(self, obj):
        return ', '.join([g.name for g in obj.groups.all()])
    list_groups.short_description = 'Groups'
