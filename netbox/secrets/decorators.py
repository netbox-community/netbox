from __future__ import unicode_literals

from django.contrib import messages
from django.shortcuts import redirect

from .models import UserKey


def userkey_required():
    """
    Decorator for views which require that the user has an active UserKey (typically for encryption/decryption of
    Secrets).
    """
    def _decorator(view):
        def wrapped_view(request, *args, **kwargs):
            try:
                uk = UserKey.objects.get(user=request.user)
            except UserKey.DoesNotExist:
                messages.warning(request, "This operation requires an active user key, but you don't have one.")
                return redirect('user:userkey')
            if not uk.is_active():
                messages.warning(request, "This operation is not available. Your user key has not been activated.")
                return redirect('user:userkey')
            return view(request, *args, **kwargs)
        return wrapped_view
    return _decorator
