from contextvars import ContextVar

__all__ = (
    'current_request',
    'events_queue',
)


current_request = ContextVar('current_request', default=None)
events_queue = ContextVar('events_queue', default=dict())
