import uuid
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from core.choices import JobStatusChoices
from core.models import Job, ObjectChange
from core.tables import *
from utilities.testing import TableTestCases


class DataSourceTableTestCase(TableTestCases.StandardTableTestCase):
    table = DataSourceTable


class DataFileTableTestCase(TableTestCases.StandardTableTestCase):
    table = DataFileTable


class JobTableTestCase(TableTestCases.StandardTableTestCase):
    table = JobTable


class JobExecutionTimeColumnTestCase(TestCase):
    """
    Test the rendering and export behavior of JobTable's execution_time column.
    """
    @classmethod
    def setUpTestData(cls):
        now = timezone.now()
        Job.objects.bulk_create((
            Job(
                name='completed-90s', job_id=uuid.uuid4(), status=JobStatusChoices.STATUS_COMPLETED,
                started=now - timedelta(seconds=90), completed=now, execution_time=timedelta(seconds=90),
            ),
            Job(
                name='completed-subsecond', job_id=uuid.uuid4(), status=JobStatusChoices.STATUS_COMPLETED,
                started=now - timedelta(milliseconds=430), completed=now,
                execution_time=timedelta(milliseconds=430),
            ),
            Job(
                name='completed-long', job_id=uuid.uuid4(), status=JobStatusChoices.STATUS_COMPLETED,
                started=now - timedelta(days=2, hours=3), completed=now,
                execution_time=timedelta(days=2, hours=3),
            ),
            Job(name='pending', job_id=uuid.uuid4(), status=JobStatusChoices.STATUS_PENDING),
        ))

    def _table(self, name):
        table = JobTable(Job.objects.filter(name=name))
        table.columns.show('execution_time')
        return table

    def _render(self, name):
        table = self._table(name)
        return str(next(iter(table.rows)).get_cell('execution_time'))

    def test_render_completed_job(self):
        self.assertEqual(self._render('completed-90s'), '1m 30s')
        self.assertEqual(self._render('completed-long'), '2d 3h')

    def test_render_subsecond_job(self):
        # Sub-second jobs report millisecond precision rather than reading as zero
        self.assertEqual(self._render('completed-subsecond'), '0.43s')

    def test_render_job_without_execution_time(self):
        table = self._table('pending')
        self.assertEqual(str(next(iter(table.rows)).get_cell('execution_time')), table.default)

    def _export_value(self, name):
        rows = list(self._table(name).as_values())
        return rows[1][rows[0].index('Execution Time')]

    def test_export_value_is_raw_seconds(self):
        # Exports carry the recorded duration in seconds, not the humanized string
        self.assertEqual(self._export_value('completed-90s'), 90.0)
        self.assertEqual(self._export_value('completed-subsecond'), 0.43)

    def test_export_value_of_job_without_execution_time(self):
        self.assertIsNone(self._export_value('pending'))


class ObjectChangeTableTestCase(TableTestCases.StandardTableTestCase):
    table = ObjectChangeTable
    queryset_sources = [
        ('ObjectChangeListView', ObjectChange.objects.all()),
    ]


class ConfigRevisionTableTestCase(TableTestCases.StandardTableTestCase):
    table = ConfigRevisionTable
