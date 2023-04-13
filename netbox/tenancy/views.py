from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

from circuits.models import Circuit
from dcim.models import Cable, Device, Location, Rack, RackReservation, Site, VirtualDeviceContext
from ipam.models import Aggregate, ASN, IPAddress, IPRange, L2VPN, Prefix, VLAN, VRF
from netbox.views import generic
from utilities.utils import count_related
from utilities.views import register_model_view
from virtualization.models import VirtualMachine, Cluster
from wireless.models import WirelessLAN, WirelessLink
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


@register_model_view(TenantGroup)
class TenantGroupView(generic.ObjectView):
    queryset = TenantGroup.objects.all()

    def get_extra_context(self, request, instance):
        tenants = Tenant.objects.restrict(request.user, 'view').filter(
            group=instance
        )
        tenants_table = tables.TenantTable(tenants, user=request.user, exclude=('group',))
        tenants_table.configure(request)

        return {
            'tenants_table': tenants_table,
        }


@register_model_view(TenantGroup, 'edit')
class TenantGroupEditView(generic.ObjectEditView):
    queryset = TenantGroup.objects.all()
    form = forms.TenantGroupForm


@register_model_view(TenantGroup, 'delete')
class TenantGroupDeleteView(generic.ObjectDeleteView):
    queryset = TenantGroup.objects.all()


class TenantGroupBulkImportView(generic.BulkImportView):
    queryset = TenantGroup.objects.all()
    model_form = forms.TenantGroupImportForm
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
    filterset = filtersets.TenantGroupFilterSet
    table = tables.TenantGroupTable


#
#  Tenants
#

class TenantListView(generic.ObjectListView):
    queryset = Tenant.objects.all()
    filterset = filtersets.TenantFilterSet
    filterset_form = forms.TenantFilterForm
    table = tables.TenantTable


@register_model_view(Tenant)
class TenantView(generic.ObjectView):
    queryset = Tenant.objects.all()

    def get_extra_context(self, request, instance):
        stats = {
            'site_count': Site.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'rack_count': Rack.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'rackreservation_count': RackReservation.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'location_count': Location.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'device_count': Device.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'vdc_count': VirtualDeviceContext.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'vrf_count': VRF.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'aggregate_count': Aggregate.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'prefix_count': Prefix.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'iprange_count': IPRange.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'ipaddress_count': IPAddress.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'vlan_count': VLAN.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'l2vpn_count': L2VPN.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'circuit_count': Circuit.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'virtualmachine_count': VirtualMachine.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'cluster_count': Cluster.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'cable_count': Cable.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'asn_count': ASN.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'wirelesslan_count': WirelessLAN.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'wirelesslink_count': WirelessLink.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
        }

        return {
            'stats': stats,
        }


@register_model_view(Tenant, 'edit')
class TenantEditView(generic.ObjectEditView):
    queryset = Tenant.objects.all()
    form = forms.TenantForm


@register_model_view(Tenant, 'delete')
class TenantDeleteView(generic.ObjectDeleteView):
    queryset = Tenant.objects.all()


class TenantBulkImportView(generic.BulkImportView):
    queryset = Tenant.objects.all()
    model_form = forms.TenantImportForm
    table = tables.TenantTable


class TenantBulkEditView(generic.BulkEditView):
    queryset = Tenant.objects.all()
    filterset = filtersets.TenantFilterSet
    table = tables.TenantTable
    form = forms.TenantBulkEditForm


class TenantBulkDeleteView(generic.BulkDeleteView):
    queryset = Tenant.objects.all()
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


@register_model_view(ContactGroup)
class ContactGroupView(generic.ObjectView):
    queryset = ContactGroup.objects.all()

    def get_extra_context(self, request, instance):
        child_groups = ContactGroup.objects.add_related_count(
            ContactGroup.objects.all(),
            Contact,
            'group',
            'contact_count',
            cumulative=True
        ).restrict(request.user, 'view').filter(
            parent__in=instance.get_descendants(include_self=True)
        )
        child_groups_table = tables.ContactGroupTable(child_groups)
        child_groups_table.columns.hide('actions')

        contacts = Contact.objects.restrict(request.user, 'view').filter(
            group=instance
        ).annotate(
            assignment_count=count_related(ContactAssignment, 'contact')
        )
        contacts_table = tables.ContactTable(contacts, user=request.user, exclude=('group',))
        contacts_table.configure(request)

        return {
            'child_groups_table': child_groups_table,
            'contacts_table': contacts_table,
        }


@register_model_view(ContactGroup, 'edit')
class ContactGroupEditView(generic.ObjectEditView):
    queryset = ContactGroup.objects.all()
    form = forms.ContactGroupForm


@register_model_view(ContactGroup, 'delete')
class ContactGroupDeleteView(generic.ObjectDeleteView):
    queryset = ContactGroup.objects.all()


class ContactGroupBulkImportView(generic.BulkImportView):
    queryset = ContactGroup.objects.all()
    model_form = forms.ContactGroupImportForm
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
    filterset = filtersets.ContactGroupFilterSet
    table = tables.ContactGroupTable


#
# Contact roles
#

class ContactRoleListView(generic.ObjectListView):
    queryset = ContactRole.objects.all()
    filterset = filtersets.ContactRoleFilterSet
    filterset_form = forms.ContactRoleFilterForm
    table = tables.ContactRoleTable


@register_model_view(ContactRole)
class ContactRoleView(generic.ObjectView):
    queryset = ContactRole.objects.all()

    def get_extra_context(self, request, instance):
        contact_assignments = ContactAssignment.objects.restrict(request.user, 'view').filter(
            role=instance
        )
        contacts_table = tables.ContactAssignmentTable(contact_assignments, user=request.user)
        contacts_table.columns.hide('role')
        contacts_table.configure(request)

        return {
            'contacts_table': contacts_table,
            'assignment_count': ContactAssignment.objects.filter(role=instance).count(),
        }


@register_model_view(ContactRole, 'edit')
class ContactRoleEditView(generic.ObjectEditView):
    queryset = ContactRole.objects.all()
    form = forms.ContactRoleForm


@register_model_view(ContactRole, 'delete')
class ContactRoleDeleteView(generic.ObjectDeleteView):
    queryset = ContactRole.objects.all()


class ContactRoleBulkImportView(generic.BulkImportView):
    queryset = ContactRole.objects.all()
    model_form = forms.ContactRoleImportForm
    table = tables.ContactRoleTable


class ContactRoleBulkEditView(generic.BulkEditView):
    queryset = ContactRole.objects.all()
    filterset = filtersets.ContactRoleFilterSet
    table = tables.ContactRoleTable
    form = forms.ContactRoleBulkEditForm


class ContactRoleBulkDeleteView(generic.BulkDeleteView):
    queryset = ContactRole.objects.all()
    filterset = filtersets.ContactRoleFilterSet
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


@register_model_view(Contact)
class ContactView(generic.ObjectView):
    queryset = Contact.objects.all()

    def get_extra_context(self, request, instance):
        contact_assignments = ContactAssignment.objects.restrict(request.user, 'view').filter(
            contact=instance
        )
        assignments_table = tables.ContactAssignmentTable(contact_assignments, user=request.user)
        assignments_table.columns.hide('contact')
        assignments_table.configure(request)

        return {
            'assignments_table': assignments_table,
            'assignment_count': ContactAssignment.objects.filter(contact=instance).count(),
        }


@register_model_view(Contact, 'edit')
class ContactEditView(generic.ObjectEditView):
    queryset = Contact.objects.all()
    form = forms.ContactForm


@register_model_view(Contact, 'delete')
class ContactDeleteView(generic.ObjectDeleteView):
    queryset = Contact.objects.all()


class ContactBulkImportView(generic.BulkImportView):
    queryset = Contact.objects.all()
    model_form = forms.ContactImportForm
    table = tables.ContactTable


class ContactBulkEditView(generic.BulkEditView):
    queryset = Contact.objects.annotate(
        assignment_count=count_related(ContactAssignment, 'contact')
    )
    filterset = filtersets.ContactFilterSet
    table = tables.ContactTable
    form = forms.ContactBulkEditForm


class ContactBulkDeleteView(generic.BulkDeleteView):
    queryset = Contact.objects.annotate(
        assignment_count=count_related(ContactAssignment, 'contact')
    )
    filterset = filtersets.ContactFilterSet
    table = tables.ContactTable


#
# Contact assignments
#

@register_model_view(ContactAssignment, 'edit')
class ContactAssignmentEditView(generic.ObjectEditView):
    queryset = ContactAssignment.objects.all()
    form = forms.ContactAssignmentForm
    template_name = 'tenancy/contactassignment_edit.html'

    def alter_object(self, instance, request, args, kwargs):
        if not instance.pk:
            # Assign the object based on URL kwargs
            content_type = get_object_or_404(ContentType, pk=request.GET.get('content_type'))
            instance.object = get_object_or_404(content_type.model_class(), pk=request.GET.get('object_id'))
        return instance

    def get_extra_addanother_params(self, request):
        return {
            'content_type': request.GET.get('content_type'),
            'object_id': request.GET.get('object_id'),
        }


@register_model_view(ContactAssignment, 'delete')
class ContactAssignmentDeleteView(generic.ObjectDeleteView):
    queryset = ContactAssignment.objects.all()
