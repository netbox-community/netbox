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
    BulkComponentCreateView, BulkDeleteView, BulkEditView, BulkImportView, ComponentCreateView, ObjectView,
    ObjectDeleteView, ObjectEditView, ObjectListView,
)
from . import filters, forms, tables
from .models import Cluster, ClusterGroup, ClusterType, VirtualMachine


#
# Cluster types
#

class ClusterTypeListView(ObjectListView):
    queryset = ClusterType.objects.annotate(cluster_count=Count('clusters'))
    table = tables.ClusterTypeTable


class ClusterTypeEditView(ObjectEditView):
    queryset = ClusterType.objects.all()
    model_form = forms.ClusterTypeForm
    default_return_url = 'virtualization:clustertype_list'


class ClusterTypeBulkImportView(BulkImportView):
    queryset = ClusterType.objects.all()
    model_form = forms.ClusterTypeCSVForm
    table = tables.ClusterTypeTable
    default_return_url = 'virtualization:clustertype_list'


class ClusterTypeBulkDeleteView(BulkDeleteView):
    queryset = ClusterType.objects.annotate(cluster_count=Count('clusters'))
    table = tables.ClusterTypeTable
    default_return_url = 'virtualization:clustertype_list'


#
# Cluster groups
#

class ClusterGroupListView(ObjectListView):
    queryset = ClusterGroup.objects.annotate(cluster_count=Count('clusters'))
    table = tables.ClusterGroupTable


class ClusterGroupEditView(ObjectEditView):
    queryset = ClusterGroup.objects.all()
    model_form = forms.ClusterGroupForm
    default_return_url = 'virtualization:clustergroup_list'


class ClusterGroupBulkImportView(BulkImportView):
    queryset = ClusterGroup.objects.all()
    model_form = forms.ClusterGroupCSVForm
    table = tables.ClusterGroupTable
    default_return_url = 'virtualization:clustergroup_list'


class ClusterGroupBulkDeleteView(BulkDeleteView):
    queryset = ClusterGroup.objects.annotate(cluster_count=Count('clusters'))
    table = tables.ClusterGroupTable
    default_return_url = 'virtualization:clustergroup_list'


#
# Clusters
#

class ClusterListView(ObjectListView):
    queryset = Cluster.objects.prefetch_related('type', 'group', 'site', 'tenant')
    table = tables.ClusterTable
    filterset = filters.ClusterFilterSet
    filterset_form = forms.ClusterFilterForm


class ClusterView(ObjectView):
    queryset = Cluster.objects.all()

    def get(self, request, pk):

        cluster = get_object_or_404(self.queryset, pk=pk)
        devices = Device.objects.filter(cluster=cluster).prefetch_related(
            'site', 'rack', 'tenant', 'device_type__manufacturer'
        )
        device_table = DeviceTable(list(devices), orderable=False)
        if request.user.has_perm('virtualization.change_cluster'):
            device_table.columns.show('pk')

        return render(request, 'virtualization/cluster.html', {
            'cluster': cluster,
            'device_table': device_table,
        })


class ClusterEditView(ObjectEditView):
    template_name = 'virtualization/cluster_edit.html'
    queryset = Cluster.objects.all()
    model_form = forms.ClusterForm


class ClusterDeleteView(ObjectDeleteView):
    queryset = Cluster.objects.all()
    default_return_url = 'virtualization:cluster_list'


class ClusterBulkImportView(BulkImportView):
    queryset = Cluster.objects.all()
    model_form = forms.ClusterCSVForm
    table = tables.ClusterTable
    default_return_url = 'virtualization:cluster_list'


class ClusterBulkEditView(BulkEditView):
    queryset = Cluster.objects.prefetch_related('type', 'group', 'site')
    filterset = filters.ClusterFilterSet
    table = tables.ClusterTable
    form = forms.ClusterBulkEditForm
    default_return_url = 'virtualization:cluster_list'


class ClusterBulkDeleteView(BulkDeleteView):
    queryset = Cluster.objects.prefetch_related('type', 'group', 'site')
    filterset = filters.ClusterFilterSet
    table = tables.ClusterTable
    default_return_url = 'virtualization:cluster_list'


class ClusterAddDevicesView(PermissionRequiredMixin, View):
    permission_required = 'virtualization.change_cluster'
    form = forms.ClusterAddDevicesForm
    template_name = 'virtualization/cluster_add_devices.html'

    def get(self, request, pk):

        cluster = get_object_or_404(Cluster, pk=pk)
        form = self.form(cluster, initial=request.GET)

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
    queryset = VirtualMachine.objects.prefetch_related('cluster', 'tenant', 'role', 'primary_ip4', 'primary_ip6')
    filterset = filters.VirtualMachineFilterSet
    filterset_form = forms.VirtualMachineFilterForm
    table = tables.VirtualMachineDetailTable
    template_name = 'virtualization/virtualmachine_list.html'


class VirtualMachineView(ObjectView):
    queryset = VirtualMachine.objects.prefetch_related('tenant__group')

    def get(self, request, pk):

        virtualmachine = get_object_or_404(self.queryset, pk=pk)
        interfaces = Interface.objects.filter(virtual_machine=virtualmachine)
        services = Service.objects.filter(virtual_machine=virtualmachine)

        return render(request, 'virtualization/virtualmachine.html', {
            'virtualmachine': virtualmachine,
            'interfaces': interfaces,
            'services': services,
        })


class VirtualMachineConfigContextView(PermissionRequiredMixin, ObjectConfigContextView):
    permission_required = 'virtualization.view_virtualmachine'
    object_class = VirtualMachine
    base_template = 'virtualization/virtualmachine.html'


class VirtualMachineEditView(ObjectEditView):
    queryset = VirtualMachine.objects.all()
    model_form = forms.VirtualMachineForm
    template_name = 'virtualization/virtualmachine_edit.html'
    default_return_url = 'virtualization:virtualmachine_list'


class VirtualMachineDeleteView(ObjectDeleteView):
    queryset = VirtualMachine.objects.all()
    default_return_url = 'virtualization:virtualmachine_list'


class VirtualMachineBulkImportView(BulkImportView):
    queryset = VirtualMachine.objects.all()
    model_form = forms.VirtualMachineCSVForm
    table = tables.VirtualMachineTable
    default_return_url = 'virtualization:virtualmachine_list'


class VirtualMachineBulkEditView(BulkEditView):
    queryset = VirtualMachine.objects.prefetch_related('cluster', 'tenant', 'role')
    filterset = filters.VirtualMachineFilterSet
    table = tables.VirtualMachineTable
    form = forms.VirtualMachineBulkEditForm
    default_return_url = 'virtualization:virtualmachine_list'


class VirtualMachineBulkDeleteView(BulkDeleteView):
    queryset = VirtualMachine.objects.prefetch_related('cluster', 'tenant', 'role')
    filterset = filters.VirtualMachineFilterSet
    table = tables.VirtualMachineTable
    default_return_url = 'virtualization:virtualmachine_list'


#
# VM interfaces
#

class InterfaceCreateView(ComponentCreateView):
    queryset = Interface.objects.all()
    form = forms.InterfaceCreateForm
    model_form = forms.InterfaceForm
    template_name = 'virtualization/virtualmachine_component_add.html'


class InterfaceEditView(ObjectEditView):
    queryset = Interface.objects.all()
    model_form = forms.InterfaceForm
    template_name = 'virtualization/interface_edit.html'


class InterfaceDeleteView(ObjectDeleteView):
    queryset = Interface.objects.all()


class InterfaceBulkEditView(BulkEditView):
    queryset = Interface.objects.all()
    table = tables.InterfaceTable
    form = forms.InterfaceBulkEditForm


class InterfaceBulkDeleteView(BulkDeleteView):
    queryset = Interface.objects.all()
    table = tables.InterfaceTable


#
# Bulk Device component creation
#

class VirtualMachineBulkAddInterfaceView(PermissionRequiredMixin, BulkComponentCreateView):
    permission_required = 'dcim.add_interface'
    parent_model = VirtualMachine
    parent_field = 'virtual_machine'
    form = forms.InterfaceBulkCreateForm
    model = Interface
    model_form = forms.InterfaceForm
    filterset = filters.VirtualMachineFilterSet
    table = tables.VirtualMachineTable
    default_return_url = 'virtualization:virtualmachine_list'
