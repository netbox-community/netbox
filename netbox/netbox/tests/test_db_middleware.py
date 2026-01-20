"""
Integration tests for database routing middleware.
"""
import time
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from dcim.models import Site, Region
from netbox.db.context_managers import _routing_state


User = get_user_model()


@override_settings(
    DATABASE_ROUTING_ENABLED=True,
    DATABASE_STICKY_SESSION_DURATION=5,
)
class DatabaseMiddlewareTestCase(TestCase):
    """Test the DatabaseRoutingMiddleware integration."""

    @classmethod
    def setUpTestData(cls):
        """Create test user with permissions."""
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        # Give user permissions to create and view sites
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType

        site_ct = ContentType.objects.get_for_model(Site)
        permissions = Permission.objects.filter(
            content_type=site_ct,
            codename__in=['add_site', 'view_site', 'change_site', 'delete_site']
        )
        cls.user.user_permissions.add(*permissions)

    def setUp(self):
        """Create authenticated client."""
        self.client = Client()
        self.client.login(username='testuser', password='testpass')

    def tearDown(self):
        """Clean up routing state."""
        _routing_state.use_primary = False
        _routing_state.writes_occurred = False

    def test_sticky_cookie_not_set_for_read_only_request(self):
        """Read-only requests should not set sticky session cookie."""
        # Create a site to read
        site = Site.objects.create(name='Test Site', slug='test-site')

        # Perform a read operation
        response = self.client.get(reverse('dcim:site', kwargs={'pk': site.pk}))

        # Sticky session cookie should not be set
        self.assertNotIn('db_sticky_until', response.cookies)

    def test_sticky_cookie_set_after_create(self):
        """Creating an object should set sticky session cookie."""
        # Perform a create operation via the UI
        response = self.client.post(
            reverse('dcim:site_add'),
            data={
                'name': 'New Site',
                'slug': 'new-site',
            },
            follow=False
        )

        # Should redirect on success
        self.assertIn(response.status_code, [200, 302])

        # Sticky session cookie should be set
        self.assertIn('db_sticky_until', response.cookies)

        # Cookie should have appropriate attributes
        cookie = response.cookies['db_sticky_until']
        self.assertTrue(cookie['httponly'])
        self.assertEqual(cookie['samesite'], 'Lax')
        self.assertEqual(cookie['path'], '/')

    def test_sticky_cookie_set_after_update(self):
        """Updating an object should set sticky session cookie."""
        # Create a site
        site = Site.objects.create(name='Test Site', slug='test-site')

        # Update the site
        response = self.client.post(
            reverse('dcim:site_edit', kwargs={'pk': site.pk}),
            data={
                'name': 'Updated Site',
                'slug': 'test-site',
            },
            follow=False
        )

        # Sticky session cookie should be set
        self.assertIn('db_sticky_until', response.cookies)

    def test_sticky_cookie_set_after_delete(self):
        """Deleting an object should set sticky session cookie."""
        # Create a site
        site = Site.objects.create(name='Test Site', slug='test-site')

        # Delete the site
        response = self.client.post(
            reverse('dcim:site_delete', kwargs={'pk': site.pk}),
            data={'confirm': True},
            follow=False
        )

        # Sticky session cookie should be set
        self.assertIn('db_sticky_until', response.cookies)

    def test_sticky_session_honored_on_subsequent_request(self):
        """Subsequent requests should honor sticky session cookie."""
        # Create a site to trigger sticky session
        site = Site.objects.create(name='Test Site', slug='test-site')
        response = self.client.post(
            reverse('dcim:site_edit', kwargs={'pk': site.pk}),
            data={
                'name': 'Updated Site',
                'slug': 'test-site',
            },
            follow=False
        )

        # Get the sticky session cookie value
        sticky_cookie = response.cookies.get('db_sticky_until')
        self.assertIsNotNone(sticky_cookie)

        # Make another request with the cookie
        # The middleware should see the cookie and set use_primary
        # We can't directly test middleware state, but we can verify
        # the cookie is being sent
        response2 = self.client.get(reverse('dcim:site_list'))
        self.assertEqual(response2.status_code, 200)

    def test_sticky_cookie_expires(self):
        """Sticky session cookie should have correct expiry."""
        site = Site.objects.create(name='Test Site', slug='test-site')

        before_time = time.time()
        response = self.client.post(
            reverse('dcim:site_edit', kwargs={'pk': site.pk}),
            data={
                'name': 'Updated Site',
                'slug': 'test-site',
            },
            follow=False
        )
        after_time = time.time()

        cookie = response.cookies.get('db_sticky_until')
        self.assertIsNotNone(cookie)

        # Cookie value should be a timestamp
        cookie_value = float(cookie.value)

        # Cookie should expire between 4-6 seconds from now
        # (configured as 5 seconds, but account for test execution time)
        self.assertGreater(cookie_value, before_time + 4)
        self.assertLess(cookie_value, after_time + 6)

    def test_middleware_disabled_when_routing_disabled(self):
        """Middleware should be bypassed when routing is disabled."""
        with self.settings(DATABASE_ROUTING_ENABLED=False):
            site = Site.objects.create(name='Test Site', slug='test-site')

            response = self.client.post(
                reverse('dcim:site_edit', kwargs={'pk': site.pk}),
                data={
                    'name': 'Updated Site',
                    'slug': 'test-site',
                },
                follow=False
            )

            # Cookie should not be set when routing is disabled
            self.assertNotIn('db_sticky_until', response.cookies)


@override_settings(
    DATABASE_ROUTING_ENABLED=True,
    DATABASE_STICKY_SESSION_DURATION=5,
)
class PermissionValidationTestCase(TestCase):
    """Test that permission validation works correctly with database routing."""

    @classmethod
    def setUpTestData(cls):
        """Create test users and data."""
        # User with permissions
        cls.user_with_perms = User.objects.create_user(
            username='user_with_perms',
            password='testpass'
        )
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType

        site_ct = ContentType.objects.get_for_model(Site)
        permissions = Permission.objects.filter(
            content_type=site_ct,
            codename__in=['add_site', 'view_site']
        )
        cls.user_with_perms.user_permissions.add(*permissions)

        # User without permissions
        cls.user_without_perms = User.objects.create_user(
            username='user_without_perms',
            password='testpass'
        )

    def test_permission_validation_succeeds_after_create(self):
        """Permission validation should work correctly after object creation."""
        client = Client()
        client.login(username='user_with_perms', password='testpass')

        # Create a site - should succeed
        response = client.post(
            reverse('dcim:site_add'),
            data={
                'name': 'New Site',
                'slug': 'new-site',
            },
            follow=False
        )

        # Should succeed (redirect or success status)
        self.assertIn(response.status_code, [200, 302])

        # Verify site was created
        self.assertTrue(Site.objects.filter(slug='new-site').exists())

    def test_read_after_write_consistency(self):
        """Objects should be immediately visible after creation."""
        client = Client()
        client.login(username='user_with_perms', password='testpass')

        # Create a site
        response = client.post(
            reverse('dcim:site_add'),
            data={
                'name': 'New Site',
                'slug': 'new-site',
            },
            follow=True  # Follow redirect
        )

        # Should be able to see the site in the response
        # (this tests read-after-write)
        self.assertEqual(response.status_code, 200)

        # Verify we can immediately read the created object
        site = Site.objects.get(slug='new-site')
        self.assertEqual(site.name, 'New Site')
