from typing import Annotated, List, Union

import strawberry

__all__ = (
    'CabledObjectMixinV1',
    'PathEndpointMixinV1',
)


@strawberry.type
class CabledObjectMixinV1:
    cable: Annotated["CableTypeV1", strawberry.lazy('dcim.graphql.types_v1')] | None  # noqa: F821

    link_peers: List[Annotated[Union[
        Annotated["CircuitTerminationTypeV1", strawberry.lazy('circuits.graphql.types_v1')],  # noqa: F821
        Annotated["ConsolePortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],  # noqa: F821
        Annotated["ConsoleServerPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],  # noqa: F821
        Annotated["FrontPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],  # noqa: F821
        Annotated["InterfaceTypeV1", strawberry.lazy('dcim.graphql.types_v1')],  # noqa: F821
        Annotated["PowerFeedTypeV1", strawberry.lazy('dcim.graphql.types_v1')],  # noqa: F821
        Annotated["PowerOutletTypeV1", strawberry.lazy('dcim.graphql.types_v1')],  # noqa: F821
        Annotated["PowerPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],  # noqa: F821
        Annotated["RearPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],  # noqa: F821
    ], strawberry.union("LinkPeerType")]]


@strawberry.type
class PathEndpointMixinV1:

    connected_endpoints: List[Annotated[Union[
        Annotated["CircuitTerminationTypeV1", strawberry.lazy('circuits.graphql.types_v1')],  # noqa: F821
        Annotated["VirtualCircuitTerminationTypeV1", strawberry.lazy('circuits.graphql.types_v1')],  # noqa: F821
        Annotated["ConsolePortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],  # noqa: F821
        Annotated["ConsoleServerPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],  # noqa: F821
        Annotated["FrontPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],  # noqa: F821
        Annotated["InterfaceTypeV1", strawberry.lazy('dcim.graphql.types_v1')],  # noqa: F821
        Annotated["PowerFeedTypeV1", strawberry.lazy('dcim.graphql.types_v1')],  # noqa: F821
        Annotated["PowerOutletTypeV1", strawberry.lazy('dcim.graphql.types_v1')],  # noqa: F821
        Annotated["PowerPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],  # noqa: F821
        Annotated["ProviderNetworkTypeV1", strawberry.lazy('circuits.graphql.types_v1')],  # noqa: F821
        Annotated["RearPortTypeV1", strawberry.lazy('dcim.graphql.types_v1')],  # noqa: F821
    ], strawberry.union("ConnectedEndpointTypeV1")]]
