import graphene

from core import models
from netbox.graphql.fields import ObjectField, ObjectListField
from .types import *
from utilities.graphql_optimizer import gql_query_optimizer


class CoreQuery(graphene.ObjectType):
    data_file = ObjectField(DataFileType)
    data_file_list = ObjectListField(DataFileType)

    def resolve_data_file_list(root, info, **kwargs):
        return gql_query_optimizer(models.DataFile.objects.all(), info)

    data_source = ObjectField(DataSourceType)
    data_source_list = ObjectListField(DataSourceType)

    def resolve_data_source_list(root, info, **kwargs):
        return gql_query_optimizer(models.DataSource.objects.all(), info)
