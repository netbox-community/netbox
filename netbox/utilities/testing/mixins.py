import itertools
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test.testcases import SerializeMixin
from django_rq import get_queue
from django_rq.workers import get_worker
from rq import SimpleWorker

__all__ = (
    'NormalizedMeasurementTestMixin',
    'RQQueueTestMixin',
)


class RQQueueTestMixin(SerializeMixin):
    """
    Clear RQ queues before and after each test.

    Test classes using this mixin share a single RQ (Redis) instance. Under the parallel
    test runner that Redis is not isolated per worker (unlike the database), so concurrent
    classes that enqueue and assert exact queue counts race each other. SerializeMixin
    holds an exclusive lock on `lockfile`, so no two classes using this mixin run at the
    same time, which removes that cross-worker contention.
    """
    lockfile = __file__
    rq_queue_names = ('default', 'high', 'low')

    @classmethod
    def clear_rq_queues(cls):
        for queue_name in cls.rq_queue_names:
            # Flush only the queue's own database. FLUSHALL would empty every database on the Redis
            # server, including the caching database, whose keys (e.g. the cached config revision)
            # are shared by the other parallel test workers.
            get_queue(queue_name).connection.flushdb()

    def run_rq_jobs(self, *queue_names, burst=True):
        """
        Process queued RQ jobs synchronously for the given queue(s) (defaulting to 'default').

        Uses a non-forking SimpleWorker: the default RQ worker forks a work horse which would
        inherit the test's open database connection. Two processes sharing one connection
        corrupts it — on an SSL-encrypted connection this surfaces as "bad record mac" and
        closes the connection for every subsequent test. SimpleWorker runs jobs in-process,
        so the connection is never shared.
        """
        worker = get_worker(*(queue_names or ('default',)), worker_class=SimpleWorker)
        worker.work(burst=burst)

    def setUp(self):
        super().setUp()

        # Clear all queues before running each test
        self.clear_rq_queues()

    def tearDown(self):
        try:
            # Clear all queues after each test so no leftover jobs leak into the next test suite
            self.clear_rq_queues()
        finally:
            super().tearDown()


class NormalizedMeasurementTestMixin:
    """
    Exercise a database-generated column that normalizes a measurement to its base unit. The column is checked
    against the matching to_*() helper for every unit choice, across each write path: save(), QuerySet.update(),
    bulk_update(), and bulk_create(). Subclasses set the attributes below and implement create_instance().
    """
    model = None
    value_field = None       # e.g. 'distance'
    unit_field = None        # e.g. 'distance_unit'
    normalized_field = None  # e.g. '_abs_distance'
    unit_choices = None      # e.g. DistanceUnitChoices
    converter = None         # e.g. staticmethod(to_meters)
    value = Decimal('123.45')

    def setUp(self):
        super().setUp()
        self.sequence = itertools.count(1)

    def create_instance(self, **attrs):
        """
        Return an unsaved instance of the model with the given attributes set. Each call must yield an instance
        which can be saved alongside those from previous calls; next(self.sequence) supplies a unique number.
        """
        raise NotImplementedError

    @property
    def units(self):
        return self.unit_choices.values()

    def assertNormalized(self, instance, value, unit):
        """
        Assert that the stored normalized value matches the converter's result for the given measurement.
        """
        expected = self.converter(value, unit) if value is not None and unit else None
        instance.refresh_from_db()
        self.assertEqual(getattr(instance, self.normalized_field), expected)

    def test_save(self):
        for unit in self.units:
            with self.subTest(unit=unit):
                instance = self.create_instance(**{self.value_field: self.value, self.unit_field: unit})
                instance.save()
                # The database returns the computed value on save, so it is available without a refresh
                self.assertEqual(getattr(instance, self.normalized_field), self.converter(self.value, unit))
                self.assertNormalized(instance, self.value, unit)

    def test_save_existing(self):
        instance = self.create_instance()
        instance.save()
        for unit in self.units:
            with self.subTest(unit=unit):
                setattr(instance, self.value_field, self.value)
                setattr(instance, self.unit_field, unit)
                instance.save()
                # An UPDATE also returns the computed value, so change logging sees the current value
                self.assertEqual(getattr(instance, self.normalized_field), self.converter(self.value, unit))
                self.assertNormalized(instance, self.value, unit)

    def test_update(self):
        instance = self.create_instance()
        instance.save()
        for unit in self.units:
            with self.subTest(unit=unit):
                self.model.objects.filter(pk=instance.pk).update(**{
                    self.value_field: self.value,
                    self.unit_field: unit,
                })
                self.assertNormalized(instance, self.value, unit)

    def test_bulk_update(self):
        instance = self.create_instance()
        instance.save()
        for unit in self.units:
            with self.subTest(unit=unit):
                setattr(instance, self.value_field, self.value)
                setattr(instance, self.unit_field, unit)
                self.model.objects.bulk_update([instance], [self.value_field, self.unit_field])
                self.assertNormalized(instance, self.value, unit)

    def test_bulk_create(self):
        instances = self.model.objects.bulk_create([
            self.create_instance(**{self.value_field: self.value, self.unit_field: unit})
            for unit in self.units
        ])
        for instance, unit in zip(instances, self.units):
            with self.subTest(unit=unit):
                self.assertNormalized(instance, self.value, unit)

    def test_negative_value_rejected(self):
        """
        A negative measurement must fail validation on the source field.
        """
        instance = self.create_instance(**{self.value_field: -self.value, self.unit_field: self.units[0]})
        with self.assertRaises(ValidationError) as cm:
            instance.full_clean()
        self.assertIn(self.value_field, cm.exception.error_dict)

    def test_negative_value_rejected_by_database(self):
        """
        Write paths which skip validation must still be unable to store a negative measurement.
        """
        unit = self.units[0]
        negative = {self.value_field: -self.value, self.unit_field: unit}
        instance = self.create_instance(**{self.value_field: self.value, self.unit_field: unit})
        instance.save()

        def assert_rejected(label, write):
            with self.subTest(write_path=label):
                with self.assertRaises(IntegrityError), transaction.atomic():
                    write()

        def save():
            for attr, value in negative.items():
                setattr(instance, attr, value)
            instance.save()

        def bulk_update():
            for attr, value in negative.items():
                setattr(instance, attr, value)
            self.model.objects.bulk_update([instance], list(negative))

        assert_rejected('save', save)
        assert_rejected('update', lambda: self.model.objects.filter(pk=instance.pk).update(**negative))
        assert_rejected('bulk_update', bulk_update)
        assert_rejected('bulk_create', lambda: self.model.objects.bulk_create([self.create_instance(**negative)]))

    def test_null_without_value_or_unit(self):
        unit = self.units[0]
        instance = self.create_instance(**{self.value_field: self.value, self.unit_field: unit})
        instance.save()
        queryset = self.model.objects.filter(pk=instance.pk)

        queryset.update(**{self.value_field: None})
        self.assertNormalized(instance, None, unit)

        queryset.update(**{self.value_field: self.value, self.unit_field: None})
        self.assertNormalized(instance, self.value, None)
