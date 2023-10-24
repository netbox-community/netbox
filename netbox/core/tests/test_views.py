from django.utils import timezone

from utilities.testing import ViewTestCases, create_tags
from ..models import *


class DataSourceTestCase(ViewTestCases.PrimaryObjectViewTestCase):
    model = DataSource

    @classmethod
    def setUpTestData(cls):
        data_sources = (
            DataSource(name='Data Source 1', type='local', source_url='file:///var/tmp/source1/'),
            DataSource(name='Data Source 2', type='local', source_url='file:///var/tmp/source2/'),
            DataSource(name='Data Source 3', type='local', source_url='file:///var/tmp/source3/'),
        )
        DataSource.objects.bulk_create(data_sources)

        tags = create_tags('Alpha', 'Bravo', 'Charlie')

        cls.form_data = {
            'name': 'Data Source X',
            'type': 'git',
            'source_url': 'http:///exmaple/com/foo/bar/',
            'description': 'Something',
            'comments': 'Foo bar baz',
            'tags': [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,type,source_url,enabled",
            "Data Source 4,local,file:///var/tmp/source4/,true",
            "Data Source 5,local,file:///var/tmp/source4/,true",
            "Data Source 6,git,http:///exmaple/com/foo/bar/,false",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{data_sources[0].pk},Data Source 7,New description7",
            f"{data_sources[1].pk},Data Source 8,New description8",
            f"{data_sources[2].pk},Data Source 9,New description9",
        )

        cls.bulk_edit_data = {
            'enabled': False,
            'description': 'New description',
        }


class DataFileTestCase(
    ViewTestCases.GetObjectViewTestCase,
    ViewTestCases.DeleteObjectViewTestCase,
    ViewTestCases.ListObjectsViewTestCase,
    ViewTestCases.BulkDeleteObjectsViewTestCase,
):
    model = DataFile

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
