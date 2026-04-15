from django.test import TestCase

from tenancy.models import Contact, ContactGroup


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
