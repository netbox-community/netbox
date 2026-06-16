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
