import graphene
from circuits.graphql.types import CircuitTerminationType
from circuits.models import CircuitTermination
from dcim.graphql.types import (
    ConsolePortType,
    ConsoleServerPortType,
    FrontPortType,
    InterfaceType,
    PowerFeedType,
    PowerOutletType,
    PowerPortType,
    RearPortType,
)
from dcim.models import (
    ConsolePort,
    ConsoleServerPort,
    FrontPort,
    Interface,
    PowerFeed,
    PowerOutlet,
    PowerPort,
    RearPort,
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
