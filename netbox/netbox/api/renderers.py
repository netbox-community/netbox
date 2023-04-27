from rest_framework.renderers import BaseRenderer, BrowsableAPIRenderer

__all__ = (
    'FormlessBrowsableAPIRenderer',
    'TextRenderer',
)


class FormlessBrowsableAPIRenderer(BrowsableAPIRenderer):
    """
    Override the built-in BrowsableAPIRenderer to disable HTML forms.
    """
    def show_form_for_method(self, *args, **kwargs):
        return False

    def get_filter_form(self, data, view, request):
        return None


class TextRenderer(BaseRenderer):
    """
    Return raw data as plain text.
    """
    media_type = 'text/plain'
    format = 'txt'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return str(data)
