from django.core.exceptions import ImproperlyConfigured
from django.db import models


class SearchMixin(models.Model):
    """
    Base class for building search indexes.
    """

    model = None
    queryset = None
    filterset = None
    table = None
    url = None

    class Meta:
        abstract = True

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
                f"{self.__class__.__name__}s is missing a Model. Define "
                f"{self.__class__.__name__}s.model or override "
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
                f"{self.__class__.__name__}s is missing a QuerySet. Define "
                f"{self.__class__.__name__}s.queryset or override "
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
                f"{self.__class__.__name__}s is missing a FilterSet. Define "
                f"{self.__class__.__name__}s.filterset or override "
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
                f"{self.__class__.__name__}s is missing a Table. Define "
                f"{self.__class__.__name__}s.table or override "
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
                f"{self.__class__.__name__}s is missing a URL. Define "
                f"{self.__class__.__name__}s.url or override "
                f"{self.__class__.__name__}s.get_url()."
            )

        return url
