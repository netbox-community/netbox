"""
Unit tests for database routing functionality.
"""
from django.conf import settings
from django.db import connection, transaction
from django.test import TestCase, override_settings
from unittest.mock import Mock, patch

from dcim.models import Site
from netbox.db.context_managers import _routing_state, use_primary_db
from netbox.db.routers import ReadWriteRouter


class DatabaseRouterTestCase(TestCase):
    """Test the ReadWriteRouter database routing logic."""

    def setUp(self):
        """Set up test router instance."""
        self.router = ReadWriteRouter()
        # Ensure clean state
        _routing_state.use_primary = False
        _routing_state.writes_occurred = False

    def tearDown(self):
        """Clean up routing state."""
        _routing_state.use_primary = False
        _routing_state.writes_occurred = False

    @override_settings(DATABASE_ROUTING_ENABLED=False)
    def test_routing_disabled_uses_default(self):
        """When routing is disabled, all reads should use default database."""
        db = self.router.db_for_read(Site)
        self.assertEqual(db, 'default')

    @override_settings(
        DATABASE_ROUTING_ENABLED=True,
        DATABASES={
            'default': {'ENGINE': 'django.db.backends.postgresql', 'NAME': 'test'},
            'replica': {'ENGINE': 'django.db.backends.postgresql', 'NAME': 'test'},
        }
    )
    def test_reads_use_replica_when_safe(self):
        """When safe, reads should use replica database."""
        _routing_state.use_primary = False
        db = self.router.db_for_read(Site)
        self.assertEqual(db, 'replica')

    @override_settings(DATABASE_ROUTING_ENABLED=True)
    def test_reads_use_primary_when_in_transaction(self):
        """Reads within transactions must use primary database."""
        with transaction.atomic():
            # Inside atomic block, connection.in_atomic_block should be True
            db = self.router.db_for_read(Site)
            self.assertEqual(db, 'default')

    @override_settings(
        DATABASE_ROUTING_ENABLED=True,
        DATABASES={
            'default': {'ENGINE': 'django.db.backends.postgresql', 'NAME': 'test'},
            'replica': {'ENGINE': 'django.db.backends.postgresql', 'NAME': 'test'},
        }
    )
    def test_reads_use_primary_with_sticky_session(self):
        """When sticky session is active, reads must use primary."""
        _routing_state.use_primary = True
        db = self.router.db_for_read(Site)
        self.assertEqual(db, 'default')

    @override_settings(DATABASE_ROUTING_ENABLED=True)
    def test_reads_use_primary_without_replica_configured(self):
        """Without replica configured, gracefully fall back to default."""
        _routing_state.use_primary = False
        # Ensure 'replica' is not in DATABASES
        if 'replica' in settings.DATABASES:
            with self.settings(DATABASES={'default': settings.DATABASES['default']}):
                db = self.router.db_for_read(Site)
                self.assertEqual(db, 'default')
        else:
            db = self.router.db_for_read(Site)
            self.assertEqual(db, 'default')

    def test_writes_always_use_primary(self):
        """All write operations must always use primary database."""
        db = self.router.db_for_write(Site)
        self.assertEqual(db, 'default')

    @override_settings(DATABASE_ROUTING_ENABLED=True)
    def test_writes_mark_write_occurred(self):
        """Write operations should mark that a write occurred."""
        self.assertFalse(_routing_state.writes_occurred)
        self.router.db_for_write(Site)
        self.assertTrue(_routing_state.writes_occurred)

    @override_settings(DATABASE_ROUTING_ENABLED=False)
    def test_writes_dont_mark_when_routing_disabled(self):
        """When routing disabled, writes don't need to mark write occurred."""
        self.assertFalse(_routing_state.writes_occurred)
        self.router.db_for_write(Site)
        # When disabled, marking write is skipped for performance
        # (no need to set cookie if routing is off)
        self.assertFalse(_routing_state.writes_occurred)

    def test_allow_relation_same_group(self):
        """Relations between objects in default/replica group should be allowed."""
        obj1 = Mock()
        obj1._state = Mock(db='default')
        obj2 = Mock()
        obj2._state = Mock(db='replica')

        result = self.router.allow_relation(obj1, obj2)
        self.assertTrue(result)

    def test_allow_relation_none_db(self):
        """Relations with None db should be allowed."""
        obj1 = Mock()
        obj1._state = Mock(db=None)
        obj2 = Mock()
        obj2._state = Mock(db='default')

        result = self.router.allow_relation(obj1, obj2)
        self.assertTrue(result)

    def test_allow_migrate_on_default(self):
        """Migrations should be allowed on default database."""
        result = self.router.allow_migrate('default', 'dcim', 'Site')
        self.assertTrue(result)

    def test_allow_migrate_on_replica_forbidden(self):
        """Migrations should not be allowed on replica database."""
        result = self.router.allow_migrate('replica', 'dcim', 'Site')
        self.assertFalse(result)

    def test_allow_migrate_other_db_defers(self):
        """Migrations on other databases should defer to other routers."""
        result = self.router.allow_migrate('other_db', 'dcim', 'Site')
        self.assertIsNone(result)


class ContextManagerTestCase(TestCase):
    """Test the use_primary_db context manager."""

    def setUp(self):
        """Ensure clean state."""
        _routing_state.use_primary = False

    def tearDown(self):
        """Clean up routing state."""
        _routing_state.use_primary = False

    def test_use_primary_db_forces_primary(self):
        """Context manager should force primary database usage."""
        self.assertFalse(_routing_state.use_primary)

        with use_primary_db():
            self.assertTrue(_routing_state.use_primary)

        self.assertFalse(_routing_state.use_primary)

    def test_use_primary_db_restores_previous_state(self):
        """Context manager should restore previous state on exit."""
        _routing_state.use_primary = True

        with use_primary_db():
            self.assertTrue(_routing_state.use_primary)

        self.assertTrue(_routing_state.use_primary)

    def test_use_primary_db_nested(self):
        """Nested context managers should work correctly."""
        self.assertFalse(_routing_state.use_primary)

        with use_primary_db():
            self.assertTrue(_routing_state.use_primary)

            with use_primary_db():
                self.assertTrue(_routing_state.use_primary)

            self.assertTrue(_routing_state.use_primary)

        self.assertFalse(_routing_state.use_primary)

    def test_use_primary_db_with_exception(self):
        """Context manager should restore state even if exception occurs."""
        self.assertFalse(_routing_state.use_primary)

        try:
            with use_primary_db():
                self.assertTrue(_routing_state.use_primary)
                raise ValueError("Test exception")
        except ValueError:
            pass

        # State should be restored even after exception
        self.assertFalse(_routing_state.use_primary)
