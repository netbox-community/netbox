"""
Database routers for read/write separation.

This module implements Django's database routing protocol to support routing
read operations to replica databases while keeping write operations on the
primary database.
"""
from django.conf import settings
from django.db import connection

from .context_managers import _routing_state, mark_write_occurred

__all__ = (
    'ReadWriteRouter',
)


class ReadWriteRouter:
    """
    Database router for read/write separation with sticky session support.

    This router implements Django's database routing protocol to route read
    operations to a replica database when safe to do so, while always routing
    write operations to the primary database.

    Routing Logic:
    - All write operations (INSERT, UPDATE, DELETE) use the 'default' (primary) database
    - Read operations use 'replica' database when ALL of the following are true:
      1. DATABASE_ROUTING_ENABLED setting is True
      2. Not within a transaction.atomic() block
      3. No sticky session is active (no recent writes by this user)
      4. A 'replica' database is configured in settings.DATABASES

    Safety Guarantees:
    - Reads within transactions always use the primary database
    - After any write, the user's session is "sticky" to primary for N seconds
    - Permission validation and security checks always use primary
    - Signal handlers inherit the transaction's database connection

    Configuration:
        DATABASES = {
            'default': {...},  # Primary database
            'replica': {...},  # Read replica
        }
        DATABASE_ROUTERS = ['netbox.db.routers.ReadWriteRouter']
        DATABASE_ROUTING_ENABLED = True
        DATABASE_STICKY_SESSION_DURATION = 5  # seconds
    """

    def db_for_read(self, model, **hints):
        """
        Route read operations based on safety guarantees.

        Args:
            model: The model class being queried
            **hints: Additional routing hints from Django

        Returns:
            str: Database alias to use ('default' or 'replica')

        Priority order:
        1. Routing disabled? → 'default'
        2. In transaction? → 'default' (primary)
        3. Sticky session active? → 'default' (primary)
        4. Explicit 'using' hint? → use hint
        5. Replica configured? → 'replica'
        6. Fallback → 'default'
        """
        # If routing is disabled, always use default
        if not getattr(settings, 'DATABASE_ROUTING_ENABLED', False):
            return 'default'

        # If we're in a transaction, always use the primary database
        # This ensures consistency for all reads within atomic blocks
        if connection.in_atomic_block:
            return 'default'

        # If sticky session is active (recent write occurred), use primary
        # This prevents reading stale data from replicas with replication lag
        if _routing_state.use_primary:
            return 'default'

        # Respect explicit database hints from Django
        if 'instance' in hints:
            # If we have an instance hint, use its database
            instance = hints['instance']
            if hasattr(instance, '_state') and instance._state.db:
                return instance._state.db

        # If replica database is configured, use it for reads
        # This is the happy path for load balancing
        if 'replica' in settings.DATABASES:
            return 'replica'

        # Fallback to default (primary) database
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Route write operations to the primary database.

        All write operations (INSERT, UPDATE, DELETE) always use the primary
        database. This method also marks that a write has occurred, which
        triggers the sticky session mechanism.

        Args:
            model: The model class being written
            **hints: Additional routing hints from Django

        Returns:
            str: Always returns 'default' (primary database)
        """
        # Mark that a write occurred for sticky session tracking
        # This will cause middleware to set a sticky session cookie
        if getattr(settings, 'DATABASE_ROUTING_ENABLED', False):
            mark_write_occurred()

        # All writes always go to the primary database
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Determine if a relation between two objects is allowed.

        Relations are allowed if both objects are in the same database group
        (primary and replicas are considered the same group since they contain
        the same data).

        Args:
            obj1: First model instance
            obj2: Second model instance
            **hints: Additional routing hints from Django

        Returns:
            bool or None: True if relation allowed, None to defer to other routers
        """
        # Get the databases for each object
        db1 = obj1._state.db if hasattr(obj1, '_state') else None
        db2 = obj2._state.db if hasattr(obj2, '_state') else None

        # If both objects are in default or replica, allow the relation
        # (they're part of the same replication group)
        if db1 in ('default', 'replica', None) and db2 in ('default', 'replica', None):
            return True

        # Defer to other routers or default Django behavior
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Determine if migrations should run on a given database.

        Migrations should only run on the primary database. Read replicas
        should receive schema changes through replication.

        Args:
            db: Database alias
            app_label: Application label
            model_name: Model name (optional)
            **hints: Additional routing hints from Django

        Returns:
            bool or None: True/False if decision is made, None to defer
        """
        # Only allow migrations on the primary database
        # Replicas will get schema changes through replication
        if db == 'default':
            return True

        # Explicitly prevent migrations on replica
        if db == 'replica':
            return False

        # Defer to other routers for other databases
        return None
