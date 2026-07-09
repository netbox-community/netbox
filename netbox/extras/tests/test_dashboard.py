from django.test import RequestFactory, TestCase, tag

from extras.dashboard.widgets import ObjectListWidget
from extras.templatetags.dashboard import render_widget


class ObjectListWidgetTestCase(TestCase):
    def test_widget_config_form_validates_model(self):
        model_info = 'extras.notification'
        form = ObjectListWidget.ConfigForm({'model': model_info})
        self.assertFalse(form.is_valid())

    @tag('regression')
    def test_widget_fails_gracefully(self):
        """
        Example:
        '2829fd9b-5dee-4c9a-81f2-5bd84c350a27': {
            'class': 'extras.ObjectListWidget',
            'color': 'indigo',
            'title': 'Object List',
            'config': {
                'model': 'extras.notification',
                'page_size': None,
                'url_params': None
            }
        }
        """
        config = {
            # 'class': 'extras.ObjectListWidget',  # normally popped off, left for clarity
            'color': 'yellow',
            'title': 'this should fail',
            'config': {
                'model': 'extras.notification',
                'page_size': None,
                'url_params': None,
            },
        }

        class Request:
            class User:
                def has_perm(self, *args, **kwargs):
                    return True

            user = User()

        mock_request = Request()
        widget = ObjectListWidget(id='2829fd9b-5dee-4c9a-81f2-5bd84c350a27', **config)
        rendered = widget.render(mock_request)
        self.assertTrue('Unable to load content. Could not resolve list URL for:' in rendered)


class RenderWidgetTemplateTagTestCase(TestCase):

    def _make_context(self):
        request = RequestFactory().get('/')
        return {'request': request}

    def test_render_widget_escapes_exception_html(self):
        """Exception text with HTML special chars must be escaped, not rendered as markup."""

        class BrokenWidget:
            def render(self, request):
                raise Exception('<script>alert(1)</script>')

        output = render_widget(self._make_context(), BrokenWidget())
        self.assertIn('&lt;script&gt;', output)
        self.assertNotIn('<script>', output)

    def test_render_widget_escapes_exception_angle_brackets(self):
        """Angle brackets in exception messages are escaped."""

        class BrokenWidget:
            def render(self, request):
                raise ValueError('invalid value: <bad>')

        output = render_widget(self._make_context(), BrokenWidget())
        self.assertIn('&lt;bad&gt;', output)
        self.assertNotIn('<bad>', output)
