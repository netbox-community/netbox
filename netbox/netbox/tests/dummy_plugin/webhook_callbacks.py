from extras.webhooks import register_webhook_callback


@register_webhook_callback
def set_context(object_type, event_type, data, request):
    return {
        'foo': 123,
    }
