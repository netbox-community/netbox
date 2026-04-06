from core.models import ObjectChange
from core.tables import *
from utilities.testing import TableTestCases


class DataSourceTableTest(TableTestCases.StandardTableTestCase):
    table = DataSourceTable


class DataFileTableTest(TableTestCases.StandardTableTestCase):
    table = DataFileTable


class JobTableTest(TableTestCases.StandardTableTestCase):
    table = JobTable


class ObjectChangeTableTest(TableTestCases.StandardTableTestCase):
    table = ObjectChangeTable
    queryset_sources = [
        ('ObjectChangeListView', ObjectChange.objects.valid_models()),
    ]


class ConfigRevisionTableTest(TableTestCases.StandardTableTestCase):
    table = ConfigRevisionTable
