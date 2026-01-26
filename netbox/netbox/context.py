from contextvars import ContextVar

__all__ = (
    'current_request',
    'events_queue',
    'query_cache',
)


current_request = ContextVar('current_request', default=None)
events_queue = ContextVar('events_queue', default=dict())
query_cache = ContextVar('query_cache', default=None)
