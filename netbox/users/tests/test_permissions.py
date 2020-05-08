from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission, User
from django.test import TestCase, override_settings

from dcim.models import Site
from tenancy.models import Tenant
from users.models import ObjectPermission


class UserConfigTest(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(username='testuser')

    @classmethod
    def setUpTestData(cls):

        tenant = Tenant.objects.create(name='Tenant 1', slug='tenant-1')
        Site.objects.bulk_create((
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2', tenant=tenant),
            Site(name='Site 3', slug='site-3'),
        ))

    @override_settings(EXEMPT_VIEW_PERMISSIONS=[])
    def test_permission_view_object(self):

        # Sanity check to ensure the user has no model-level permission
        self.assertFalse(self.user.has_perm('dcim.view_site'))

        # The permission check for a specific object should fail.
        sites = Site.objects.all()
        self.assertFalse(self.user.has_perm('dcim.view_site', sites[0]))

        # Create and assign a new ObjectPermission specifying the first site by name.
        ct = ContentType.objects.get_for_model(sites[0])
        object_perm = ObjectPermission(
            model=ct,
            attrs={'name': 'Site 1'},
            can_view=True
        )
        object_perm.save()
        self.user.object_permissions.add(object_perm)

        # The test user should have permission to view only the first site.
        self.assertTrue(self.user.has_perm('dcim.view_site', sites[0]))
        self.assertFalse(self.user.has_perm('dcim.view_site', sites[1]))

        # Create a second ObjectPermission matching sites by assigned tenant.
        object_perm = ObjectPermission(
            model=ct,
            attrs={'tenant__name': 'Tenant 1'},
            can_view=True
        )
        object_perm.save()
        self.user.object_permissions.add(object_perm)

        # The user should now able to view the first two sites, but not the third.
        self.assertTrue(self.user.has_perm('dcim.view_site', sites[0]))
        self.assertTrue(self.user.has_perm('dcim.view_site', sites[1]))
        self.assertFalse(self.user.has_perm('dcim.view_site', sites[2]))
