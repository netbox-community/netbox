from django.test import TestCase
from django.test import override_settings

from circuits.api.serializers import ProviderSerializer
from circuits.forms import ProviderForm
from circuits.models import Provider
from ipam.models import ASN, RIR
from netbox.choices import CSVDelimiterChoices, ImportFormatChoices
from utilities.testing import APITestCase, ModelViewTestCase, create_tags, post_data


class ModelFormCustomValidationTest(TestCase):

    @override_settings(CUSTOM_VALIDATORS={
        'circuits.provider': [
            {'tags': {'required': True}}
        ]
    })
    def test_tags_validation(self):
        """
        Check that custom validation rules work for tag assignment.
        """
        data = {
            'name': 'Provider 1',
            'slug': 'provider-1',
        }
        form = ProviderForm(data)
        self.assertFalse(form.is_valid())

        tags = create_tags('Tag1', 'Tag2', 'Tag3')
        data['tags'] = [tag.pk for tag in tags]
        form = ProviderForm(data)
        self.assertTrue(form.is_valid())

    @override_settings(CUSTOM_VALIDATORS={
        'circuits.provider': [
            {'asns': {'required': True}}
        ]
    })
    def test_m2m_validation(self):
        """
        Check that custom validation rules work for many-to-many fields.
        """
        data = {
            'name': 'Provider 1',
            'slug': 'provider-1',
        }
        form = ProviderForm(data)
        self.assertFalse(form.is_valid())

        rir = RIR.objects.create(name='RIR 1', slug='rir-1')
        asns = ASN.objects.bulk_create((
            ASN(rir=rir, asn=65001),
            ASN(rir=rir, asn=65002),
            ASN(rir=rir, asn=65003),
        ))
        data['asns'] = [asn.pk for asn in asns]
        form = ProviderForm(data)
        self.assertTrue(form.is_valid())


class BulkEditCustomValidationTest(ModelViewTestCase):
    model = Provider

    @classmethod
    def setUpTestData(cls):
        rir = RIR.objects.create(name='RIR 1', slug='rir-1')
        asns = ASN.objects.bulk_create((
            ASN(rir=rir, asn=65001),
            ASN(rir=rir, asn=65002),
            ASN(rir=rir, asn=65003),
        ))

        providers = (
            Provider(name='Provider 1', slug='provider-1'),
            Provider(name='Provider 2', slug='provider-2'),
            Provider(name='Provider 3', slug='provider-3'),
        )
        Provider.objects.bulk_create(providers)
        for provider in providers:
            provider.asns.set(asns)

    @override_settings(CUSTOM_VALIDATORS={
        'circuits.provider': [
            {'asns': {'required': True}}
        ]
    })
    def test_bulk_edit_without_m2m(self):
        """
        Check that custom validation rules do not interfere with bulk editing.
        """
        data = {
            'pk': list(Provider.objects.values_list('pk', flat=True)),
            '_apply': '',
            'description': 'New description',
        }
        self.add_permissions(
            'circuits.view_provider',
            'circuits.change_provider',
        )

        # Bulk edit the description without changing ASN assignments
        request = {
            'path': self._get_url('bulk_edit'),
            'data': post_data(data),
        }
        response = self.client.post(**request)
        self.assertHttpStatus(response, 302)
        self.assertEqual(
            Provider.objects.filter(description=data['description']).count(),
            len(data['pk'])
        )

    @override_settings(CUSTOM_VALIDATORS={
        'circuits.provider': [
            {'asns': {'required': True}}
        ]
    })
    def test_bulk_edit_m2m(self):
        """
        Test that custom validation rules are enforced during bulk editing.
        """
        data = {
            'pk': list(Provider.objects.values_list('pk', flat=True)),
            '_apply': '',
            'description': 'New description',
        }
        self.add_permissions(
            'circuits.view_provider',
            'circuits.change_provider',
            'ipam.view_asn',
        )

        # Change the ASN assignments
        asn = ASN.objects.first()
        data['asns'] = [asn.pk]
        request = {
            'path': self._get_url('bulk_edit'),
            'data': post_data(data),
        }
        response = self.client.post(**request)
        self.assertHttpStatus(response, 302)
        for provider in Provider.objects.all():
            self.assertEqual(len(provider.asns.all()), 1)

        # Attempt to remove the ASN assignments
        data.pop('asns')
        data['_nullify'] = 'asns'
        request = {
            'path': self._get_url('bulk_edit'),
            'data': post_data(data),
        }
        response = self.client.post(**request)
        self.assertHttpStatus(response, 200)
        for provider in Provider.objects.all():
            self.assertTrue(provider.asns.exists())


class BulkImportCustomValidationTest(ModelViewTestCase):
    model = Provider

    @classmethod
    def setUpTestData(cls):
        create_tags('Tag1', 'Tag2', 'Tag3')

    @override_settings(CUSTOM_VALIDATORS={
        'circuits.provider': [
            {'tags': {'required': True}}
        ]
    })
    def test_bulk_import_invalid(self):
        """
        Test that custom validation rules are enforced during bulk import.
        """
        csv_data = (
            "name,slug",
            "Provider 1,provider-1",
            "Provider 2,provider-2",
            "Provider 3,provider-3",
        )
        data = {
            'data': '\n'.join(csv_data),
            'format': ImportFormatChoices.CSV,
            'csv_delimiter': CSVDelimiterChoices.COMMA,
        }
        self.add_permissions(
            'circuits.view_provider',
            'circuits.add_provider',
            'extras.view_tag',
        )

        # Attempt to import providers without tags
        request = {
            'path': self._get_url('import'),
            'data': post_data(data),
        }
        response = self.client.post(**request)
        self.assertHttpStatus(response, 200)
        self.assertFalse(Provider.objects.exists())

        # Import providers successfully with tag assignments
        csv_data = (
            "name,slug,tags",
            "Provider 1,provider-1,tag1",
            "Provider 2,provider-2,tag2",
            "Provider 3,provider-3,tag3",
        )
        data['data'] = '\n'.join(csv_data)
        request = {
            'path': self._get_url('import'),
            'data': post_data(data),
        }
        response = self.client.post(**request)
        self.assertHttpStatus(response, 302)
        self.assertTrue(Provider.objects.exists())


class APISerializerCustomValidationTest(APITestCase):

    @override_settings(CUSTOM_VALIDATORS={
        'circuits.provider': [
            {'tags': {'required': True}}
        ]
    })
    def test_tags_validation(self):
        """
        Check that custom validation rules work for tag assignment.
        """
        data = {
            'name': 'Provider 1',
            'slug': 'provider-1',
        }
        serializer = ProviderSerializer(data=data)
        self.assertFalse(serializer.is_valid())

        tags = create_tags('Tag1', 'Tag2', 'Tag3')
        data['tags'] = [tag.pk for tag in tags]
        serializer = ProviderSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    @override_settings(CUSTOM_VALIDATORS={
        'circuits.provider': [
            {'asns': {'required': True}}
        ]
    })
    def test_m2m_validation(self):
        """
        Check that custom validation rules work for many-to-many fields.
        """
        data = {
            'name': 'Provider 1',
            'slug': 'provider-1',
        }
        serializer = ProviderSerializer(data=data)
        self.assertFalse(serializer.is_valid())

        rir = RIR.objects.create(name='RIR 1', slug='rir-1')
        asns = ASN.objects.bulk_create((
            ASN(rir=rir, asn=65001),
            ASN(rir=rir, asn=65002),
            ASN(rir=rir, asn=65003),
        ))
        data['asns'] = [asn.pk for asn in asns]
        serializer = ProviderSerializer(data=data)
        self.assertTrue(serializer.is_valid())
