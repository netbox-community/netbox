from __future__ import unicode_literals

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import View

from dcim.models import Device, Interface
from dcim.tables import DeviceTable
from extras.views import ObjectConfigContextView
from ipam.models import Service
from utilities.views import (
    BulkComponentCreateView, BulkDeleteView, BulkEditView, BulkImportView, ComponentCreateView, ObjectDeleteView,
    ObjectEditView, ObjectListView,
)
from . import filters, forms, tables
from .models import Cluster, ClusterGroup, ClusterType, VirtualMachine


#
# Cluster types
#

class ClusterTypeListView(ObjectListView):
    queryset = ClusterType.objects.annotate(cluster_count=Count('clusters'))
    table = tables.ClusterTypeTable
    template_name = 'virtualization/clustertype_list.html'


class ClusterTypeCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'virtualization.add_clustertype'
    model = ClusterType
    model_form = forms.ClusterTypeForm
    default_return_url = 'virtualization:clustertype_list'


class ClusterTypeEditView(ClusterTypeCreateView):
    permission_required = 'virtualization.change_clustertype'


class ClusterTypeBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'virtualization.add_clustertype'
    model_form = forms.ClusterTypeCSVForm
    table = tables.ClusterTypeTable
    default_return_url = 'virtualization:clustertype_list'


class ClusterTypeBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'virtualization.delete_clustertype'
    queryset = ClusterType.objects.annotate(cluster_count=Count('clusters'))
    table = tables.ClusterTypeTable
    default_return_url = 'virtualization:clustertype_list'


#
# Cluster groups
#

class ClusterGroupListView(ObjectListView):
    queryset = ClusterGroup.objects.annotate(cluster_count=Count('clusters'))
    table = tables.ClusterGroupTable
    template_name = 'virtualization/clustergroup_list.html'


class ClusterGroupCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'virtualization.add_clustergroup'
    model = ClusterGroup
    model_form = forms.ClusterGroupForm
    default_return_url = 'virtualization:clustergroup_list'


class ClusterGroupEditView(ClusterGroupCreateView):
    permission_required = 'virtualization.change_clustergroup'


class ClusterGroupBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'virtualization.add_clustergroup'
    model_form = forms.ClusterGroupCSVForm
    table = tables.ClusterGroupTable
    default_return_url = 'virtualization:clustergroup_list'


class ClusterGroupBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'virtualization.delete_clustergroup'
    queryset = ClusterGroup.objects.annotate(cluster_count=Count('clusters'))
    table = tables.ClusterGroupTable
    default_return_url = 'virtualization:clustergroup_list'


#
# Clusters
#

class ClusterListView(ObjectListView):
    queryset = Cluster.objects.select_related('type', 'group', 'site')
    table = tables.ClusterTable
    filter = filters.ClusterFilter
    filter_form = forms.ClusterFilterForm
    template_name = 'virtualization/cluster_list.html'


class ClusterView(View):

    def get(self, request, pk):

        cluster = get_object_or_404(Cluster, pk=pk)
        devices = Device.objects.filter(cluster=cluster).select_related(
            'site', 'rack', 'tenant', 'device_type__manufacturer'
        )
        device_table = DeviceTable(list(devices), orderable=False)
        if request.user.has_perm('virtualization.change_cluster'):
            device_table.columns.show('pk')

        return render(request, 'virtualization/cluster.html', {
            'cluster': cluster,
            'device_table': device_table,
        })


class ClusterCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'virtualization.add_cluster'
    template_name = 'virtualization/cluster_edit.html'
    model = Cluster
    model_form = forms.ClusterForm


class ClusterEditView(ClusterCreateView):
    permission_required = 'virtualization.change_cluster'


class ClusterDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'virtualization.delete_cluster'
    model = Cluster
    default_return_url = 'virtualization:cluster_list'


class ClusterBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'virtualization.add_cluster'
    model_form = forms.ClusterCSVForm
    table = tables.ClusterTable
    default_return_url = 'virtualization:cluster_list'


class ClusterBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'virtualization.change_cluster'
    queryset = Cluster.objects.select_related('type', 'group', 'site')
    filter = filters.ClusterFilter
    table = tables.ClusterTable
    form = forms.ClusterBulkEditForm
    default_return_url = 'virtualization:cluster_list'


class ClusterBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'virtualization.delete_cluster'
    queryset = Cluster.objects.select_related('type', 'group', 'site')
    filter = filters.ClusterFilter
    table = tables.ClusterTable
    default_return_url = 'virtualization:cluster_list'


class ClusterAddDevicesView(PermissionRequiredMixin, View):
    permission_required = 'virtualization.change_cluster'
    form = forms.ClusterAddDevicesForm
    template_name = 'virtualization/cluster_add_devices.html'

    def get(self, request, pk):

        cluster = get_object_or_404(Cluster, pk=pk)
        form = self.form(cluster)

        return render(request, self.template_name, {
            'cluster': cluster,
            'form': form,
            'return_url': reverse('virtualization:cluster', kwargs={'pk': pk}),
        })

    def post(self, request, pk):

        cluster = get_object_or_404(Cluster, pk=pk)
        form = self.form(cluster, request.POST)

        if form.is_valid():

            device_pks = form.cleaned_data['devices']
            with transaction.atomic():

                # Assign the selected Devices to the Cluster
                for device in Device.objects.filter(pk__in=device_pks):
                    device.cluster = cluster
                    device.save()

            messages.success(request, "Added {} devices to cluster {}".format(
                len(device_pks), cluster
            ))
            return redirect(cluster.get_absolute_url())

        return render(request, self.template_name, {
            'cluster': cluster,
            'form': form,
            'return_url': cluster.get_absolute_url(),
        })


class ClusterRemoveDevicesView(PermissionRequiredMixin, View):
    permission_required = 'virtualization.change_cluster'
    form = forms.ClusterRemoveDevicesForm
    template_name = 'utilities/obj_bulk_remove.html'

    def post(self, request, pk):

        cluster = get_object_or_404(Cluster, pk=pk)

        if '_confirm' in request.POST:
            form = self.form(request.POST)
            if form.is_valid():

                device_pks = form.cleaned_data['pk']
                with transaction.atomic():

                    # Remove the selected Devices from the Cluster
                    for device in Device.objects.filter(pk__in=device_pks):
                        device.cluster = None
                        device.save()

                messages.success(request, "Removed {} devices from cluster {}".format(
                    len(device_pks), cluster
                ))
                return redirect(cluster.get_absolute_url())

        else:
            form = self.form(initial={'pk': request.POST.getlist('pk')})

        selected_objects = Device.objects.filter(pk__in=form.initial['pk'])
        device_table = DeviceTable(list(selected_objects), orderable=False)

        return render(request, self.template_name, {
            'form': form,
            'parent_obj': cluster,
            'table': device_table,
            'obj_type_plural': 'devices',
            'return_url': cluster.get_absolute_url(),
        })


#
# Virtual machines
#

class VirtualMachineListView(ObjectListView):
    queryset = VirtualMachine.objects.select_related('cluster', 'tenant', 'role', 'primary_ip4', 'primary_ip6')
    filter = filters.VirtualMachineFilter
    filter_form = forms.VirtualMachineFilterForm
    table = tables.VirtualMachineDetailTable
    template_name = 'virtualization/virtualmachine_list.html'


class VirtualMachineView(View):

    def get(self, request, pk):

        virtualmachine = get_object_or_404(VirtualMachine.objects.select_related('tenant__group'), pk=pk)
        interfaces = Interface.objects.filter(virtual_machine=virtualmachine)
        services = Service.objects.filter(virtual_machine=virtualmachine)

        return render(request, 'virtualization/virtualmachine.html', {
            'virtualmachine': virtualmachine,
            'interfaces': interfaces,
            'services': services,
        })


class VirtualMachineConfigContextView(ObjectConfigContextView):
    object_class = VirtualMachine
    base_template = 'virtualization/virtualmachine.html'


class VirtualMachineCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'virtualization.add_virtualmachine'
    model = VirtualMachine
    model_form = forms.VirtualMachineForm
    template_name = 'virtualization/virtualmachine_edit.html'
    default_return_url = 'virtualization:virtualmachine_list'


class VirtualMachineEditView(VirtualMachineCreateView):
    permission_required = 'virtualization.change_virtualmachine'


class VirtualMachineDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'virtualization.delete_virtualmachine'
    model = VirtualMachine
    default_return_url = 'virtualization:virtualmachine_list'


class VirtualMachineBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'virtualization.add_virtualmachine'
    model_form = forms.VirtualMachineCSVForm
    table = tables.VirtualMachineTable
    default_return_url = 'virtualization:virtualmachine_list'


class VirtualMachineBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'virtualization.change_virtualmachine'
    queryset = VirtualMachine.objects.select_related('cluster', 'tenant', 'role')
    filter = filters.VirtualMachineFilter
    table = tables.VirtualMachineTable
    form = forms.VirtualMachineBulkEditForm
    default_return_url = 'virtualization:virtualmachine_list'


class VirtualMachineBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'virtualization.delete_virtualmachine'
    queryset = VirtualMachine.objects.select_related('cluster', 'tenant', 'role')
    filter = filters.VirtualMachineFilter
    table = tables.VirtualMachineTable
    default_return_url = 'virtualization:virtualmachine_list'


#
# VM interfaces
#

class InterfaceCreateView(PermissionRequiredMixin, ComponentCreateView):
    permission_required = 'dcim.add_interface'
    parent_model = VirtualMachine
    parent_field = 'virtual_machine'
    model = Interface
    form = forms.InterfaceCreateForm
    model_form = forms.InterfaceForm
    template_name = 'virtualization/virtualmachine_component_add.html'


class InterfaceEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'dcim.change_interface'
    model = Interface
    model_form = forms.InterfaceForm
    template_name = 'virtualization/interface_edit.html'


class InterfaceDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'dcim.delete_interface'
    model = Interface


class InterfaceBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'dcim.change_interface'
    queryset = Interface.objects.all()
    parent_model = VirtualMachine
    table = tables.InterfaceTable
    form = forms.InterfaceBulkEditForm


class InterfaceBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'dcim.delete_interface'
    queryset = Interface.objects.all()
    parent_model = VirtualMachine
    table = tables.InterfaceTable


#
# Bulk Device component creation
#

class VirtualMachineBulkAddInterfaceView(PermissionRequiredMixin, BulkComponentCreateView):
    permission_required = 'dcim.add_interface'
    parent_model = VirtualMachine
    parent_field = 'virtual_machine'
    form = forms.VirtualMachineBulkAddInterfaceForm
    model = Interface
    model_form = forms.InterfaceForm
    table = tables.VirtualMachineTable
    default_return_url = 'virtualization:virtualmachine_list'
