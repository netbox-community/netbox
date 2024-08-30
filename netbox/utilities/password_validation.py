from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class AlphanumericPasswordValidator:
    """
    Validate that the password has at least one numeral, one uppercase letter and one lowercase letter.
    """

    def validate(self, password, user=None):
        if not any(char.isdigit() for char in password):
            raise ValidationError(
                _("Password must have at least one numeral."),
            )

        if not any(char.isupper() for char in password):
            raise ValidationError(
                _("Password must have at least one uppercase letter."),
            )

        if not any(char.islower() for char in password):
            raise ValidationError(
                _("Password must have at least one lowercase letter."),
            )

    def get_help_text(self):
        return _("Your password must contain at least one numeral, one uppercase letter and one lowercase letter.")
