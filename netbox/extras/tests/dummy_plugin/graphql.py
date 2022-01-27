import graphene
from graphene_django import DjangoObjectType

from netbox.graphql.fields import ObjectField, ObjectListField

from . import models


class DummyModelType(DjangoObjectType):

    class Meta:
        model = models.DummyModel
        fields = '__all__'


class DummyQuery(graphene.ObjectType):
    dummymodel = ObjectField(DummyModelType)
    dummymodel_list = ObjectListField(DummyModelType)


schema = DummyQuery
