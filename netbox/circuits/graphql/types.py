from typing import List

import strawberry
import strawberry_django
from circuits import models
from dcim.graphql.mixins import CabledObjectMixin
from extras.graphql.mixins import ContactsMixin, CustomFieldsMixin, TagsMixin
from tenancy.graphql.types import TenantType

from netbox.graphql.types import NetBoxObjectType, ObjectType, OrganizationalObjectType

from .filters import *

__all__ = (
    'CircuitTerminationType',
    'CircuitType',
    'CircuitTypeType',
    'ProviderType',
    'ProviderAccountType',
    'ProviderNetworkType',
)


@strawberry_django.type(
    models.Provider,
    fields='__all__',
    filters=ProviderFilter
)
class ProviderType(NetBoxObjectType, ContactsMixin):
    pass


@strawberry_django.type(
    models.ProviderAccount,
    fields='__all__',
    filters=ProviderAccountFilter
)
class ProviderAccountType(NetBoxObjectType):
    pass


@strawberry_django.type(
    models.ProviderNetwork,
    fields='__all__',
    filters=ProviderNetworkFilter
)
class ProviderNetworkType(NetBoxObjectType):
    pass


@strawberry_django.type(
    models.CircuitTermination,
    fields='__all__',
    filters=CircuitTerminationFilter
)
class CircuitTerminationType(CustomFieldsMixin, TagsMixin, CabledObjectMixin, ObjectType):
    pass


@strawberry_django.type(
    models.CircuitType,
    # fields='__all__',
    exclude=['color',],  # bug - remove color from exclude
    filters=CircuitTypeFilter
)
class CircuitTypeType(OrganizationalObjectType):
    pass


@strawberry_django.type(
    models.Circuit,
    fields='__all__',
    filters=CircuitFilter
)
class CircuitType(NetBoxObjectType, ContactsMixin):
    provider: ProviderType
    provider_account: ProviderAccountType | None
    termination_a: CircuitTerminationType | None
    termination_z: CircuitTerminationType | None
    type: CircuitTypeType
    tenant: TenantType | None

    @strawberry_django.field
    def terminations(self) -> List[CircuitTerminationType]:
        return self.terminations.all()
