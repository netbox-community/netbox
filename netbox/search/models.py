from django.core.exceptions import ImproperlyConfigured
from django.db import models


class SearchMixin(object):
    """
    Base class for building search indexes.
    """

    def __init__(self, model=None, queryset=None, filterset=None, table=None, url=None):
        self.model = model
        self.queryset = queryset
        self.filterset = filterset
        self.table = table
        self.url = url

    def get_model(self):
        """
        Should return the ``Model`` class (not an instance) that the rest of the
        ``SearchIndex`` should use.
        This method is required & you must override it to return the correct class.
        """
        if self.model is not None:
            model = self.model
        else:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__}s is missing a Model. Set model in init or override"
                f"{self.__class__.__name__}s.get_model()."
            )

        return model

    def get_queryset(self):
        """
        Should return the ``QuerySet`` class (not an instance) that the rest of the
        ``SearchIndex`` should use.
        This method is required & you must override it to return the correct class.
        """
        if self.queryset is not None:
            queryset = self.queryset
        else:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__}s is missing a QuerySet. Set queryset in init or override "
                f"{self.__class__.__name__}s.get_queryset()."
            )

        return queryset

    def get_filterset(self):
        """
        Should return the ``FilterSet`` class (not an instance) that the rest of the
        ``SearchIndex`` should use.
        This method is required & you must override it to return the correct class.
        """
        if self.filterset is not None:
            filterset = self.filterset
        else:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__}s is missing a FilterSet.  Set filterset in init or override "
                f"{self.__class__.__name__}s.get_filterset()."
            )

        return filterset

    def get_table(self):
        """
        Should return the ``Table`` class (not an instance) that the rest of the
        ``SearchIndex`` should use.
        This method is required & you must override it to return the correct class.
        """
        if self.table is not None:
            table = self.table
        else:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__}s is missing a Table.  Set table in init or override "
                f"{self.__class__.__name__}s.get_table()."
            )

        return table

    def get_url(self):
        """
        Should return the ``URL`` class (not an instance) that the rest of the
        ``SearchIndex`` should use.
        This method is required & you must override it to return the correct class.
        """
        if self.url is not None:
            url = self.url
        else:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__}s is missing a URL.  Set url in init or override "
                f"{self.__class__.__name__}s.get_url()."
            )

        return url
