from django.core.cache import cache
from django.test import RequestFactory, TestCase, tag

from extras.dashboard.widgets import ObjectListWidget, RSSFeedWidget
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


class RSSFeedWidgetSanitizationTestCase(TestCase):
    """
    Feed entry content is externally controlled and untrusted. Links must be validated against
    ALLOWED_URL_SCHEMES so dangerous schemes (e.g. javascript:) cannot become clickable XSS sinks.
    """

    @tag('regression')
    def test_sanitize_entries_blanks_disallowed_schemes(self):
        entries = [
            {'link': 'javascript:alert(document.cookie)', 'title': 't1'},
            {'link': 'JavaScript:alert(1)', 'title': 't2'},  # case-insensitive
            {'link': 'data:text/html,<script>alert(1)</script>', 'title': 't3'},
            {'link': 'vbscript:msgbox(1)', 'title': 't4'},
        ]
        RSSFeedWidget.sanitize_entries(entries)
        for entry in entries:
            self.assertEqual(entry['link'], '', msg=f"Failed to blank {entry['title']}")

    @tag('regression')
    def test_sanitize_entries_preserves_allowed_links(self):
        entries = [
            {'link': 'https://example.com/post', 'title': 't1'},
            {'link': 'http://example.com/post', 'title': 't2'},
            {'link': 'mailto:user@example.com', 'title': 't3'},
            {'link': '/relative/path', 'title': 't4'},  # schemeless relative link
        ]
        expected = [e['link'] for e in entries]
        RSSFeedWidget.sanitize_entries(entries)
        self.assertEqual([e['link'] for e in entries], expected)

    @tag('regression')
    def test_sanitize_entries_cleans_summary_html(self):
        entries = [
            {'link': 'https://example.com', 'title': 't1', 'summary': '<b>ok</b><script>alert(1)</script>'},
        ]
        RSSFeedWidget.sanitize_entries(entries)
        self.assertNotIn('<script>', entries[0]['summary'])
        self.assertIn('<b>ok</b>', entries[0]['summary'])

    @tag('regression')
    def test_get_feed_sanitizes_cached_content(self):
        """
        Content cached by a pre-fix release must be sanitized on read, not served verbatim.
        """
        widget = RSSFeedWidget(config={
            'feed_url': 'https://example.com/feed.xml',
            'requires_internet': False,
            'max_entries': 10,
        })
        # Simulate a poisoned feed left in the cache by an older release
        cache.set(widget.cache_key, {
            'bozo': False,
            'entries': [
                {'link': 'javascript:alert(1)', 'title': 'evil', 'summary': 'x'},
            ],
        })

        result = widget.get_feed()

        self.assertEqual(result['feed']['entries'][0]['link'], '')


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
