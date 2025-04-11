from typing import Annotated, List, Union

import strawberry

__all__ = (
    'CabledObjectMixin',
    'PathEndpointMixin',
)


@strawberry.type
class CabledObjectMixin:
    cable: Annotated["CableType", strawberry.lazy('dcim.graphql.types')] | None  # noqa: F821

    link_peers: List[Annotated[Union[
        Annotated["CircuitTerminationType", strawberry.lazy('circuits.graphql.types')],  # noqa: F821
        Annotated["ConsolePortType", strawberry.lazy('dcim.graphql.types')],  # noqa: F821
        Annotated["ConsoleServerPortType", strawberry.lazy('dcim.graphql.types')],  # noqa: F821
        Annotated["FrontPortType", strawberry.lazy('dcim.graphql.types')],  # noqa: F821
        Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')],  # noqa: F821
        Annotated["PowerFeedType", strawberry.lazy('dcim.graphql.types')],  # noqa: F821
        Annotated["PowerOutletType", strawberry.lazy('dcim.graphql.types')],  # noqa: F821
        Annotated["PowerPortType", strawberry.lazy('dcim.graphql.types')],  # noqa: F821
        Annotated["RearPortType", strawberry.lazy('dcim.graphql.types')],  # noqa: F821
    ], strawberry.union("LinkPeerType")]]


@strawberry.type
class PathEndpointMixin:

    connected_endpoints: List[Annotated[Union[
        Annotated["CircuitTerminationType", strawberry.lazy('circuits.graphql.types')],  # noqa: F821
        Annotated["VirtualCircuitTerminationType", strawberry.lazy('circuits.graphql.types')],  # noqa: F821
        Annotated["ConsolePortType", strawberry.lazy('dcim.graphql.types')],  # noqa: F821
        Annotated["ConsoleServerPortType", strawberry.lazy('dcim.graphql.types')],  # noqa: F821
        Annotated["FrontPortType", strawberry.lazy('dcim.graphql.types')],  # noqa: F821
        Annotated["InterfaceType", strawberry.lazy('dcim.graphql.types')],  # noqa: F821
        Annotated["PowerFeedType", strawberry.lazy('dcim.graphql.types')],  # noqa: F821
        Annotated["PowerOutletType", strawberry.lazy('dcim.graphql.types')],  # noqa: F821
        Annotated["PowerPortType", strawberry.lazy('dcim.graphql.types')],  # noqa: F821
        Annotated["ProviderNetworkType", strawberry.lazy('circuits.graphql.types')],  # noqa: F821
        Annotated["RearPortType", strawberry.lazy('dcim.graphql.types')],  # noqa: F821
    ], strawberry.union("ConnectedEndpointType")]]
