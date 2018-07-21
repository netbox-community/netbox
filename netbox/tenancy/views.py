from __future__ import unicode_literals

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render
from django.views.generic import View

from circuits.models import Circuit
from dcim.models import Site, Rack, Device, RackReservation
from ipam.models import IPAddress, Prefix, VLAN, VRF
from utilities.views import (
    BulkDeleteView, BulkEditView, BulkImportView, ObjectDeleteView, ObjectEditView, ObjectListView,
)
from virtualization.models import VirtualMachine
from . import filters, forms, tables
from .models import Tenant, TenantGroup


#
# Tenant groups
#

class TenantGroupListView(ObjectListView):
    queryset = TenantGroup.objects.annotate(tenant_count=Count('tenants'))
    table = tables.TenantGroupTable
    template_name = 'tenancy/tenantgroup_list.html'


class TenantGroupCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'tenancy.add_tenantgroup'
    model = TenantGroup
    model_form = forms.TenantGroupForm
    default_return_url = 'tenancy:tenantgroup_list'


class TenantGroupEditView(TenantGroupCreateView):
    permission_required = 'tenancy.change_tenantgroup'


class TenantGroupBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'tenancy.add_tenantgroup'
    model_form = forms.TenantGroupCSVForm
    table = tables.TenantGroupTable
    default_return_url = 'tenancy:tenantgroup_list'


class TenantGroupBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'tenancy.delete_tenantgroup'
    queryset = TenantGroup.objects.annotate(tenant_count=Count('tenants'))
    table = tables.TenantGroupTable
    default_return_url = 'tenancy:tenantgroup_list'


#
#  Tenants
#

class TenantListView(ObjectListView):
    queryset = Tenant.objects.select_related('group')
    filter = filters.TenantFilter
    filter_form = forms.TenantFilterForm
    table = tables.TenantTable
    template_name = 'tenancy/tenant_list.html'


class TenantView(View):

    def get(self, request, slug):

        tenant = get_object_or_404(Tenant, slug=slug)
        stats = {
            'site_count': Site.objects.filter(tenant=tenant).count(),
            'rack_count': Rack.objects.filter(tenant=tenant).count(),
            'rackreservation_count': RackReservation.objects.filter(tenant=tenant).count(),
            'device_count': Device.objects.filter(tenant=tenant).count(),
            'vrf_count': VRF.objects.filter(tenant=tenant).count(),
            'prefix_count': Prefix.objects.filter(tenant=tenant).count(),
            'ipaddress_count': IPAddress.objects.filter(tenant=tenant).count(),
            'vlan_count': VLAN.objects.filter(tenant=tenant).count(),
            'circuit_count': Circuit.objects.filter(tenant=tenant).count(),
            'virtualmachine_count': VirtualMachine.objects.filter(tenant=tenant).count(),
        }

        return render(request, 'tenancy/tenant.html', {
            'tenant': tenant,
            'stats': stats,
        })


class TenantCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'tenancy.add_tenant'
    model = Tenant
    model_form = forms.TenantForm
    template_name = 'tenancy/tenant_edit.html'
    default_return_url = 'tenancy:tenant_list'


class TenantEditView(TenantCreateView):
    permission_required = 'tenancy.change_tenant'


class TenantDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'tenancy.delete_tenant'
    model = Tenant
    default_return_url = 'tenancy:tenant_list'


class TenantBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'tenancy.add_tenant'
    model_form = forms.TenantCSVForm
    table = tables.TenantTable
    default_return_url = 'tenancy:tenant_list'


class TenantBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'tenancy.change_tenant'
    queryset = Tenant.objects.select_related('group')
    filter = filters.TenantFilter
    table = tables.TenantTable
    form = forms.TenantBulkEditForm
    default_return_url = 'tenancy:tenant_list'


class TenantBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'tenancy.delete_tenant'
    queryset = Tenant.objects.select_related('group')
    filter = filters.TenantFilter
    table = tables.TenantTable
    default_return_url = 'tenancy:tenant_list'
