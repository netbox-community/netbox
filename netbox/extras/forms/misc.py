from django import forms

__all__ = (
    'RenderMarkdownForm',
)


class RenderMarkdownForm(forms.Form):
    """
    Provides basic validation for markup to be rendered.
    """
    text = forms.CharField(
        required=False
    )
