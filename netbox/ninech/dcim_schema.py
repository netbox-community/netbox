import graphene
from graphene import AbstractType
from graphene import Node
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType
from dcim.models import Device, Interface
from graphene_django.converter import convert_django_field
from dcim.fields import ASNField, MACAddressField
from filter_fields import date_types, string_types, number_types

# Convert special field
@convert_django_field.register(MACAddressField)
def MACAddressFieldConvert(field, registry=None):
    return graphene.String()

@convert_django_field.register(ASNField)
def ASNFieldConvert(field, registry=None):
    return graphene.String()

# Nodes
class DeviceNode(DjangoObjectType):
    class Meta:
        model = Device
        interfaces = (Node, )

class InterfaceNode(DjangoObjectType):
    class Meta:
        model = Interface
        interfaces = (Node, )
        # only_fields = ('name', 'device', 'mgmt_only', 'id', 'mac_address')

# Queries
class DcimQuery(AbstractType):
    devices = DjangoFilterConnectionField(DeviceNode)
    interfaces = DjangoFilterConnectionField(InterfaceNode)