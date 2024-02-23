from typing import TYPE_CHECKING, Annotated, List, Union

import strawberry
import strawberry_django
from circuits.graphql.types import CircuitTerminationType, ProviderNetworkType
from circuits.models import CircuitTermination, ProviderNetwork
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


class InventoryItemTemplateComponentType:
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
        if type(instance) is ConsolePortTemplate:
            return ConsolePortTemplateType
        if type(instance) is ConsoleServerPortTemplate:
            return ConsoleServerPortTemplateType
        if type(instance) is FrontPortTemplate:
            return FrontPortTemplateType
        if type(instance) is InterfaceTemplate:
            return InterfaceTemplateType
        if type(instance) is PowerOutletTemplate:
            return PowerOutletTemplateType
        if type(instance) is PowerPortTemplate:
            return PowerPortTemplateType
        if type(instance) is RearPortTemplate:
            return RearPortTemplateType


class InventoryItemComponentType:
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
        if type(instance) is ConsolePort:
            return ConsolePortType
        if type(instance) is ConsoleServerPort:
            return ConsoleServerPortType
        if type(instance) is FrontPort:
            return FrontPortType
        if type(instance) is Interface:
            return InterfaceType
        if type(instance) is PowerOutlet:
            return PowerOutletType
        if type(instance) is PowerPort:
            return PowerPortType
        if type(instance) is RearPort:
            return RearPortType


class ConnectedEndpointType:
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
            ProviderNetworkType,
            RearPortType,
        )

    @classmethod
    def resolve_type(cls, instance, info):
        if type(instance) is CircuitTermination:
            return CircuitTerminationType
        if type(instance) is ConsolePortType:
            return ConsolePortType
        if type(instance) is ConsoleServerPort:
            return ConsoleServerPortType
        if type(instance) is FrontPort:
            return FrontPortType
        if type(instance) is Interface:
            return InterfaceType
        if type(instance) is PowerFeed:
            return PowerFeedType
        if type(instance) is PowerOutlet:
            return PowerOutletType
        if type(instance) is PowerPort:
            return PowerPortType
        if type(instance) is ProviderNetwork:
            return ProviderNetworkType
        if type(instance) is RearPort:
            return RearPortType
