from django.urls import reverse

from core.models import DataFile
from netbox.ui.breadcrumbs import Breadcrumb, BreadcrumbTrail, register_breadcrumbs


@register_breadcrumbs
class DataFileBreadcrumbs(BreadcrumbTrail):
    model = DataFile
    items = (
        Breadcrumb('source', url=lambda o: f"{reverse('core:datafile_list')}?source_id={o.pk}"),
    )
