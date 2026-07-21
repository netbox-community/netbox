from django.contrib.auth import get_user_model
from django.contrib.auth.context_processors import PermWrapper
from django.test import RequestFactory, TestCase

from core.models import ObjectType
from dcim.models import Site
from extras.models import CustomLink
from extras.templatetags.custom_links import custom_links
from users.models import ObjectPermission

User = get_user_model()


class CustomLinkTemplateTagTest(TestCase):
    """
    The custom_links template tag must honor object-level permissions on CustomLink (see #22439).
    """

    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.create(name='Site 1', slug='site-1')
        cls.custom_link = CustomLink.objects.create(
            name='Custom Link 1',
            enabled=True,
            weight=100,
            new_window=False,
            link_text='Link 1',
            link_url='http://example.com/'
        )
        cls.custom_link.object_types.set([ObjectType.objects.get_for_model(Site)])

    def render(self, user):
        request = RequestFactory().get('/')
        request.user = user
        context = {
            'request': request,
            'user': user,
            'perms': PermWrapper(user),
        }
        return custom_links(context, self.site)

    def test_no_permission_hides_link(self):
        # A user without the view_customlink permission must not see the link.
        user = User.objects.create_user(username='user1')
        self.assertNotIn('Link 1', self.render(user))

    def test_constrained_permission_hides_link(self):
        # A user granted view_customlink via a constraint that excludes the link must not see it (#22439).
        user = User.objects.create_user(username='user2')
        permission = ObjectPermission.objects.create(
            name='Constrained custom links',
            actions=['view'],
            constraints={'name': 'Some Other Link'}  # Does not match Custom Link 1
        )
        permission.object_types.set([ObjectType.objects.get_for_model(CustomLink)])
        permission.users.set([user])

        # Re-fetch to clear any cached permissions
        user = User.objects.get(pk=user.pk)
        self.assertNotIn('Link 1', self.render(user))

    def test_permitted_link_is_shown(self):
        # A user granted view_customlink covering the link must see it.
        user = User.objects.create_user(username='user3')
        permission = ObjectPermission.objects.create(
            name='Custom links',
            actions=['view'],
            constraints={'name': 'Custom Link 1'}  # Matches Custom Link 1
        )
        permission.object_types.set([ObjectType.objects.get_for_model(CustomLink)])
        permission.users.set([user])

        # Re-fetch to clear any cached permissions
        user = User.objects.get(pk=user.pk)
        self.assertIn('Link 1', self.render(user))


class CustomLinkRequestSanitizationTest(TestCase):
    """
    The custom_links template tag must not expose sensitive request attributes (cookies, headers,
    session state) to custom link templates (see #22607 / CVE-2026-56715).
    """
    SECRET = 'super-secret-session-value'

    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.create(name='Site 1', slug='site-1')
        cls.user = User.objects.create_superuser(username='admin')

    def render_link(self, link_text):
        custom_link = CustomLink.objects.create(
            name=f'Custom Link for {link_text!r}',
            enabled=True,
            weight=100,
            new_window=False,
            link_text=link_text,
            link_url='http://example.com/'
        )
        custom_link.object_types.set([ObjectType.objects.get_for_model(Site)])

        request = RequestFactory().get('/dcim/sites/1/?foo=bar')
        request.user = self.user
        request.COOKIES['sessionid'] = self.SECRET
        context = {
            'request': request,
            'user': self.user,
            'perms': PermWrapper(self.user),
        }
        return custom_links(context, self.site)

    def test_cookies_not_exposed(self):
        # A link interpolating request.COOKIES must not leak the session cookie value.
        output = self.render_link("{{ request.COOKIES.get('sessionid') }}")
        self.assertNotIn(self.SECRET, output)

    def test_meta_not_exposed(self):
        # request.META (which carries cookies, auth headers, etc.) must not be accessible.
        output = self.render_link('{{ request.META }}')
        self.assertNotIn(self.SECRET, output)

    def test_headers_not_exposed(self):
        # request.headers must not be accessible.
        output = self.render_link('{{ request.headers }}')
        self.assertNotIn(self.SECRET, output)

    def test_safe_attributes_still_available(self):
        # Benign attributes remain accessible for backward compatibility.
        self.assertIn('/dcim/sites/1/', self.render_link('{{ request.path }}'))
        self.assertIn('bar', self.render_link("{{ request.GET.get('foo') }}"))
        self.assertIn('admin', self.render_link('{{ request.user }}'))


class CustomLinkRenderErrorEscapingTest(TestCase):
    """
    When CustomLink.render() raises, the exception-fallback markup must escape the (attacker-controllable)
    CustomLink name before it is returned via mark_safe() (see NB-3004).
    """

    XSS_NAME = '<img src=x onerror=alert(1)>'
    ESCAPED_NAME = '&lt;img src=x onerror=alert(1)&gt;'

    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.create(name='Site 1', slug='site-1')

    def render(self, user):
        request = RequestFactory().get('/')
        request.user = user
        context = {
            'request': request,
            'user': user,
            'perms': PermWrapper(user),
        }
        return custom_links(context, self.site)

    def make_user_with_view_permission(self, username):
        user = User.objects.create_user(username=username)
        permission = ObjectPermission.objects.create(name=f'{username} custom links', actions=['view'])
        permission.object_types.set([ObjectType.objects.get_for_model(CustomLink)])
        permission.users.set([user])
        # Re-fetch to clear any cached permissions
        return User.objects.get(pk=user.pk)

    def test_render_error_escapes_name(self):
        # A CustomLink whose render() raises must have its name escaped in the error fallback.
        custom_link = CustomLink.objects.create(
            name=self.XSS_NAME,
            enabled=True,
            link_text='{{ 1 / 0 }}',  # Raises ZeroDivisionError during render
            link_url='http://example.com/',
        )
        custom_link.object_types.set([ObjectType.objects.get_for_model(Site)])

        rendered = self.render(self.make_user_with_view_permission('user1'))
        self.assertNotIn(self.XSS_NAME, rendered)
        self.assertIn(self.ESCAPED_NAME, rendered)

    def test_render_error_escapes_grouped_name(self):
        # The grouped-link error fallback must likewise escape the name.
        custom_link = CustomLink.objects.create(
            name=self.XSS_NAME,
            enabled=True,
            group_name='Group 1',
            link_text='{{ 1 / 0 }}',  # Raises ZeroDivisionError during render
            link_url='http://example.com/',
        )
        custom_link.object_types.set([ObjectType.objects.get_for_model(Site)])

        rendered = self.render(self.make_user_with_view_permission('user2'))
        self.assertNotIn(self.XSS_NAME, rendered)
        self.assertIn(self.ESCAPED_NAME, rendered)
