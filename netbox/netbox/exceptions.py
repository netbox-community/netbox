from django.db.utils import DatabaseError


class DatabaseWriteDenied(DatabaseError):
    """
    Custom exception raised when a write operation is attempted in maintenance mode.
    """
    pass
