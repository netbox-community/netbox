import logging

from dataclasses import dataclass, field
from datetime import datetime

from django.utils import timezone

__all__ = (
    'JobLogEntry',
)


@dataclass
class JobLogEntry:
    level: str
    message: str
    timestamp: datetime = field(default_factory=timezone.now)

    @classmethod
    def from_logrecord(cls, record: logging.LogRecord):
        return cls(record.levelname.lower(), record.msg)
