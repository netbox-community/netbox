from strawberry.types import Info

from circuits.graphql.types_v1 import CircuitTerminationTypeV1, ProviderNetworkTypeV1
from circuits.models import CircuitTermination, ProviderNetwork
from dcim.graphql.types_v1 import (
    ConsolePortTemplateTypeV1,
    ConsolePortTypeV1,
    ConsoleServerPortTemplateTypeV1,
    ConsoleServerPortTypeV1,
    FrontPortTemplateTypeV1,
    FrontPortTypeV1,
    InterfaceTemplateTypeV1,
    InterfaceTypeV1,
    PowerFeedTypeV1,
    PowerOutletTemplateTypeV1,
    PowerOutletTypeV1,
    PowerPortTemplateTypeV1,
    PowerPortTypeV1,
    RearPortTemplateTypeV1,
    RearPortTypeV1,
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


class InventoryItemTemplateComponentTypeV1:
    class Meta:
        types = (
            ConsolePortTemplateTypeV1,
            ConsoleServerPortTemplateTypeV1,
            FrontPortTemplateTypeV1,
            InterfaceTemplateTypeV1,
            PowerOutletTemplateTypeV1,
            PowerPortTemplateTypeV1,
            RearPortTemplateTypeV1,
        )

    @classmethod
    def resolve_type(cls, instance, info: Info):
        if type(instance) is ConsolePortTemplate:
            return ConsolePortTemplateTypeV1
        if type(instance) is ConsoleServerPortTemplate:
            return ConsoleServerPortTemplateTypeV1
        if type(instance) is FrontPortTemplate:
            return FrontPortTemplateTypeV1
        if type(instance) is InterfaceTemplate:
            return InterfaceTemplateTypeV1
        if type(instance) is PowerOutletTemplate:
            return PowerOutletTemplateTypeV1
        if type(instance) is PowerPortTemplate:
            return PowerPortTemplateTypeV1
        if type(instance) is RearPortTemplate:
            return RearPortTemplateTypeV1


class InventoryItemComponentTypeV1:
    class Meta:
        types = (
            ConsolePortTypeV1,
            ConsoleServerPortTypeV1,
            FrontPortTypeV1,
            InterfaceTypeV1,
            PowerOutletTypeV1,
            PowerPortTypeV1,
            RearPortTypeV1,
        )

    @classmethod
    def resolve_type(cls, instance, info: Info):
        if type(instance) is ConsolePort:
            return ConsolePortTypeV1
        if type(instance) is ConsoleServerPort:
            return ConsoleServerPortTypeV1
        if type(instance) is FrontPort:
            return FrontPortTypeV1
        if type(instance) is Interface:
            return InterfaceTypeV1
        if type(instance) is PowerOutlet:
            return PowerOutletTypeV1
        if type(instance) is PowerPort:
            return PowerPortTypeV1
        if type(instance) is RearPort:
            return RearPortTypeV1


class ConnectedEndpointTypeV1:
    class Meta:
        types = (
            CircuitTerminationTypeV1,
            ConsolePortTypeV1,
            ConsoleServerPortTypeV1,
            FrontPortTypeV1,
            InterfaceTypeV1,
            PowerFeedTypeV1,
            PowerOutletTypeV1,
            PowerPortTypeV1,
            ProviderNetworkTypeV1,
            RearPortTypeV1,
        )

    @classmethod
    def resolve_type(cls, instance, info: Info):
        if type(instance) is CircuitTermination:
            return CircuitTerminationTypeV1
        if type(instance) is ConsolePort:
            return ConsolePortTypeV1
        if type(instance) is ConsoleServerPort:
            return ConsoleServerPortTypeV1
        if type(instance) is FrontPort:
            return FrontPortTypeV1
        if type(instance) is Interface:
            return InterfaceTypeV1
        if type(instance) is PowerFeed:
            return PowerFeedTypeV1
        if type(instance) is PowerOutlet:
            return PowerOutletTypeV1
        if type(instance) is PowerPort:
            return PowerPortTypeV1
        if type(instance) is ProviderNetwork:
            return ProviderNetworkTypeV1
        if type(instance) is RearPort:
            return RearPortTypeV1
