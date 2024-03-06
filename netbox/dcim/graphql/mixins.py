import strawberry
import strawberry_django
from typing import TYPE_CHECKING, Annotated, List, Union


__all__ = (
    'CabledObjectMixin',
    'PathEndpointMixin',
)


@strawberry.type
class CabledObjectMixin:
    cable: Annotated["CableType", strawberry.lazy('dcim.graphql.types')] | None

    @strawberry_django.field
    def link_peers(self) -> List[Annotated[Union[
        Annotated["CircuitTerminationType", strawberry.lazy('circuits.graphql.types')],
        Annotated["ConsolePortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["ConsoleServerPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["FrontPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerFeedType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerOutletType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["RearPortType", strawberry.lazy('dcim.graphql.types')],
    ], strawberry.union("LinkPeerType")]]:
        return self.link_peers


@strawberry.type
class PathEndpointMixin:

    @strawberry_django.field
    def connected_endpoints(self) -> List[Annotated[Union[
        Annotated["CircuitTerminationType", strawberry.lazy('circuits.graphql.types')],
        Annotated["ConsolePortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["ConsoleServerPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["FrontPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerFeedType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerOutletType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["ProviderNetworkType", strawberry.lazy('circuits.graphql.types')],
        Annotated["RearPortType", strawberry.lazy('dcim.graphql.types')],
    ], strawberry.union("ConnectedEndpointType")]]:
        return self.connected_endpoints or None
