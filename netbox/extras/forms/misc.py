from django import forms
from django.utils.translation import gettext_lazy as _

__all__ = (
    'RenderMarkdownForm',
)


class RenderMarkdownForm(forms.Form):
    """
    Provides basic validation for markup to be rendered.
    """
    text = forms.CharField(
        label=_('Text'),
        required=False
    )
