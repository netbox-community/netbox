from utilities.forms import BootstrapMixin, CommentField
from .models import LogItem

from django import forms


class CommentForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        fields = [
            'body',
            'for_device',
            'created_by',
        ]
        model = LogItem
