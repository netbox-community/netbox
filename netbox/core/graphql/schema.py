import graphene

from netbox.graphql.fields import ObjectField, ObjectListField
from .types import *


class CoreQuery(graphene.ObjectType):
    data_file = ObjectField(DataFileType)
    data_file_list = ObjectListField(DataFileType)

    data_source = ObjectField(DataSourceType)
    data_source_list = ObjectListField(DataSourceType)
