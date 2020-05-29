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

    class Meta:
        model = ObjectPermission
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Format ContentType choices
        order_content_types(self.fields['content_types'])
        self.fields['content_types'].choices.insert(0, ('', '---------'))

    def clean(self):
        content_types = self.cleaned_data['content_types']
        attrs = self.cleaned_data['attrs']

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
