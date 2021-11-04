from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import get_object_or_404

from circuits.models import Circuit
from dcim.models import Site, Rack, Device, RackReservation
from ipam.models import Aggregate, IPAddress, Prefix, VLAN, VRF
from netbox.views import generic
from utilities.tables import paginate_table
from utilities.utils import count_related
from virtualization.models import VirtualMachine, Cluster
from . import filtersets, forms, tables
from .models import *


#
# Tenant groups
#

class TenantGroupListView(generic.ObjectListView):
    queryset = TenantGroup.objects.add_related_count(
        TenantGroup.objects.all(),
        Tenant,
        'group',
        'tenant_count',
        cumulative=True
    )
    filterset = filtersets.TenantGroupFilterSet
    filterset_form = forms.TenantGroupFilterForm
    table = tables.TenantGroupTable


class TenantGroupView(generic.ObjectView):
    queryset = TenantGroup.objects.all()

    def get_extra_context(self, request, instance):
        tenants = Tenant.objects.restrict(request.user, 'view').filter(
            group=instance
        )
        tenants_table = tables.TenantTable(tenants, exclude=('group',))
        paginate_table(tenants_table, request)

        return {
            'tenants_table': tenants_table,
        }


class TenantGroupEditView(generic.ObjectEditView):
    queryset = TenantGroup.objects.all()
    model_form = forms.TenantGroupForm


class TenantGroupDeleteView(generic.ObjectDeleteView):
    queryset = TenantGroup.objects.all()


class TenantGroupBulkImportView(generic.BulkImportView):
    queryset = TenantGroup.objects.all()
    model_form = forms.TenantGroupCSVForm
    table = tables.TenantGroupTable


class TenantGroupBulkEditView(generic.BulkEditView):
    queryset = TenantGroup.objects.add_related_count(
        TenantGroup.objects.all(),
        Tenant,
        'group',
        'tenant_count',
        cumulative=True
    )
    filterset = filtersets.TenantGroupFilterSet
    table = tables.TenantGroupTable
    form = forms.TenantGroupBulkEditForm


class TenantGroupBulkDeleteView(generic.BulkDeleteView):
    queryset = TenantGroup.objects.add_related_count(
        TenantGroup.objects.all(),
        Tenant,
        'group',
        'tenant_count',
        cumulative=True
    )
    table = tables.TenantGroupTable


#
#  Tenants
#

class TenantListView(generic.ObjectListView):
    queryset = Tenant.objects.all()
    filterset = filtersets.TenantFilterSet
    filterset_form = forms.TenantFilterForm
    table = tables.TenantTable


class TenantView(generic.ObjectView):
    queryset = Tenant.objects.prefetch_related('group')

    def get_extra_context(self, request, instance):
        stats = {
            'site_count': Site.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'rack_count': Rack.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'rackreservation_count': RackReservation.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'device_count': Device.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'vrf_count': VRF.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'prefix_count': Prefix.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'aggregate_count': Aggregate.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'ipaddress_count': IPAddress.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'vlan_count': VLAN.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'circuit_count': Circuit.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'virtualmachine_count': VirtualMachine.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'cluster_count': Cluster.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
        }

        return {
            'stats': stats,
        }


class TenantEditView(generic.ObjectEditView):
    queryset = Tenant.objects.all()
    model_form = forms.TenantForm


class TenantDeleteView(generic.ObjectDeleteView):
    queryset = Tenant.objects.all()


class TenantBulkImportView(generic.BulkImportView):
    queryset = Tenant.objects.all()
    model_form = forms.TenantCSVForm
    table = tables.TenantTable


class TenantBulkEditView(generic.BulkEditView):
    queryset = Tenant.objects.prefetch_related('group')
    filterset = filtersets.TenantFilterSet
    table = tables.TenantTable
    form = forms.TenantBulkEditForm


class TenantBulkDeleteView(generic.BulkDeleteView):
    queryset = Tenant.objects.prefetch_related('group')
    filterset = filtersets.TenantFilterSet
    table = tables.TenantTable


#
# Contact groups
#

class ContactGroupListView(generic.ObjectListView):
    queryset = ContactGroup.objects.add_related_count(
        ContactGroup.objects.all(),
        Contact,
        'group',
        'contact_count',
        cumulative=True
    )
    filterset = filtersets.ContactGroupFilterSet
    filterset_form = forms.ContactGroupFilterForm
    table = tables.ContactGroupTable


class ContactGroupView(generic.ObjectView):
    queryset = ContactGroup.objects.all()

    def get_extra_context(self, request, instance):
        contacts = Contact.objects.restrict(request.user, 'view').filter(
            group=instance
        )
        contacts_table = tables.ContactTable(contacts, exclude=('group',))
        paginate_table(contacts_table, request)

        return {
            'contacts_table': contacts_table,
        }


class ContactGroupEditView(generic.ObjectEditView):
    queryset = ContactGroup.objects.all()
    model_form = forms.ContactGroupForm


class ContactGroupDeleteView(generic.ObjectDeleteView):
    queryset = ContactGroup.objects.all()


class ContactGroupBulkImportView(generic.BulkImportView):
    queryset = ContactGroup.objects.all()
    model_form = forms.ContactGroupCSVForm
    table = tables.ContactGroupTable


class ContactGroupBulkEditView(generic.BulkEditView):
    queryset = ContactGroup.objects.add_related_count(
        ContactGroup.objects.all(),
        Contact,
        'group',
        'contact_count',
        cumulative=True
    )
    filterset = filtersets.ContactGroupFilterSet
    table = tables.ContactGroupTable
    form = forms.ContactGroupBulkEditForm


class ContactGroupBulkDeleteView(generic.BulkDeleteView):
    queryset = ContactGroup.objects.add_related_count(
        ContactGroup.objects.all(),
        Contact,
        'group',
        'contact_count',
        cumulative=True
    )
    table = tables.ContactGroupTable


#
# Contact roles
#

class ContactRoleListView(generic.ObjectListView):
    queryset = ContactRole.objects.all()
    filterset = filtersets.ContactRoleFilterSet
    filterset_form = forms.ContactRoleFilterForm
    table = tables.ContactRoleTable


class ContactRoleView(generic.ObjectView):
    queryset = ContactRole.objects.all()

    def get_extra_context(self, request, instance):
        contact_assignments = ContactAssignment.objects.restrict(request.user, 'view').filter(
            role=instance
        )
        contacts_table = tables.ContactAssignmentTable(contact_assignments)
        contacts_table.columns.hide('role')
        paginate_table(contacts_table, request)

        return {
            'contacts_table': contacts_table,
            'assignment_count': ContactAssignment.objects.filter(role=instance).count(),
        }


class ContactRoleEditView(generic.ObjectEditView):
    queryset = ContactRole.objects.all()
    model_form = forms.ContactRoleForm


class ContactRoleDeleteView(generic.ObjectDeleteView):
    queryset = ContactRole.objects.all()


class ContactRoleBulkImportView(generic.BulkImportView):
    queryset = ContactRole.objects.all()
    model_form = forms.ContactRoleCSVForm
    table = tables.ContactRoleTable


class ContactRoleBulkEditView(generic.BulkEditView):
    queryset = ContactRole.objects.all()
    filterset = filtersets.ContactRoleFilterSet
    table = tables.ContactRoleTable
    form = forms.ContactRoleBulkEditForm


class ContactRoleBulkDeleteView(generic.BulkDeleteView):
    queryset = ContactRole.objects.all()
    table = tables.ContactRoleTable


#
# Contacts
#

class ContactListView(generic.ObjectListView):
    queryset = Contact.objects.annotate(
        assignment_count=count_related(ContactAssignment, 'contact')
    )
    filterset = filtersets.ContactFilterSet
    filterset_form = forms.ContactFilterForm
    table = tables.ContactTable


class ContactView(generic.ObjectView):
    queryset = Contact.objects.all()

    def get_extra_context(self, request, instance):
        contact_assignments = ContactAssignment.objects.restrict(request.user, 'view').filter(
            contact=instance
        )
        contacts_table = tables.ContactAssignmentTable(contact_assignments)
        contacts_table.columns.hide('contact')
        paginate_table(contacts_table, request)

        return {
            'contacts_table': contacts_table,
            'assignment_count': ContactAssignment.objects.filter(contact=instance).count(),
        }


class ContactEditView(generic.ObjectEditView):
    queryset = Contact.objects.all()
    model_form = forms.ContactForm


class ContactDeleteView(generic.ObjectDeleteView):
    queryset = Contact.objects.all()


class ContactBulkImportView(generic.BulkImportView):
    queryset = Contact.objects.all()
    model_form = forms.ContactCSVForm
    table = tables.ContactTable


class ContactBulkEditView(generic.BulkEditView):
    queryset = Contact.objects.prefetch_related('group')
    filterset = filtersets.ContactFilterSet
    table = tables.ContactTable
    form = forms.ContactBulkEditForm


class ContactBulkDeleteView(generic.BulkDeleteView):
    queryset = Contact.objects.prefetch_related('group')
    filterset = filtersets.ContactFilterSet
    table = tables.ContactTable


#
# Contact assignments
#

class ContactAssignmentEditView(generic.ObjectEditView):
    queryset = ContactAssignment.objects.all()
    model_form = forms.ContactAssignmentForm
    template_name = 'tenancy/contactassignment_edit.html'

    def alter_obj(self, instance, request, args, kwargs):
        if not instance.pk:
            # Assign the object based on URL kwargs
            try:
                app_label, model = request.GET.get('content_type').split('.')
            except (AttributeError, ValueError):
                raise Http404("Content type not specified")
            content_type = get_object_or_404(ContentType, app_label=app_label, model=model)
            instance.object = get_object_or_404(content_type.model_class(), pk=request.GET.get('object_id'))
        return instance

    def get_return_url(self, request, obj=None):
        return obj.object.get_absolute_url() if obj else super().get_return_url(request)


class ContactAssignmentDeleteView(generic.ObjectDeleteView):
    queryset = ContactAssignment.objects.all()

    def get_return_url(self, request, obj=None):
        return obj.object.get_absolute_url() if obj else super().get_return_url(request)
