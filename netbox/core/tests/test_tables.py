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
    Test the rendering, export, and ordering behavior of JobTable's execution_time column.
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
            Job(
                name='negative', job_id=uuid.uuid4(), status=JobStatusChoices.STATUS_COMPLETED,
                started=now, completed=now, execution_time=timedelta(seconds=-5),
            ),
            Job(
                name='running', job_id=uuid.uuid4(), status=JobStatusChoices.STATUS_RUNNING,
                started=now - timedelta(minutes=5),
            ),
            Job(name='pending', job_id=uuid.uuid4(), status=JobStatusChoices.STATUS_PENDING),
        ))

    def _render(self, name):
        table = JobTable(Job.objects.filter(name=name))
        table.columns.show('execution_time')
        return str(next(iter(table.rows)).get_cell('execution_time'))

    def test_render_completed_job(self):
        self.assertEqual(self._render('completed-90s'), '1m 30s')
        self.assertEqual(self._render('completed-long'), '2d 3h')

    def test_render_subsecond_job(self):
        # Sub-second jobs report millisecond precision rather than reading as zero
        self.assertEqual(self._render('completed-subsecond'), '0.43s')

    def test_render_negative_execution_time(self):
        # A negative stored value (e.g. from clock skew) never renders as negative
        self.assertEqual(self._render('negative'), '0s')

    def test_render_running_job(self):
        """
        A running job has no recorded execution time, so the column shows the time elapsed so far,
        visually distinguished from a completed job's final value.
        """
        rendered = self._render('running')
        self.assertIn('5m', rendered)
        self.assertIn('text-primary', rendered)

    def test_render_job_never_started(self):
        table = JobTable(Job.objects.filter(name='pending'))
        table.columns.show('execution_time')
        row = next(iter(table.rows))
        self.assertEqual(str(row.get_cell('execution_time')), table.default)

    def test_export_value_is_raw_seconds(self):
        table = JobTable(Job.objects.filter(name='completed-90s'))
        table.columns.show('execution_time')
        rows = list(table.as_values())
        index = rows[0].index('Execution Time')
        self.assertEqual(rows[1][index], 90.0)

    def test_export_value_of_job_never_started(self):
        table = JobTable(Job.objects.filter(name='pending'))
        table.columns.show('execution_time')
        rows = list(table.as_values())
        index = rows[0].index('Execution Time')
        self.assertIsNone(rows[1][index])

    def test_ordering_sorts_nulls_last(self):
        """
        Jobs with no recorded execution time must sort last in both directions, so that sorting by
        execution time does not bury the longest-running jobs behind pending ones.
        """
        recorded = ['negative', 'completed-subsecond', 'completed-90s', 'completed-long']
        unrecorded = {'running', 'pending'}

        for descending, expected in (
            (False, recorded),
            (True, list(reversed(recorded))),
        ):
            with self.subTest(descending=descending):
                table = JobTable(Job.objects.all())
                queryset, _modified = table.columns['execution_time'].order(Job.objects.all(), descending)
                names = list(queryset.values_list('name', flat=True))
                self.assertEqual(names[:len(recorded)], expected)
                self.assertEqual(set(names[len(recorded):]), unrecorded)


class ObjectChangeTableTestCase(TableTestCases.StandardTableTestCase):
    table = ObjectChangeTable
    queryset_sources = [
        ('ObjectChangeListView', ObjectChange.objects.all()),
    ]


class ConfigRevisionTableTestCase(TableTestCases.StandardTableTestCase):
    table = ConfigRevisionTable
