from django.urls import reverse

from netbox.ui.breadcrumbs import Breadcrumb, BreadcrumbTrail, register_breadcrumbs
from tenancy.models import ContactGroup, Tenant


@register_breadcrumbs
class TenantBreadcrumbs(BreadcrumbTrail):
    model = Tenant
    items = (
        Breadcrumb(
            lambda o: o.group.get_ancestors(include_self=True) if o.group else [],
            url=lambda group: f"{reverse('tenancy:tenant_list')}?group_id={group.pk}",
        ),
    )


@register_breadcrumbs
class ContactGroupBreadcrumbs(BreadcrumbTrail):
    model = ContactGroup
    items = (
        Breadcrumb(
            lambda o: o.get_ancestors(),
            url=lambda a: f"{reverse('tenancy:contactgroup_list')}?parent_id={a.pk}",
        ),
    )
