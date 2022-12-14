import graphene
from circuits.graphql.types import CircuitTerminationType
from circuits.models import CircuitTermination
from dcim.graphql.types import (
    ConsolePortTemplateType,
    ConsolePortType,
    ConsoleServerPortTemplateType,
    ConsoleServerPortType,
    FrontPortTemplateType,
    FrontPortType,
    InterfaceTemplateType,
    InterfaceType,
    PowerFeedType,
    PowerOutletTemplateType,
    PowerOutletType,
    PowerPortTemplateType,
    PowerPortType,
    RearPortTemplateType,
    RearPortType,
)
from dcim.models import (
    ConsolePort,
    ConsolePortTemplate,
    ConsoleServerPort,
    ConsoleServerPortTemplate,
    FrontPort,
    FrontPortTemplate,
    Interface,
    InterfaceTemplate,
    PowerFeed,
    PowerOutlet,
    PowerOutletTemplate,
    PowerPort,
    PowerPortTemplate,
    RearPort,
    RearPortTemplate,
)


class LinkPeerType(graphene.Union):
    class Meta:
        types = (
            CircuitTerminationType,
            ConsolePortType,
            ConsoleServerPortType,
            FrontPortType,
            InterfaceType,
            PowerFeedType,
            PowerOutletType,
            PowerPortType,
            RearPortType,
        )

    @classmethod
    def resolve_type(cls, instance, info):
        if type(instance) == CircuitTermination:
            return CircuitTerminationType
        if type(instance) == ConsolePortType:
            return ConsolePortType
        if type(instance) == ConsoleServerPort:
            return ConsoleServerPortType
        if type(instance) == FrontPort:
            return FrontPortType
        if type(instance) == Interface:
            return InterfaceType
        if type(instance) == PowerFeed:
            return PowerFeedType
        if type(instance) == PowerOutlet:
            return PowerOutletType
        if type(instance) == PowerPort:
            return PowerPortType
        if type(instance) == RearPort:
            return RearPortType


class CableTerminationTerminationType(graphene.Union):
    class Meta:
        types = (
            CircuitTerminationType,
            ConsolePortType,
            ConsoleServerPortType,
            FrontPortType,
            InterfaceType,
            PowerFeedType,
            PowerOutletType,
            PowerPortType,
            RearPortType,
        )

    @classmethod
    def resolve_type(cls, instance, info):
        if type(instance) == CircuitTermination:
            return CircuitTerminationType
        if type(instance) == ConsolePortType:
            return ConsolePortType
        if type(instance) == ConsoleServerPort:
            return ConsoleServerPortType
        if type(instance) == FrontPort:
            return FrontPortType
        if type(instance) == Interface:
            return InterfaceType
        if type(instance) == PowerFeed:
            return PowerFeedType
        if type(instance) == PowerOutlet:
            return PowerOutletType
        if type(instance) == PowerPort:
            return PowerPortType
        if type(instance) == RearPort:
            return RearPortType


class InventoryItemTemplateComponentType(graphene.Union):
    class Meta:
        types = (
            ConsolePortTemplateType,
            ConsoleServerPortTemplateType,
            FrontPortTemplateType,
            InterfaceTemplateType,
            PowerOutletTemplateType,
            PowerPortTemplateType,
            RearPortTemplateType,
        )

    @classmethod
    def resolve_type(cls, instance, info):
        if type(instance) == ConsolePortTemplate:
            return ConsolePortTemplateType
        if type(instance) == ConsoleServerPortTemplate:
            return ConsoleServerPortTemplateType
        if type(instance) == FrontPortTemplate:
            return FrontPortTemplateType
        if type(instance) == InterfaceTemplate:
            return InterfaceTemplateType
        if type(instance) == PowerOutletTemplate:
            return PowerOutletTemplateType
        if type(instance) == PowerPortTemplate:
            return PowerPortTemplateType
        if type(instance) == RearPortTemplate:
            return RearPortTemplateType


class InventoryItemComponentType(graphene.Union):
    class Meta:
        types = (
            ConsolePortType,
            ConsoleServerPortType,
            FrontPortType,
            InterfaceType,
            PowerOutletType,
            PowerPortType,
            RearPortType,
        )

    @classmethod
    def resolve_type(cls, instance, info):
        if type(instance) == ConsolePort:
            return ConsolePortType
        if type(instance) == ConsoleServerPort:
            return ConsoleServerPortType
        if type(instance) == FrontPort:
            return FrontPortType
        if type(instance) == Interface:
            return InterfaceType
        if type(instance) == PowerOutlet:
            return PowerOutletType
        if type(instance) == PowerPort:
            return PowerPortType
        if type(instance) == RearPort:
            return RearPortType
