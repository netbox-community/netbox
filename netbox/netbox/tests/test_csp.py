import re
from html.parser import HTMLParser
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.staticfiles import finders
from django.test import Client, override_settings
from django.urls import reverse
from django.utils.csp import CSP
from drf_spectacular.settings import patched_settings

from dcim.models import Site
from utilities.testing import TestCase

CSP_POLICY = {
    'script-src': [CSP.SELF, CSP.NONCE],
}


class ScriptCollector(HTMLParser):
    """
    Record the attributes of every <script> element, and every inline event handler attribute (e.g. onerror) on any
    element.
    """
    def __init__(self):
        super().__init__()
        self.scripts = []
        self.handlers = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'script':
            self.scripts.append(attrs)
        for name in attrs:
            # Inline event handler attributes are the only standard attributes starting with "on"
            if name.startswith('on'):
                self.handlers.append(f'<{tag} {name}="{attrs[name]}">')


class HxTriggerCollector(HTMLParser):
    """
    Record the attributes of every <input> element that has an hx-trigger attribute.
    """
    def __init__(self):
        super().__init__()
        self.inputs = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'input' and 'hx-trigger' in attrs:
            self.inputs.append(attrs)


@override_settings(SECURE_CSP=CSP_POLICY, DEBUG=False)
class ScriptNonceTestCase(TestCase):
    """
    Every <script> NetBox renders carries the request's CSP nonce, and no page uses inline event handler attributes
    (which a nonce cannot cover). Together these let NetBox run under a policy without 'unsafe-inline'.
    """

    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.create(name='Site 1', slug='site-1')

    def setUp(self):
        super().setUp()

        self.user.is_superuser = True
        self.user.save()

    @staticmethod
    def collect(response):
        parser = ScriptCollector()
        parser.feed(response.content.decode())
        return parser

    def assertScriptsNonced(self, response):
        self.assertHttpStatus(response, 200)
        match = re.search(r"'nonce-([^']+)'", response['Content-Security-Policy'])
        self.assertIsNotNone(match, f"No nonce in header: {response['Content-Security-Policy']}")
        nonce = match.group(1)

        parser = self.collect(response)
        self.assertTrue(parser.scripts, 'No <script> elements found')
        for script in parser.scripts:
            self.assertEqual(script.get('nonce'), nonce, f'<script> without the request nonce: {script}')
        self.assertEqual(parser.handlers, [], 'Inline event handler attributes found')

    def test_login(self):
        self.assertScriptsNonced(Client().get(reverse('login')))

    def test_object_list(self):
        self.assertScriptsNonced(self.client.get(reverse('dcim:site_list')))

    def test_object_detail(self):
        self.assertScriptsNonced(self.client.get(self.site.get_absolute_url()))

    def test_user_token_edit(self):
        self.assertScriptsNonced(self.client.get(reverse('account:usertoken_add')))

    def test_token_edit(self):
        self.assertScriptsNonced(self.client.get(reverse('users:token_add')))

    def test_copilot_script(self):
        # Copilot is enabled globally by default. Each user opts in with a preference.
        self.user.config.set('ui.copilot_enabled', 'true', commit=True)

        response = self.client.get(reverse('dcim:site_list'))
        self.assertScriptsNonced(response)
        self.assertIn(settings.NETBOX_COPILOT_URL, [script.get('src') for script in self.collect(response).scripts])

    def test_graphiql(self):
        self.assertScriptsNonced(self.client.get(reverse('graphql'), HTTP_ACCEPT='text/html'))

    def test_swagger_ui(self):
        self.assertScriptsNonced(self.client.get(reverse('api_docs')))

    def test_redoc(self):
        self.assertScriptsNonced(self.client.get(reverse('api_redocs')))

    def test_redoc_with_settings(self):
        # With REDOC_UI_SETTINGS set, Redoc renders an inline Redoc.init script. drf-spectacular reads its settings
        # once at import and has no setting_changed hook, so override_settings(SPECTACULAR_SETTINGS=...) has no
        # effect. patched_settings is its own supported way to override them temporarily.
        with patched_settings({'REDOC_UI_SETTINGS': {'hideDownloadButton': True}}):
            response = self.client.get(reverse('api_redocs'))
        self.assertScriptsNonced(response)
        inline = [script for script in self.collect(response).scripts if 'src' not in script]
        self.assertEqual(len(inline), 1)
        self.assertIn('Redoc.init', response.content.decode())

    def test_browsable_api(self):
        self.assertScriptsNonced(self.client.get(reverse('api-root'), HTTP_ACCEPT='text/html'))
        self.assertScriptsNonced(self.client.get(reverse('dcim-api:site-list'), HTTP_ACCEPT='text/html'))

    def test_api_script_sources_exist(self):
        # The overrides copy upstream script tags, so an upgrade that renames a bundled file (e.g. jQuery) would
        # leave a dead src. Every same-origin script src must resolve to a static file.
        static_url = settings.STATIC_URL
        responses = [
            self.client.get(reverse('api_docs')),
            self.client.get(reverse('api_redocs')),
            self.client.get(reverse('api-root'), HTTP_ACCEPT='text/html'),
        ]
        for response in responses:
            self.assertHttpStatus(response, 200)
            checked = 0
            for script in self.collect(response).scripts:
                src = script.get('src')
                if not src:
                    continue
                path = urlsplit(src).path
                if not path.startswith(static_url):
                    continue
                checked += 1
                relative = path.removeprefix(static_url)
                self.assertTrue(finders.find(relative), f'No static file for script src {src}')
            self.assertGreater(checked, 0, f'No same-origin scripts found on {response.request["PATH_INFO"]}')

    def test_search_has_no_runtime_eval(self):
        # A trigger filter such as keyup[...] is compiled with eval by htmx, which a policy without
        # 'unsafe-eval' blocks (htmx then fires with no filter at all).
        response = self.client.get(reverse('search'))
        self.assertHttpStatus(response, 200)
        collector = HxTriggerCollector()
        collector.feed(response.content.decode())
        self.assertEqual(len(collector.inputs), 1)
        attrs = collector.inputs[0]
        self.assertEqual(attrs['hx-trigger'], 'netbox:search-input changed delay:500ms')
        self.assertEqual(attrs['data-search-min-length'], '3')
