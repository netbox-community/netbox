from django import forms

__all__ = (
    'ArrayWidget',
    'ChoicesWidget',
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

    def __init__(self, attrs=None):
        # Markdown fields should use monospace font
        default_attrs = {
            "class": "font-monospace",
        }
        if attrs:
            default_attrs.update(attrs)

        super().__init__(default_attrs)


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


class ArrayWidget(forms.Textarea):
    """
    Render each item of an array on a new line within a textarea for easy editing/
    """
    def format_value(self, value):
        if value is None or not len(value):
            return None
        return '\n'.join(value)


class ChoicesWidget(forms.Textarea):
    """
    Render each key-value pair of a dictionary on a new line within a textarea for easy editing.
    """
    def format_value(self, value):
        if not value:
            return None
        if type(value) is list:
            return '\n'.join([f'{k}:{v}' for k, v in value])
        return value
