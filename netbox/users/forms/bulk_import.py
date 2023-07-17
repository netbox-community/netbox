from django import forms

from users.models import NetBoxGroup, NetBoxUser
from utilities.forms import CSVModelForm

__all__ = (
    'GroupImportForm',
    'UserImportForm',
)


class GroupImportForm(CSVModelForm):

    class Meta:
        model = NetBoxGroup
        fields = (
            'name',
        )


class UserImportForm(CSVModelForm):

    class Meta:
        model = NetBoxUser
        fields = (
            'username', 'first_name', 'last_name', 'email', 'password', 'is_staff',
            'is_active', 'is_superuser'
        )

    def save(self, *args, **kwargs):
        edited = getattr(self, 'instance', None)
        instance = super().save(*args, **kwargs)

        # On edit, check if we have to save the password
        if edited and self.cleaned_data.get("password"):
            instance.set_password(self.cleaned_data.get("password"))
            instance.save()

        return instance
