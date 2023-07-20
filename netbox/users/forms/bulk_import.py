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
        # Set the hashed password
        self.instance.set_password(self.cleaned_data.get('password'))

        return super().save(*args, **kwargs)
