from typing import Annotated, List, Union

import strawberry

__all__ = (
    'CabledObjectMixin',
    'PathEndpointMixin',
)


@strawberry.type
class CabledObjectMixin:
    cable: Annotated["CableType", strawberry.lazy('dcim.graphql.types')] | None

    link_peers: List[Annotated[Union[
        Annotated["CircuitTerminationType", strawberry.lazy('circuits.graphql.types')],
        Annotated["ConsolePortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["ConsoleServerPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["FrontPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerFeedType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerOutletType", strawberry.lazy('dcim.graphql.types')],
        Annotated["PowerPortType", strawberry.lazy('dcim.graphql.types')],
        Annotated["RearPortType", strawberry.lazy('dcim.graphql.types')],
    ], strawberry.union("LinkPeerType")]]


@strawberry.type
class PathEndpointMixin:

    connected_endpoints: List[Annotated[Union[
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
    ], strawberry.union("ConnectedEndpointType")]]
