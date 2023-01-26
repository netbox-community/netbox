import graphene

from netbox.graphql.fields import ObjectField, ObjectListField
from .types import *


class CoreQuery(graphene.ObjectType):
    datafile = ObjectField(DataFileType)
    datafile_list = ObjectListField(DataFileType)

    datasource = ObjectField(DataSourceType)
    datasource_list = ObjectListField(DataSourceType)
