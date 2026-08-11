from django.db.models import ProtectedError
from django.test import TestCase, tag

from tenancy.models import Contact, ContactGroup, Tenant, TenantGroup


class TenantGroupTestCase(TestCase):

    @tag('regression')  # Ref: #22821
    def test_tenantgroup_deletion_blocked_by_duplicate_ungrouped_name(self):
        """
        Deleting a tenant group must raise ProtectedError when ungrouping its tenant would duplicate
        the name of an already ungrouped tenant.
        """
        group = TenantGroup.objects.create(name='Tenant Group 1', slug='tenant-group-1')
        tenant1 = Tenant.objects.create(name='Tenant 1', slug='tenant-1a', group=group)
        tenant2 = Tenant.objects.create(name='Tenant 1', slug='tenant-1b')

        with self.assertRaises(ProtectedError) as cm:
            group.delete()

        self.assertEqual(
            cm.exception.args[0],
            'Unable to delete tenant group Tenant Group 1. Ungrouping its tenants, including those of any nested '
            'groups, would create duplicate tenant names or slugs.'
        )
        self.assertEqual(set(cm.exception.protected_objects), {tenant1, tenant2})

        # The failed deletion must leave the group and its tenant assignment intact
        self.assertTrue(TenantGroup.objects.filter(pk=group.pk).exists())
        tenant1.refresh_from_db()
        self.assertEqual(tenant1.group, group)

    @tag('regression')  # Ref: #22821
    def test_tenantgroup_deletion_blocked_by_duplicate_ungrouped_slug(self):
        """
        Deleting a tenant group must raise ProtectedError for a slug collision alone, when the
        colliding tenants have differing names.
        """
        group = TenantGroup.objects.create(name='Tenant Group 2', slug='tenant-group-2')
        tenant1 = Tenant.objects.create(name='Tenant 2', slug='duplicate-slug', group=group)
        tenant2 = Tenant.objects.create(name='Tenant 3', slug='duplicate-slug')

        with self.assertRaises(ProtectedError) as cm:
            group.delete()

        self.assertEqual(set(cm.exception.protected_objects), {tenant1, tenant2})
        self.assertTrue(TenantGroup.objects.filter(pk=group.pk).exists())

    @tag('regression')  # Ref: #22821
    def test_tenantgroup_deletion_blocked_by_duplicate_name_in_descendants(self):
        """
        Deleting a parent tenant group must raise ProtectedError when ungrouping the tenants of its
        descendant groups would duplicate a name.
        """
        parent = TenantGroup.objects.create(name='Parent Group', slug='parent-group')
        child1 = TenantGroup.objects.create(name='Child Group 1', slug='child-group-1', parent=parent)
        child2 = TenantGroup.objects.create(name='Child Group 2', slug='child-group-2', parent=parent)
        tenant1 = Tenant.objects.create(name='Tenant 4', slug='tenant-4a', group=child1)
        tenant2 = Tenant.objects.create(name='Tenant 4', slug='tenant-4b', group=child2)

        with self.assertRaises(ProtectedError) as cm:
            parent.delete()

        self.assertEqual(set(cm.exception.protected_objects), {tenant1, tenant2})
        self.assertTrue(TenantGroup.objects.filter(pk=parent.pk).exists())
        self.assertEqual(TenantGroup.objects.filter(pk__in=(child1.pk, child2.pk)).count(), 2)

    def test_tenantgroup_deletion_ungroups_tenants(self):
        """
        Deleting a tenant group whose tenants can be ungrouped safely must succeed and clear the group
        assignment across the whole subtree.
        """
        parent = TenantGroup.objects.create(name='Parent Group', slug='parent-group')
        child = TenantGroup.objects.create(name='Child Group', slug='child-group', parent=parent)
        tenant1 = Tenant.objects.create(name='Tenant 5', slug='tenant-5', group=parent)
        tenant2 = Tenant.objects.create(name='Tenant 6', slug='tenant-6', group=child)

        parent.delete()

        self.assertFalse(TenantGroup.objects.filter(pk__in=(parent.pk, child.pk)).exists())
        tenant1.refresh_from_db()
        tenant2.refresh_from_db()
        self.assertIsNone(tenant1.group)
        self.assertIsNone(tenant2.group)

    def test_tenantgroup_deletion_ignores_tenants_in_unrelated_groups(self):
        """
        Deleting a tenant group must succeed when a tenant outside its subtree shares a name and slug
        with one of its own tenants, as that tenant remains grouped.
        """
        group = TenantGroup.objects.create(name='Tenant Group 3', slug='tenant-group-3')
        unrelated = TenantGroup.objects.create(name='Unrelated Group', slug='unrelated-group')
        tenant = Tenant.objects.create(name='Tenant 7', slug='tenant-7', group=group)
        Tenant.objects.create(name='Tenant 7', slug='tenant-7', group=unrelated)

        group.delete()

        self.assertFalse(TenantGroup.objects.filter(pk=group.pk).exists())
        tenant.refresh_from_db()
        self.assertIsNone(tenant.group)


class ContactGroupTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create a tree of contact groups:
        #  - Group A
        #    - Group A1
        #    - Group A2
        #  - Group B
        cls.group_a = ContactGroup.objects.create(name='Group A', slug='group-a')
        cls.group_a1 = ContactGroup.objects.create(name='Group A1', slug='group-a1', parent=cls.group_a)
        cls.group_a2 = ContactGroup.objects.create(name='Group A2', slug='group-a2', parent=cls.group_a)
        cls.group_b = ContactGroup.objects.create(name='Group B', slug='group-b')

        # Create contacts
        cls.contact1 = Contact.objects.create(name='Contact 1')
        cls.contact2 = Contact.objects.create(name='Contact 2')
        cls.contact3 = Contact.objects.create(name='Contact 3')
        cls.contact4 = Contact.objects.create(name='Contact 4')

    def test_annotate_contacts_direct(self):
        """Contacts assigned directly to a group should be counted."""
        self.contact1.groups.set([self.group_a])
        self.contact2.groups.set([self.group_a])

        queryset = ContactGroup.objects.annotate_contacts()
        self.assertEqual(queryset.get(pk=self.group_a.pk).contact_count, 2)

    def test_annotate_contacts_cumulative(self):
        """Contacts assigned to child groups should be included in the parent's count."""
        self.contact1.groups.set([self.group_a1])
        self.contact2.groups.set([self.group_a2])

        queryset = ContactGroup.objects.annotate_contacts()
        self.assertEqual(queryset.get(pk=self.group_a.pk).contact_count, 2)
        self.assertEqual(queryset.get(pk=self.group_a1.pk).contact_count, 1)
        self.assertEqual(queryset.get(pk=self.group_a2.pk).contact_count, 1)

    def test_annotate_contacts_no_double_counting(self):
        """A contact assigned to multiple child groups must be counted only once for the parent."""
        self.contact1.groups.set([self.group_a1, self.group_a2])

        queryset = ContactGroup.objects.annotate_contacts()
        self.assertEqual(queryset.get(pk=self.group_a.pk).contact_count, 1)

    def test_annotate_contacts_mixed(self):
        """Test a mix of direct and inherited contacts with overlap."""
        self.contact1.groups.set([self.group_a])
        self.contact2.groups.set([self.group_a1])
        self.contact3.groups.set([self.group_a1, self.group_a2])
        self.contact4.groups.set([self.group_b])

        queryset = ContactGroup.objects.annotate_contacts()
        # Group A: contact1 (direct) + contact2 (via A1) + contact3 (via A1 & A2) = 3
        self.assertEqual(queryset.get(pk=self.group_a.pk).contact_count, 3)
        # Group A1: contact2 + contact3 = 2
        self.assertEqual(queryset.get(pk=self.group_a1.pk).contact_count, 2)
        # Group A2: contact3 = 1
        self.assertEqual(queryset.get(pk=self.group_a2.pk).contact_count, 1)
        # Group B: contact4 = 1
        self.assertEqual(queryset.get(pk=self.group_b.pk).contact_count, 1)

    def test_annotate_contacts_empty(self):
        """Groups with no contacts should return a count of zero."""
        queryset = ContactGroup.objects.annotate_contacts()
        self.assertEqual(queryset.get(pk=self.group_a.pk).contact_count, 0)
        self.assertEqual(queryset.get(pk=self.group_b.pk).contact_count, 0)
