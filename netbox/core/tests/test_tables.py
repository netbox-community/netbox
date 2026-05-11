from core.models import ObjectChange
from core.tables import *
from utilities.testing import TableTestCases


class DataSourceTableTestCase(TableTestCases.StandardTableTestCase):
    table = DataSourceTable


class DataFileTableTestCase(TableTestCases.StandardTableTestCase):
    table = DataFileTable


class JobTableTestCase(TableTestCases.StandardTableTestCase):
    table = JobTable


class ObjectChangeTableTestCase(TableTestCases.StandardTableTestCase):
    table = ObjectChangeTable
    queryset_sources = [
        ('ObjectChangeListView', ObjectChange.objects.all()),
    ]


class ConfigRevisionTableTestCase(TableTestCases.StandardTableTestCase):
    table = ConfigRevisionTable
