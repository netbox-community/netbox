from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, render

from utilities.views import (
    BulkDeleteView, BulkEditView, BulkImportView, ObjectDeleteView, ObjectEditView, ObjectListView,
)

from models import Tenant, TenantGroup
from . import filters, forms, tables


#
# Tenant groups
#

class TenantGroupListView(ObjectListView):
    queryset = TenantGroup.objects.annotate(tenant_count=Count('tenants'))
    table = tables.TenantGroupTable
    edit_permissions = ['tenancy.change_tenantgroup', 'tenancy.delete_tenantgroup']
    template_name = 'tenancy/tenantgroup_list.html'


class TenantGroupEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'tenancy.change_tenantgroup'
    model = TenantGroup
    form_class = forms.TenantGroupForm
    success_url = 'tenancy:tenantgroup_list'
    cancel_url = 'tenancy:tenantgroup_list'


class TenantGroupBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'tenancy.delete_tenantgroup'
    cls = TenantGroup
    default_redirect_url = 'tenancy:tenantgroup_list'


#
#  Tenants
#

class TenantListView(ObjectListView):
    queryset = Tenant.objects.select_related('group')
    filter = filters.TenantFilter
    filter_form = forms.TenantFilterForm
    table = tables.TenantTable
    edit_permissions = ['tenancy.change_tenant', 'tenancy.delete_tenant']
    template_name = 'tenancy/tenant_list.html'


def tenant(request, slug):

    tenant = get_object_or_404(Tenant.objects.annotate(
        site_count=Count('sites', distinct=True),
        rack_count=Count('racks', distinct=True),
        device_count=Count('devices', distinct=True),
        vrf_count=Count('vrfs', distinct=True),
        prefix_count=Count('prefixes', distinct=True),
        ipaddress_count=Count('ip_addresses', distinct=True),
        vlan_count=Count('vlans', distinct=True),
        circuit_count=Count('circuits', distinct=True),
    ), slug=slug)

    return render(request, 'tenancy/tenant.html', {
        'tenant': tenant,
    })


class TenantEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'tenancy.change_tenant'
    model = Tenant
    form_class = forms.TenantForm
    fields_initial = ['group']
    template_name = 'tenancy/tenant_edit.html'
    cancel_url = 'tenancy:tenant_list'


class TenantDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'tenancy.delete_tenant'
    model = Tenant
    redirect_url = 'tenancy:tenant_list'


class TenantBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'tenancy.add_tenant'
    form = forms.TenantImportForm
    table = tables.TenantTable
    template_name = 'tenancy/tenant_import.html'
    obj_list_url = 'tenancy:tenant_list'


class TenantBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'tenancy.change_tenant'
    cls = Tenant
    form = forms.TenantBulkEditForm
    template_name = 'tenancy/tenant_bulk_edit.html'
    default_redirect_url = 'tenancy:tenant_list'

    def update_objects(self, pk_list, form):

        fields_to_update = {}
        if form.cleaned_data['group'] == 0:
            fields_to_update['group'] = None
        elif form.cleaned_data['group']:
            fields_to_update['group'] = form.cleaned_data['group']

        return self.cls.objects.filter(pk__in=pk_list).update(**fields_to_update)


class TenantBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'tenancy.delete_tenant'
    cls = Tenant
    default_redirect_url = 'tenancy:tenant_list'
