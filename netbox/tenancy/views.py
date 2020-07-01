from django.db.models import Count
from django.shortcuts import get_object_or_404, render

from circuits.models import Circuit
from dcim.models import Site, Rack, Device, RackReservation
from ipam.models import IPAddress, Prefix, VLAN, VRF
from utilities.views import (
    BulkDeleteView, BulkEditView, BulkImportView, ObjectView, ObjectDeleteView, ObjectEditView, ObjectListView,
)
from virtualization.models import VirtualMachine, Cluster
from . import filters, forms, tables
from .models import Tenant, TenantGroup


#
# Tenant groups
#

class TenantGroupListView(ObjectListView):
    queryset = TenantGroup.objects.add_related_count(
        TenantGroup.objects.all(),
        Tenant,
        'group',
        'tenant_count',
        cumulative=True
    )
    table = tables.TenantGroupTable


class TenantGroupEditView(ObjectEditView):
    queryset = TenantGroup.objects.all()
    model_form = forms.TenantGroupForm


class TenantGroupBulkImportView(BulkImportView):
    queryset = TenantGroup.objects.all()
    model_form = forms.TenantGroupCSVForm
    table = tables.TenantGroupTable


class TenantGroupBulkDeleteView(BulkDeleteView):
    queryset = TenantGroup.objects.annotate(tenant_count=Count('tenants'))
    table = tables.TenantGroupTable


#
#  Tenants
#

class TenantListView(ObjectListView):
    queryset = Tenant.objects.prefetch_related('group')
    filterset = filters.TenantFilterSet
    filterset_form = forms.TenantFilterForm
    table = tables.TenantTable


class TenantView(ObjectView):
    queryset = Tenant.objects.prefetch_related('group')

    def get(self, request, slug):

        tenant = get_object_or_404(self.queryset, slug=slug)
        stats = {
            'site_count': Site.objects.restrict(request.user, 'view').filter(tenant=tenant).count(),
            'rack_count': Rack.objects.restrict(request.user, 'view').filter(tenant=tenant).count(),
            'rackreservation_count': RackReservation.objects.restrict(request.user, 'view').filter(tenant=tenant).count(),
            'device_count': Device.objects.restrict(request.user, 'view').filter(tenant=tenant).count(),
            'vrf_count': VRF.objects.restrict(request.user, 'view').filter(tenant=tenant).count(),
            'prefix_count': Prefix.objects.restrict(request.user, 'view').filter(tenant=tenant).count(),
            'ipaddress_count': IPAddress.objects.restrict(request.user, 'view').filter(tenant=tenant).count(),
            'vlan_count': VLAN.objects.restrict(request.user, 'view').filter(tenant=tenant).count(),
            'circuit_count': Circuit.objects.restrict(request.user, 'view').filter(tenant=tenant).count(),
            'virtualmachine_count': VirtualMachine.objects.restrict(request.user, 'view').filter(tenant=tenant).count(),
            'cluster_count': Cluster.objects.restrict(request.user, 'view').filter(tenant=tenant).count(),
        }

        return render(request, 'tenancy/tenant.html', {
            'tenant': tenant,
            'stats': stats,
        })


class TenantEditView(ObjectEditView):
    queryset = Tenant.objects.all()
    model_form = forms.TenantForm
    template_name = 'tenancy/tenant_edit.html'


class TenantDeleteView(ObjectDeleteView):
    queryset = Tenant.objects.all()


class TenantBulkImportView(BulkImportView):
    queryset = Tenant.objects.all()
    model_form = forms.TenantCSVForm
    table = tables.TenantTable


class TenantBulkEditView(BulkEditView):
    queryset = Tenant.objects.prefetch_related('group')
    filterset = filters.TenantFilterSet
    table = tables.TenantTable
    form = forms.TenantBulkEditForm


class TenantBulkDeleteView(BulkDeleteView):
    queryset = Tenant.objects.prefetch_related('group')
    filterset = filters.TenantFilterSet
    table = tables.TenantTable
