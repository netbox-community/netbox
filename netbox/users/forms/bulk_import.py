from users.models import *
from utilities.forms import CSVModelForm


__all__ = (
    'TokenImportForm',
)


class TokenImportForm(CSVModelForm):

    class Meta:
        model = Token
        fields = ('description', )
