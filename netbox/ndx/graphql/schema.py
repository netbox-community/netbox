import strawberry
import strawberry_django

from .types import *


@strawberry.type(name="Query")
class NDXQuery:
    ndx_import_record: ImportRecordType = strawberry_django.field()
    ndx_import_record_list: list[ImportRecordType] = strawberry_django.field()

    ndx_enrichment: EnrichmentType = strawberry_django.field()
    ndx_enrichment_list: list[EnrichmentType] = strawberry_django.field()
