import re
from html.parser import HTMLParser

from django.conf import settings
from django.test import Client, override_settings
from django.urls import reverse
from django.utils.csp import CSP

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
