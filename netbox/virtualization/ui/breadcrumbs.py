from django.urls import reverse

from netbox.ui.breadcrumbs import Breadcrumb, BreadcrumbTrail, register_breadcrumbs
from virtualization.models import VirtualDisk, VMInterface


@register_breadcrumbs
class VMInterfaceBreadcrumbs(BreadcrumbTrail):
    model = VMInterface
    items = (
        Breadcrumb(
            'virtual_machine',
            url=lambda o: reverse('virtualization:virtualmachine_interfaces', kwargs={'pk': o.pk}),
        ),
    )


@register_breadcrumbs
class VirtualDiskBreadcrumbs(BreadcrumbTrail):
    model = VirtualDisk
    items = (
        Breadcrumb(
            'virtual_machine',
            url=lambda o: reverse('virtualization:virtualmachine_disks', kwargs={'pk': o.pk}),
        ),
    )
