from functools import partial

import graphene
from graphene_django import DjangoListField

from .utils import get_graphene_type

__all__ = (
    'ObjectField',
    'ObjectListField',
)


class ObjectField(graphene.Field):
    """
    Retrieve a single object, identified by its numeric ID.
    """
    def __init__(self, *args, **kwargs):

        if 'id' not in kwargs:
            kwargs['id'] = graphene.Int(required=True)

        super().__init__(*args, **kwargs)

    @staticmethod
    def object_resolver(django_object_type, root, info, **args):
        """
        Return an object given its numeric ID.
        """
        manager = django_object_type._meta.model._default_manager
        queryset = django_object_type.get_queryset(manager, info)

        return queryset.get(**args)

    def get_resolver(self, parent_resolver):
        return partial(self.object_resolver, self._type)


class ObjectListField(DjangoListField):
    """
    Retrieve a list of objects, optionally filtered by one or more FilterSet filters.
    """
    def __init__(self, _type, *args, **kwargs):

        assert hasattr(_type._meta, 'filterset_class'), "DjangoFilterListField must define filterset_class under Meta"
        filterset_class = _type._meta.filterset_class

        # Get FilterSet kwargs
        filter_kwargs = {}
        for filter_name, filter_field in filterset_class.get_filters().items():
            field_type = get_graphene_type(type(filter_field))
            filter_kwargs[filter_name] = graphene.Argument(field_type)

        super().__init__(_type, args=filter_kwargs, *args, **kwargs)

    @staticmethod
    def list_resolver(django_object_type, resolver, default_manager, root, info, **args):
        # Get the QuerySet from the object type
        queryset = django_object_type.get_queryset(default_manager, info)

        # Instantiate and apply the FilterSet
        filterset_class = django_object_type._meta.filterset_class
        filterset = filterset_class(data=args, queryset=queryset, request=info.context)

        return filterset.qs
