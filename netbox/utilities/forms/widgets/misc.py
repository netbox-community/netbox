from django import forms

__all__ = (
    'ClearableFileInput',
    'MarkdownWidget',
    'NumberWithOptions',
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


class NumberWithOptions(forms.NumberInput):
    """
    Number field with a dropdown pre-populated with common values for convenience.
    """
    template_name = 'widgets/number_with_options.html'

    def __init__(self, options, attrs=None):
        self.options = options
        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['options'] = self.options
        return context


class SlugWidget(forms.TextInput):
    """
    Subclass TextInput and add a slug regeneration button next to the form field.
    """
    template_name = 'widgets/sluginput.html'
