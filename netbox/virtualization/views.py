from __future__ import unicode_literals

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import View

from dcim.models import Device
from dcim.tables import DeviceTable
from utilities.views import (
    BulkDeleteView, BulkEditView, BulkImportView, ComponentCreateView, ComponentDeleteView, ComponentEditView,
    ObjectDeleteView, ObjectEditView, ObjectListView,
)
from .models import Cluster, ClusterGroup, ClusterType, VirtualMachine, VMInterface
from . import filters
from . import forms
from . import tables


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
    form_class = forms.ClusterTypeForm

    def get_return_url(self, request, obj):
        return reverse('virtualization:clustertype_list')


class ClusterTypeEditView(ClusterTypeCreateView):
    permission_required = 'virtualization.change_clustertype'


class ClusterTypeBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'virtualization.delete_clustertype'
    cls = ClusterType
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
    form_class = forms.ClusterGroupForm

    def get_return_url(self, request, obj):
        return reverse('virtualization:clustergroup_list')


class ClusterGroupEditView(ClusterGroupCreateView):
    permission_required = 'virtualization.change_clustergroup'


class ClusterGroupBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'virtualization.delete_clustergroup'
    cls = ClusterGroup
    queryset = ClusterGroup.objects.annotate(cluster_count=Count('clusters'))
    table = tables.ClusterGroupTable
    default_return_url = 'virtualization:clustergroup_list'


#
# Clusters
#

class ClusterListView(ObjectListView):
    queryset = Cluster.objects.annotate(vm_count=Count('virtual_machines'))
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
        if request.user.has_perm('virtualization:change_cluster'):
            device_table.columns.show('pk')

        return render(request, 'virtualization/cluster.html', {
            'cluster': cluster,
            'device_table': device_table,
        })


class ClusterCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'virtualization.add_cluster'
    model = Cluster
    form_class = forms.ClusterForm


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


class ClusterBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'virtualization.delete_cluster'
    cls = Cluster
    queryset = Cluster.objects.annotate(vm_count=Count('virtual_machines'))
    table = tables.ClusterTable
    default_return_url = 'virtualization:cluster_list'


class ClusterAddDevicesView(PermissionRequiredMixin, View):
    permission_required = 'virtualization.change_cluster'
    form = forms.ClusterAddDevicesForm
    template_name = 'virtualization/cluster_add_devices.html'

    def get(self, request, pk):

        cluster = get_object_or_404(Cluster, pk=pk)
        form = self.form()

        return render(request, self.template_name, {
            'cluster': cluster,
            'form': form,
            'return_url': reverse('virtualization:cluster', kwargs={'pk': pk}),
        })

    def post(self, request, pk):

        cluster = get_object_or_404(Cluster, pk=pk)
        form = self.form(request.POST)

        if form.is_valid():

            # Assign the selected Devices to the Cluster
            devices = form.cleaned_data['devices']
            Device.objects.filter(pk__in=devices).update(cluster=cluster)

            messages.success(request, "Added {} devices to cluster {}".format(
                len(devices), cluster
            ))
            return redirect(cluster.get_absolute_url())

        return render(request, self.template_name, {
            'cluser': cluster,
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

                # Remove the selected Devices from the Cluster
                devices = form.cleaned_data['pk']
                Device.objects.filter(pk__in=devices).update(cluster=None)

                messages.success(request, "Removed {} devices from cluster {}".format(
                    len(devices), cluster
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
    queryset = VirtualMachine.objects.select_related('tenant')
    filter = filters.VirtualMachineFilter
    filter_form = forms.VirtualMachineFilterForm
    table = tables.VirtualMachineTable
    template_name = 'virtualization/virtualmachine_list.html'


class VirtualMachineView(View):

    def get(self, request, pk):

        vm = get_object_or_404(VirtualMachine.objects.select_related('tenant__group'), pk=pk)
        interfaces = VMInterface.objects.filter(virtual_machine=vm)

        return render(request, 'virtualization/virtualmachine.html', {
            'vm': vm,
            'interfaces': interfaces,
        })


class VirtualMachineCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'virtualization.add_virtualmachine'
    model = VirtualMachine
    form_class = forms.VirtualMachineForm
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
    cls = VirtualMachine
    queryset = VirtualMachine.objects.select_related('tenant')
    filter = filters.VirtualMachineFilter
    table = tables.VirtualMachineTable
    form = forms.VirtualMachineBulkEditForm
    default_return_url = 'virtualization:virtualmachine_list'


#
# VM interfaces
#

class VMInterfaceCreateView(PermissionRequiredMixin, ComponentCreateView):
    permission_required = 'virtualization.add_vminterface'
    parent_model = VirtualMachine
    parent_field = 'virtual_machine'
    model = VMInterface
    form = forms.VMInterfaceCreateForm
    model_form = forms.VMInterfaceForm
    template_name = 'virtualization/virtualmachine_component_add.html'


class VMInterfaceEditView(PermissionRequiredMixin, ComponentEditView):
    permission_required = 'virtualization.change_vminterface'
    model = VMInterface
    parent_field = 'virtual_machine'
    form_class = forms.VMInterfaceForm


class VMInterfaceDeleteView(PermissionRequiredMixin, ComponentDeleteView):
    permission_required = 'virtualization.delete_vminterface'
    model = VMInterface
    parent_field = 'virtual_machine'


class VMInterfaceBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'virtualization.change_vminterface'
    cls = VMInterface
    parent_cls = VirtualMachine
    table = tables.VMInterfaceTable
    form = forms.VMInterfaceBulkEditForm


class VMInterfaceBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'virtualization.delete_vminterface'
    cls = VMInterface
    parent_cls = VirtualMachine
    table = tables.VMInterfaceTable
