from contextvars import ContextVar

__all__ = (
    'current_request',
    'webhooks_queue',
)


current_request = ContextVar('current_request')
webhooks_queue = ContextVar('webhooks_queue')
