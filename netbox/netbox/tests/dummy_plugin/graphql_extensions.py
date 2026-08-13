from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from django.db.models import Q

from utilities.querysets import RestrictedPrefetch

from . import models

if TYPE_CHECKING:
    from dcim.graphql.types import SiteType

#
# Extensions to core GraphQL types & filters (see netbox.graphql.types.register_type /
# netbox.graphql.filters.register_filter). These exercise the plugin extension point.
#


@strawberry_django.type(
    models.DummySiteAttachment,
    fields='__all__',
)
class DummySiteAttachmentType:
    site: Annotated['SiteType', strawberry.lazy('dcim.graphql.types')]


@strawberry.type
class SiteTypeExtension:
    models = ['dcim.site']

    @strawberry_django.field
    def dummy_plugin_field(self) -> str:
        return 'dummy-plugin-value'

    @strawberry_django.field(
        prefetch_related=lambda info: RestrictedPrefetch(
            'dummy_site_attachments', info.context.request.user, 'view',
            queryset=models.DummySiteAttachment.objects.all(),
        ),
    )
    def dummy_site_attachments(self) -> list[Annotated[
        'DummySiteAttachmentType', strawberry.lazy('netbox.tests.dummy_plugin.graphql_extensions')
    ]]:
        return self.dummy_site_attachments.all()


@strawberry.type
class RackReservationTypeExtension:
    models = ['dcim.rackreservation']

    @strawberry_django.field
    def dummy_reservation_note(self) -> str:
        return 'dummy-reservation-note'


@strawberry.type
class SiteFilterExtension:
    models = ['dcim.site']

    @strawberry_django.filter_field()
    def dummy_plugin_filter(self, value: str, prefix) -> Q:
        return Q(**{f'{prefix}name': value})


type_extensions = [
    SiteTypeExtension,
    RackReservationTypeExtension,
]

filter_extensions = [
    SiteFilterExtension,
]
