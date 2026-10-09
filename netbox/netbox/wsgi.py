import os

from django.core.wsgi import get_wsgi_application
from django.urls import get_resolver

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "netbox.settings")

application = get_wsgi_application()

# Load the URLconf (and with it the GraphQL schema) at startup, so URLconf, plugin URL, and schema errors prevent the
# worker from starting instead of failing the first request. (This is skipped for management commands which don't
# need the URLconf.)
get_resolver().url_patterns
