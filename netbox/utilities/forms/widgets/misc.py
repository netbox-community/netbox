from django import forms

__all__ = (
    'ClearableFileInput',
    'MarkdownWidget',
    'SlugWidget',
)


class ClearableFileInput(forms.ClearableFileInput):
    """
    Override Django's stock ClearableFileInput with a custom template.
    """
    template_name = 'widgets/clearable_file_input.html'


class MarkdownWidget(forms.Textarea):
    """
    Provide a live preview for Markdown-formatted content.
    """
    template_name = 'widgets/markdown_input.html'


class SlugWidget(forms.TextInput):
    """
    Subclass TextInput and add a slug regeneration button next to the form field.
    """
    template_name = 'widgets/sluginput.html'
