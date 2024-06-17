import uuid
from datetime import datetime, timezone

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from dcim.models import Site
from ipam.models import IPAddress
from users.models import User
from utilities.testing import BaseFilterSetTests, ChangeLoggedFilterSetTests
from ..choices import *
from ..filtersets import *
from ..models import *


class DataSourceTestCase(TestCase, ChangeLoggedFilterSetTests):
    queryset = DataSource.objects.all()
    filterset = DataSourceFilterSet
    ignore_fields = ('ignore_rules', 'parameters')

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
    ignore_fields = ('data',)

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


class ObjectChangeTestCase(TestCase, BaseFilterSetTests):
    queryset = ObjectChange.objects.all()
    filterset = ObjectChangeFilterSet
    ignore_fields = ('prechange_data', 'postchange_data')

    @classmethod
    def setUpTestData(cls):
        users = (
            User(username='user1'),
            User(username='user2'),
            User(username='user3'),
        )
        User.objects.bulk_create(users)

        site = Site.objects.create(name='Test Site 1', slug='test-site-1')
        ipaddress = IPAddress.objects.create(address='192.0.2.1/24')

        object_changes = (
            ObjectChange(
                user=users[0],
                user_name=users[0].username,
                request_id=uuid.uuid4(),
                action=ObjectChangeActionChoices.ACTION_CREATE,
                changed_object=site,
                object_repr=str(site),
                postchange_data={'name': site.name, 'slug': site.slug}
            ),
            ObjectChange(
                user=users[0],
                user_name=users[0].username,
                request_id=uuid.uuid4(),
                action=ObjectChangeActionChoices.ACTION_UPDATE,
                changed_object=site,
                object_repr=str(site),
                postchange_data={'name': site.name, 'slug': site.slug}
            ),
            ObjectChange(
                user=users[1],
                user_name=users[1].username,
                request_id=uuid.uuid4(),
                action=ObjectChangeActionChoices.ACTION_DELETE,
                changed_object=site,
                object_repr=str(site),
                postchange_data={'name': site.name, 'slug': site.slug}
            ),
            ObjectChange(
                user=users[1],
                user_name=users[1].username,
                request_id=uuid.uuid4(),
                action=ObjectChangeActionChoices.ACTION_CREATE,
                changed_object=ipaddress,
                object_repr=str(ipaddress),
                postchange_data={'address': ipaddress.address, 'status': ipaddress.status}
            ),
            ObjectChange(
                user=users[2],
                user_name=users[2].username,
                request_id=uuid.uuid4(),
                action=ObjectChangeActionChoices.ACTION_UPDATE,
                changed_object=ipaddress,
                object_repr=str(ipaddress),
                postchange_data={'address': ipaddress.address, 'status': ipaddress.status}
            ),
            ObjectChange(
                user=users[2],
                user_name=users[2].username,
                request_id=uuid.uuid4(),
                action=ObjectChangeActionChoices.ACTION_DELETE,
                changed_object=ipaddress,
                object_repr=str(ipaddress),
                postchange_data={'address': ipaddress.address, 'status': ipaddress.status}
            ),
        )
        ObjectChange.objects.bulk_create(object_changes)

    def test_q(self):
        params = {'q': 'Site 1'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_user(self):
        params = {'user_id': User.objects.filter(username__in=['user1', 'user2']).values_list('pk', flat=True)}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'user': ['user1', 'user2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_user_name(self):
        params = {'user_name': ['user1', 'user2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_changed_object_type(self):
        params = {'changed_object_type': 'dcim.site'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {'changed_object_type_id': [ContentType.objects.get(app_label='dcim', model='site').pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
