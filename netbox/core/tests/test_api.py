from django.urls import reverse
from django.utils import timezone

from utilities.testing import APITestCase, APIViewTestCases
from ..models import *


class AppTest(APITestCase):

    def test_root(self):
        url = reverse('core-api:api-root')
        response = self.client.get('{}?format=api'.format(url), **self.header)

        self.assertEqual(response.status_code, 200)


class DataSourceTest(APIViewTestCases.APIViewTestCase):
    model = DataSource
    brief_fields = ['display', 'id', 'name', 'url']
    bulk_update_data = {
        'enabled': False,
        'description': 'foo bar baz',
    }

    @classmethod
    def setUpTestData(cls):
        data_sources = (
            DataSource(name='Data Source 1', type='local', source_url='file:///var/tmp/source1/'),
            DataSource(name='Data Source 2', type='local', source_url='file:///var/tmp/source2/'),
            DataSource(name='Data Source 3', type='local', source_url='file:///var/tmp/source3/'),
        )
        DataSource.objects.bulk_create(data_sources)

        cls.create_data = [
            {
                'name': 'Data Source 4',
                'type': 'git',
                'source_url': 'https://example.com/git/source4'
            },
            {
                'name': 'Data Source 5',
                'type': 'git',
                'source_url': 'https://example.com/git/source5'
            },
            {
                'name': 'Data Source 6',
                'type': 'git',
                'source_url': 'https://example.com/git/source6'
            },
        ]


class DataFileTest(
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.GraphQLTestCase
):
    model = DataFile
    brief_fields = ['display', 'id', 'path', 'url']

    @classmethod
    def setUpTestData(cls):
        datasource = DataSource.objects.create(
            name='Data Source 1',
            type='local',
            source_url='file:///var/tmp/source1/'
        )

        data_files = (
            DataFile(
                source=datasource,
                path='dir1/file1.txt',
                last_updated=timezone.now(),
                size=1000,
                hash='442da078f0111cbdf42f21903724f6597c692535f55bdfbbea758a1ae99ad9e1'
            ),
            DataFile(
                source=datasource,
                path='dir1/file2.txt',
                last_updated=timezone.now(),
                size=2000,
                hash='a78168c7c97115bafd96450ed03ea43acec495094c5caa28f0d02e20e3a76cc2'
            ),
            DataFile(
                source=datasource,
                path='dir1/file3.txt',
                last_updated=timezone.now(),
                size=3000,
                hash='12b8827a14c4d5a2f30b6c6e2b7983063988612391c6cbe8ee7493b59054827a'
            ),
        )
        DataFile.objects.bulk_create(data_files)
