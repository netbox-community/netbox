import graphene
from django_filters import filters


def get_graphene_type(filter_cls):
    """
    Return the appropriate Graphene scalar type for a django_filters Filter
    """
    if issubclass(filter_cls, filters.BooleanFilter):
        field_type = graphene.Boolean
    elif issubclass(filter_cls, filters.NumberFilter):
        # TODO: Floats? BigInts?
        field_type = graphene.Int
    elif issubclass(filter_cls, filters.DateFilter):
        field_type = graphene.Date
    elif issubclass(filter_cls, filters.DateTimeFilter):
        field_type = graphene.DateTime
    else:
        field_type = graphene.String

    # Multi-value filters should be handled as lists
    if issubclass(filter_cls, filters.MultipleChoiceFilter):
        return graphene.List(field_type)

    return field_type
