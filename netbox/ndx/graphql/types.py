from typing import TYPE_CHECKING, Annotated

import strawberry

from ndx import models
from netbox.graphql.types import ObjectType, register_type

from .filters import *

if TYPE_CHECKING:
    from netbox.graphql.types import ContentTypeType

__all__ = (
    'EnrichmentType',
    'ImportRecordType',
    'ProvenanceType',
)


@register_type(
    models.ImportRecord,
    fields='__all__',
    filters=ImportRecordFilter,
    pagination=True
)
class ImportRecordType(ObjectType):
    object_type: Annotated["ContentTypeType", strawberry.lazy('netbox.graphql.types')]
    enrichment: Annotated["EnrichmentType", strawberry.lazy('ndx.graphql.types')] | None


@register_type(
    models.Enrichment,
    fields='__all__',
    filters=EnrichmentFilter,
    pagination=True
)
class EnrichmentType(ObjectType):
    import_record: Annotated["ImportRecordType", strawberry.lazy('ndx.graphql.types')]
    provenance: list[Annotated["ProvenanceType", strawberry.lazy('ndx.graphql.types')]]


@register_type(
    models.Provenance,
    fields='__all__',
)
class ProvenanceType(ObjectType):
    enrichment: Annotated["EnrichmentType", strawberry.lazy('ndx.graphql.types')]
