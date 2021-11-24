from netbox import thread_locals


def set_request(request):
    thread_locals.request = request


def get_request():
    return getattr(thread_locals, 'request', None)
