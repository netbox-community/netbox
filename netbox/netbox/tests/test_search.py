from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from dcim.models import Site
from dcim.search import SiteIndex
from extras.models import CachedValue
from netbox.search.backends import search_backend


class SearchBackendTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create sites with a value for each cacheable field defined on SiteIndex
        sites = (
            Site(
                name='Site 1',
                slug='site-1',
                facility='Alpha',
                description='First test site',
                physical_address='123 Fake St Lincoln NE 68588',
                shipping_address='123 Fake St Lincoln NE 68588',
                comments='Lorem ipsum etcetera'
            ),
            Site(
                name='Site 2',
                slug='site-2',
                facility='Bravo',
                description='Second test site',
                physical_address='725 Cyrus Valleys Suite 761 Douglasfort NE 57761',
                shipping_address='725 Cyrus Valleys Suite 761 Douglasfort NE 57761',
                comments='Lorem ipsum etcetera'
            ),
            Site(
                name='Site 3',
                slug='site-3',
                facility='Charlie',
                description='Third test site',
                physical_address='2321 Dovie Dale East Cristobal AK 71959',
                shipping_address='2321 Dovie Dale East Cristobal AK 71959',
                comments='Lorem ipsum etcetera'
            ),
        )
        Site.objects.bulk_create(sites)

    def test_cache_single_object(self):
        """
        Test that a single object is cached appropriately
        """
        site = Site.objects.first()
        search_backend.cache(site)

        content_type = ContentType.objects.get_for_model(Site)
        self.assertEqual(
            CachedValue.objects.filter(object_type=content_type, object_id=site.pk).count(),
            len(SiteIndex.fields)
        )
        for field_name, weight in SiteIndex.fields:
            self.assertTrue(
                CachedValue.objects.filter(
                    object_type=content_type,
                    object_id=site.pk,
                    field=field_name,
                    value=getattr(site, field_name),
                    weight=weight
                ),
            )

    def test_cache_multiple_objects(self):
        """
        Test that multiples objects are cached appropriately
        """
        sites = Site.objects.all()
        search_backend.cache(sites)

        content_type = ContentType.objects.get_for_model(Site)
        self.assertEqual(
            CachedValue.objects.filter(object_type=content_type).count(),
            len(SiteIndex.fields) * sites.count()
        )
        for site in sites:
            for field_name, weight in SiteIndex.fields:
                self.assertTrue(
                    CachedValue.objects.filter(
                        object_type=content_type,
                        object_id=site.pk,
                        field=field_name,
                        value=getattr(site, field_name),
                        weight=weight
                    ),
                )

    def test_cache_on_save(self):
        """
        Test that an object is automatically cached on calling save().
        """
        site = Site(
            name='Site 4',
            slug='site-4',
            facility='Delta',
            description='Fourth test site',
            physical_address='7915 Lilla Plains West Ladariusport TX 19429',
            shipping_address='7915 Lilla Plains West Ladariusport TX 19429',
            comments='Lorem ipsum etcetera'
        )
        site.save()

        content_type = ContentType.objects.get_for_model(Site)
        self.assertEqual(
            CachedValue.objects.filter(object_type=content_type, object_id=site.pk).count(),
            len(SiteIndex.fields)
        )

    def test_remove_on_delete(self):
        """
        Test that any cached value for an object are automatically removed on delete().
        """
        site = Site.objects.first()
        site.delete()

        content_type = ContentType.objects.get_for_model(Site)
        self.assertFalse(
            CachedValue.objects.filter(object_type=content_type, object_id=site.pk).exists()
        )

    def test_clear_all(self):
        """
        Test that calling clear() on the backend removes all cached entries.
        """
        sites = Site.objects.all()
        search_backend.cache(sites)
        self.assertTrue(
            CachedValue.objects.exists()
        )

        search_backend.clear()
        self.assertFalse(
            CachedValue.objects.exists()
        )

    def test_search(self):
        """
        Test various searches.
        """
        sites = Site.objects.all()
        search_backend.cache(sites)

        results = search_backend.search('site')
        self.assertEqual(len(results), 3)
        results = search_backend.search('first')
        self.assertEqual(len(results), 1)
        results = search_backend.search('xxxxx')
        self.assertEqual(len(results), 0)
