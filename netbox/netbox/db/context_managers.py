"""
Context managers and state management for database routing.

This module provides thread-safe state management for tracking database routing
decisions, particularly for sticky sessions after write operations.
"""
from contextlib import contextmanager
from contextvars import ContextVar

__all__ = (
    'use_primary_db',
    'mark_write_occurred',
)


# Context variables for async-safe thread-local storage
_use_primary = ContextVar('use_primary', default=False)
_writes_occurred = ContextVar('writes_occurred', default=False)


class RoutingState:
    """
    Manages routing state for database read/write separation.

    This class provides properties to track:
    - Whether reads should be forced to the primary database (sticky session)
    - Whether write operations occurred during the current request
    """

    @property
    def use_primary(self):
        """
        Returns True if reads should use the primary database.
        Set by middleware when sticky session is active.
        """
        return _use_primary.get()

    @use_primary.setter
    def use_primary(self, value):
        """Set whether to use primary database for reads."""
        _use_primary.set(bool(value))

    @property
    def writes_occurred(self):
        """
        Returns True if write operations occurred during this request.
        Used by middleware to determine if sticky session cookie should be set.
        """
        return _writes_occurred.get()

    @writes_occurred.setter
    def writes_occurred(self, value):
        """Mark that write operations have occurred."""
        _writes_occurred.set(bool(value))


# Global routing state instance
_routing_state = RoutingState()


@contextmanager
def use_primary_db():
    """
    Context manager to force all database operations to use the primary database.

    This is useful for operations that require strong consistency guarantees,
    such as reading data immediately after a write when you can't rely on
    the sticky session mechanism.

    Usage:
        from netbox.db import use_primary_db

        with use_primary_db():
            # All reads and writes use primary database
            obj = MyModel.objects.get(pk=1)
            obj.field = 'new value'
            obj.save()

    The context manager is re-entrant and properly handles nested calls.
    """
    old_state = _routing_state.use_primary
    _routing_state.use_primary = True
    try:
        yield
    finally:
        _routing_state.use_primary = old_state


def mark_write_occurred():
    """
    Mark that a write operation has occurred.

    This function is called internally by the database router when a write
    operation is performed. It signals to the middleware that a sticky session
    cookie should be set on the response.

    This function is primarily for internal use and generally does not need
    to be called directly by application code.
    """
    _routing_state.writes_occurred = True
