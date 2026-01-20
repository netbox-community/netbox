"""
Database utilities for NetBox, including read/write separation support.
"""
from .context_managers import use_primary_db

__all__ = (
    'use_primary_db',
)
