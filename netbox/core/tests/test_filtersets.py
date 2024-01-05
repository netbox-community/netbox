from datetime import datetime, timezone

from django.test import TestCase
from utilities.testing import ChangeLoggedFilterSetTests
from ..choices import *
from ..filtersets import *
from ..models import *


class DataSourceTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = DataSource.objects.all()
    filterset = DataSourceFilterSet

    @classmethod
    def setUpTestData(cls):
        data_sources = (
            DataSource(
                name='Data Source 1',
                type='local',
                source_url='file:///var/tmp/source1/',
                status=DataSourceStatusChoices.NEW,
                enabled=True,
                description='foobar1'
            ),
            DataSource(
                name='Data Source 2',
                type='local',
                source_url='file:///var/tmp/source2/',
                status=DataSourceStatusChoices.SYNCING,
                enabled=True,
                description='foobar2'
            ),
            DataSource(
                name='Data Source 3',
                type='git',
                source_url='https://example.com/git/source3',
                status=DataSourceStatusChoices.COMPLETED,
                enabled=False
            ),
        )
        DataSource.objects.bulk_create(data_sources)

    def test_q(self):
        params = {'q': 'foobar1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Data Source 1', 'Data Source 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {'description': ['foobar1', 'foobar2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_type(self):
        params = {'type': ['local']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_enabled(self):
        params = {'enabled': 'true'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'enabled': 'false'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_status(self):
        params = {'status': [DataSourceStatusChoices.NEW, DataSourceStatusChoices.SYNCING]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class DataFileTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = DataFile.objects.all()
    filterset = DataFileFilterSet

    @classmethod
    def setUpTestData(cls):
        data_sources = (
            DataSource(name='Data Source 1', type='local', source_url='file:///var/tmp/source1/'),
            DataSource(name='Data Source 2', type='local', source_url='file:///var/tmp/source2/'),
            DataSource(name='Data Source 3', type='local', source_url='file:///var/tmp/source3/'),
        )
        DataSource.objects.bulk_create(data_sources)

        data_files = (
            DataFile(
                source=data_sources[0],
                path='dir1/file1.txt',
                last_updated=datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
                size=1000,
                hash='442da078f0111cbdf42f21903724f6597c692535f55bdfbbea758a1ae99ad9e1'
            ),
            DataFile(
                source=data_sources[1],
                path='dir1/file2.txt',
                last_updated=datetime(2023, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
                size=2000,
                hash='a78168c7c97115bafd96450ed03ea43acec495094c5caa28f0d02e20e3a76cc2'
            ),
            DataFile(
                source=data_sources[2],
                path='dir1/file3.txt',
                last_updated=datetime(2023, 1, 3, 0, 0, 0, tzinfo=timezone.utc),
                size=3000,
                hash='12b8827a14c4d5a2f30b6c6e2b7983063988612391c6cbe8ee7493b59054827a'
            ),
        )
        DataFile.objects.bulk_create(data_files)

    def test_q(self):
        params = {'q': 'file1.txt'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_source(self):
        sources = DataSource.objects.all()
        params = {'source_id': [sources[0].pk, sources[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'source': [sources[0].name, sources[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_path(self):
        params = {'path': ['dir1/file1.txt', 'dir1/file2.txt']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_size(self):
        params = {'size': [1000, 2000]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_hash(self):
        params = {'hash': [
            '442da078f0111cbdf42f21903724f6597c692535f55bdfbbea758a1ae99ad9e1',
            'a78168c7c97115bafd96450ed03ea43acec495094c5caa28f0d02e20e3a76cc2',
        ]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
