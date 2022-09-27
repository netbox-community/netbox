from django.core.exceptions import ImproperlyConfigured
from django.db import models


class SearchMixin(object):
    """
    Base class for building search indexes.
    """
    search_index = True
