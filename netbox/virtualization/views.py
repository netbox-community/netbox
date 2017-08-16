from __future__ import unicode_literals

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import View

from dcim.models import Device
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
        devices = Device.objects.filter(cluster=cluster)

        return render(request, 'virtualization/cluster.html', {
            'cluster': cluster,
            'devices': devices,
        })


class ClusterCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'virtualization.add_cluster'
    model = Cluster
    form_class = forms.ClusterForm

    def get_return_url(self, request, obj):
        return reverse('virtualization:cluster_list')


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

        return render(request, 'virtualization/virtualmachine.html', {
            'vm': vm,
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

# class VMInterfaceCreateView(PermissionRequiredMixin, ComponentCreateView):
#     permission_required = 'virtualization.add_vminterface'
#     parent_model = VirtualMachine
#     parent_field = 'vm'
#     model = VMInterface
#     form = forms.VMInterfaceCreateForm
#     model_form = forms.VMInterfaceForm
#
#
# class VMInterfaceEditView(PermissionRequiredMixin, ComponentEditView):
#     permission_required = 'virtualization.change_vminterface'
#     model = VMInterface
#     form_class = forms.VMInterfaceForm
#
#
# class VMInterfaceDeleteView(PermissionRequiredMixin, ComponentDeleteView):
#     permission_required = 'virtualization.delete_vminterface'
#     model = VMInterface
#
#
# class VMInterfaceBulkEditView(PermissionRequiredMixin, BulkEditView):
#     permission_required = 'virtualization.change_vminterface'
#     cls = VMInterface
#     parent_cls = VirtualMachine
#     table = tables.VMInterfaceTable
#     form = forms.VMInterfaceBulkEditForm
#
#
# class VMInterfaceBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
#     permission_required = 'virtualization.delete_vminterface'
#     cls = VMInterface
#     parent_cls = VirtualMachine
#     table = tables.VMInterfaceTable
