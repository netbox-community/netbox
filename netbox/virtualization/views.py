from django.contrib import messages
from django.db import transaction
from django.db.models import Prefetch, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _

from dcim.filtersets import DeviceFilterSet
from dcim.models import Device
from dcim.tables import DeviceTable
from extras.views import ObjectConfigContextView
from ipam.models import IPAddress, Service
from ipam.tables import AssignedIPAddressesTable, InterfaceVLANTable
from netbox.views import generic
from utilities.utils import count_related
from utilities.views import ViewTab, register_model_view
from . import filtersets, forms, tables
from .models import Cluster, ClusterGroup, ClusterType, VirtualMachine, VMInterface


#
# Cluster types
#

class ClusterTypeListView(generic.ObjectListView):
    queryset = ClusterType.objects.annotate(
        cluster_count=count_related(Cluster, 'type')
    )
    filterset = filtersets.ClusterTypeFilterSet
    filterset_form = forms.ClusterTypeFilterForm
    table = tables.ClusterTypeTable


@register_model_view(ClusterType)
class ClusterTypeView(generic.ObjectView):
    queryset = ClusterType.objects.all()

    def get_extra_context(self, request, instance):
        clusters = Cluster.objects.restrict(request.user, 'view').filter(
            type=instance
        ).annotate(
            device_count=count_related(Device, 'cluster'),
            vm_count=count_related(VirtualMachine, 'cluster')
        )
        clusters_table = tables.ClusterTable(clusters, user=request.user, exclude=('type',))
        clusters_table.configure(request)

        return {
            'clusters_table': clusters_table,
        }


@register_model_view(ClusterType, 'edit')
class ClusterTypeEditView(generic.ObjectEditView):
    queryset = ClusterType.objects.all()
    form = forms.ClusterTypeForm


@register_model_view(ClusterType, 'delete')
class ClusterTypeDeleteView(generic.ObjectDeleteView):
    queryset = ClusterType.objects.all()


class ClusterTypeBulkImportView(generic.BulkImportView):
    queryset = ClusterType.objects.all()
    model_form = forms.ClusterTypeImportForm
    table = tables.ClusterTypeTable


class ClusterTypeBulkEditView(generic.BulkEditView):
    queryset = ClusterType.objects.annotate(
        cluster_count=count_related(Cluster, 'type')
    )
    filterset = filtersets.ClusterTypeFilterSet
    table = tables.ClusterTypeTable
    form = forms.ClusterTypeBulkEditForm


class ClusterTypeBulkDeleteView(generic.BulkDeleteView):
    queryset = ClusterType.objects.annotate(
        cluster_count=count_related(Cluster, 'type')
    )
    filterset = filtersets.ClusterTypeFilterSet
    table = tables.ClusterTypeTable


#
# Cluster groups
#

class ClusterGroupListView(generic.ObjectListView):
    queryset = ClusterGroup.objects.annotate(
        cluster_count=count_related(Cluster, 'group')
    )
    filterset = filtersets.ClusterGroupFilterSet
    filterset_form = forms.ClusterGroupFilterForm
    table = tables.ClusterGroupTable


@register_model_view(ClusterGroup)
class ClusterGroupView(generic.ObjectView):
    queryset = ClusterGroup.objects.all()

    def get_extra_context(self, request, instance):
        clusters = Cluster.objects.restrict(request.user, 'view').filter(
            group=instance
        ).annotate(
            device_count=count_related(Device, 'cluster'),
            vm_count=count_related(VirtualMachine, 'cluster')
        )
        clusters_table = tables.ClusterTable(clusters, user=request.user, exclude=('group',))
        clusters_table.configure(request)

        return {
            'clusters_table': clusters_table,
        }


@register_model_view(ClusterGroup, 'edit')
class ClusterGroupEditView(generic.ObjectEditView):
    queryset = ClusterGroup.objects.all()
    form = forms.ClusterGroupForm


@register_model_view(ClusterGroup, 'delete')
class ClusterGroupDeleteView(generic.ObjectDeleteView):
    queryset = ClusterGroup.objects.all()


class ClusterGroupBulkImportView(generic.BulkImportView):
    queryset = ClusterGroup.objects.annotate(
        cluster_count=count_related(Cluster, 'group')
    )
    model_form = forms.ClusterGroupImportForm
    table = tables.ClusterGroupTable


class ClusterGroupBulkEditView(generic.BulkEditView):
    queryset = ClusterGroup.objects.annotate(
        cluster_count=count_related(Cluster, 'group')
    )
    filterset = filtersets.ClusterGroupFilterSet
    table = tables.ClusterGroupTable
    form = forms.ClusterGroupBulkEditForm


class ClusterGroupBulkDeleteView(generic.BulkDeleteView):
    queryset = ClusterGroup.objects.annotate(
        cluster_count=count_related(Cluster, 'group')
    )
    filterset = filtersets.ClusterGroupFilterSet
    table = tables.ClusterGroupTable


#
# Clusters
#

class ClusterListView(generic.ObjectListView):
    permission_required = 'virtualization.view_cluster'
    queryset = Cluster.objects.annotate(
        device_count=count_related(Device, 'cluster'),
        vm_count=count_related(VirtualMachine, 'cluster')
    )
    table = tables.ClusterTable
    filterset = filtersets.ClusterFilterSet
    filterset_form = forms.ClusterFilterForm


@register_model_view(Cluster)
class ClusterView(generic.ObjectView):
    queryset = Cluster.objects.all()

    def get_extra_context(self, request, instance):
        return instance.virtual_machines.aggregate(vcpus_sum=Sum('vcpus'), memory_sum=Sum('memory'), disk_sum=Sum('disk'))


@register_model_view(Cluster, 'virtualmachines', path='virtual-machines')
class ClusterVirtualMachinesView(generic.ObjectChildrenView):
    queryset = Cluster.objects.all()
    child_model = VirtualMachine
    table = tables.VirtualMachineTable
    filterset = filtersets.VirtualMachineFilterSet
    template_name = 'virtualization/cluster/virtual_machines.html'
    tab = ViewTab(
        label=_('Virtual Machines'),
        badge=lambda obj: obj.virtual_machines.count(),
        permission='virtualization.view_virtualmachine',
        weight=500
    )

    def get_children(self, request, parent):
        return VirtualMachine.objects.restrict(request.user, 'view').filter(cluster=parent)


@register_model_view(Cluster, 'devices')
class ClusterDevicesView(generic.ObjectChildrenView):
    queryset = Cluster.objects.all()
    child_model = Device
    table = DeviceTable
    filterset = DeviceFilterSet
    template_name = 'virtualization/cluster/devices.html'
    tab = ViewTab(
        label=_('Devices'),
        badge=lambda obj: obj.devices.count(),
        permission='virtualization.view_virtualmachine',
        weight=600
    )

    def get_children(self, request, parent):
        return Device.objects.restrict(request.user, 'view').filter(cluster=parent)


@register_model_view(Cluster, 'edit')
class ClusterEditView(generic.ObjectEditView):
    queryset = Cluster.objects.all()
    form = forms.ClusterForm


@register_model_view(Cluster, 'delete')
class ClusterDeleteView(generic.ObjectDeleteView):
    queryset = Cluster.objects.all()


class ClusterBulkImportView(generic.BulkImportView):
    queryset = Cluster.objects.all()
    model_form = forms.ClusterImportForm
    table = tables.ClusterTable


class ClusterBulkEditView(generic.BulkEditView):
    queryset = Cluster.objects.all()
    filterset = filtersets.ClusterFilterSet
    table = tables.ClusterTable
    form = forms.ClusterBulkEditForm


class ClusterBulkDeleteView(generic.BulkDeleteView):
    queryset = Cluster.objects.all()
    filterset = filtersets.ClusterFilterSet
    table = tables.ClusterTable


@register_model_view(Cluster, 'add_devices', path='devices/add')
class ClusterAddDevicesView(generic.ObjectEditView):
    queryset = Cluster.objects.all()
    form = forms.ClusterAddDevicesForm
    template_name = 'virtualization/cluster_add_devices.html'

    def get(self, request, pk):
        cluster = get_object_or_404(self.queryset, pk=pk)
        form = self.form(cluster, initial=request.GET)

        return render(request, self.template_name, {
            'cluster': cluster,
            'form': form,
            'return_url': reverse('virtualization:cluster', kwargs={'pk': pk}),
        })

    def post(self, request, pk):
        cluster = get_object_or_404(self.queryset, pk=pk)
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


@register_model_view(Cluster, 'remove_devices', path='devices/remove')
class ClusterRemoveDevicesView(generic.ObjectEditView):
    queryset = Cluster.objects.all()
    form = forms.ClusterRemoveDevicesForm
    template_name = 'generic/bulk_remove.html'

    def post(self, request, pk):

        cluster = get_object_or_404(self.queryset, pk=pk)

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

class VirtualMachineListView(generic.ObjectListView):
    queryset = VirtualMachine.objects.prefetch_related('primary_ip4', 'primary_ip6')
    filterset = filtersets.VirtualMachineFilterSet
    filterset_form = forms.VirtualMachineFilterForm
    table = tables.VirtualMachineTable
    template_name = 'virtualization/virtualmachine_list.html'


@register_model_view(VirtualMachine)
class VirtualMachineView(generic.ObjectView):
    queryset = VirtualMachine.objects.prefetch_related('tenant__group')

    def get_extra_context(self, request, instance):
        # Interfaces
        vminterfaces = VMInterface.objects.restrict(request.user, 'view').filter(
            virtual_machine=instance
        ).prefetch_related(
            Prefetch('ip_addresses', queryset=IPAddress.objects.restrict(request.user))
        )
        vminterface_table = tables.VirtualMachineVMInterfaceTable(vminterfaces, user=request.user, orderable=False)
        if request.user.has_perm('virtualization.change_vminterface') or \
                request.user.has_perm('virtualization.delete_vminterface'):
            vminterface_table.columns.show('pk')

        # Services
        services = Service.objects.restrict(request.user, 'view').filter(
            virtual_machine=instance
        ).prefetch_related(
            Prefetch('ipaddresses', queryset=IPAddress.objects.restrict(request.user)),
            'virtual_machine'
        )

        return {
            'vminterface_table': vminterface_table,
            'services': services,
        }


@register_model_view(VirtualMachine, 'interfaces')
class VirtualMachineInterfacesView(generic.ObjectChildrenView):
    queryset = VirtualMachine.objects.all()
    child_model = VMInterface
    table = tables.VirtualMachineVMInterfaceTable
    filterset = filtersets.VMInterfaceFilterSet
    template_name = 'virtualization/virtualmachine/interfaces.html'
    tab = ViewTab(
        label=_('Interfaces'),
        badge=lambda obj: obj.interfaces.count(),
        permission='virtualization.view_vminterface',
        weight=500
    )

    def get_children(self, request, parent):
        return parent.interfaces.restrict(request.user, 'view').prefetch_related(
            Prefetch('ip_addresses', queryset=IPAddress.objects.restrict(request.user)),
            'tags',
        )


@register_model_view(VirtualMachine, 'configcontext', path='config-context')
class VirtualMachineConfigContextView(ObjectConfigContextView):
    queryset = VirtualMachine.objects.annotate_config_context_data()
    base_template = 'virtualization/virtualmachine.html'
    tab = ViewTab(
        label=_('Config Context'),
        permission='extras.view_configcontext',
        weight=2000
    )


@register_model_view(VirtualMachine, 'edit')
class VirtualMachineEditView(generic.ObjectEditView):
    queryset = VirtualMachine.objects.all()
    form = forms.VirtualMachineForm


@register_model_view(VirtualMachine, 'delete')
class VirtualMachineDeleteView(generic.ObjectDeleteView):
    queryset = VirtualMachine.objects.all()


class VirtualMachineBulkImportView(generic.BulkImportView):
    queryset = VirtualMachine.objects.all()
    model_form = forms.VirtualMachineImportForm
    table = tables.VirtualMachineTable


class VirtualMachineBulkEditView(generic.BulkEditView):
    queryset = VirtualMachine.objects.prefetch_related('primary_ip4', 'primary_ip6')
    filterset = filtersets.VirtualMachineFilterSet
    table = tables.VirtualMachineTable
    form = forms.VirtualMachineBulkEditForm


class VirtualMachineBulkDeleteView(generic.BulkDeleteView):
    queryset = VirtualMachine.objects.prefetch_related('primary_ip4', 'primary_ip6')
    filterset = filtersets.VirtualMachineFilterSet
    table = tables.VirtualMachineTable


#
# VM interfaces
#

class VMInterfaceListView(generic.ObjectListView):
    queryset = VMInterface.objects.all()
    filterset = filtersets.VMInterfaceFilterSet
    filterset_form = forms.VMInterfaceFilterForm
    table = tables.VMInterfaceTable
    actions = ('import', 'export', 'bulk_edit', 'bulk_delete')


@register_model_view(VMInterface)
class VMInterfaceView(generic.ObjectView):
    queryset = VMInterface.objects.all()

    def get_extra_context(self, request, instance):
        # Get assigned IP addresses
        ipaddress_table = AssignedIPAddressesTable(
            data=instance.ip_addresses.restrict(request.user, 'view'),
            orderable=False
        )

        # Get child interfaces
        child_interfaces = VMInterface.objects.restrict(request.user, 'view').filter(parent=instance)
        child_interfaces_tables = tables.VMInterfaceTable(
            child_interfaces,
            exclude=('virtual_machine',),
            orderable=False
        )

        # Get assigned VLANs and annotate whether each is tagged or untagged
        vlans = []
        if instance.untagged_vlan is not None:
            vlans.append(instance.untagged_vlan)
            vlans[0].tagged = False
        for vlan in instance.tagged_vlans.restrict(request.user).prefetch_related('site', 'group', 'tenant', 'role'):
            vlan.tagged = True
            vlans.append(vlan)
        vlan_table = InterfaceVLANTable(
            interface=instance,
            data=vlans,
            orderable=False
        )

        return {
            'ipaddress_table': ipaddress_table,
            'child_interfaces_table': child_interfaces_tables,
            'vlan_table': vlan_table,
        }


class VMInterfaceCreateView(generic.ComponentCreateView):
    queryset = VMInterface.objects.all()
    form = forms.VMInterfaceCreateForm
    model_form = forms.VMInterfaceForm


@register_model_view(VMInterface, 'edit')
class VMInterfaceEditView(generic.ObjectEditView):
    queryset = VMInterface.objects.all()
    form = forms.VMInterfaceForm


@register_model_view(VMInterface, 'delete')
class VMInterfaceDeleteView(generic.ObjectDeleteView):
    queryset = VMInterface.objects.all()


class VMInterfaceBulkImportView(generic.BulkImportView):
    queryset = VMInterface.objects.all()
    model_form = forms.VMInterfaceImportForm
    table = tables.VMInterfaceTable


class VMInterfaceBulkEditView(generic.BulkEditView):
    queryset = VMInterface.objects.all()
    filterset = filtersets.VMInterfaceFilterSet
    table = tables.VMInterfaceTable
    form = forms.VMInterfaceBulkEditForm


class VMInterfaceBulkRenameView(generic.BulkRenameView):
    queryset = VMInterface.objects.all()
    form = forms.VMInterfaceBulkRenameForm


class VMInterfaceBulkDeleteView(generic.BulkDeleteView):
    queryset = VMInterface.objects.all()
    filterset = filtersets.VMInterfaceFilterSet
    table = tables.VMInterfaceTable


#
# Bulk Device component creation
#

class VirtualMachineBulkAddInterfaceView(generic.BulkComponentCreateView):
    parent_model = VirtualMachine
    parent_field = 'virtual_machine'
    form = forms.VMInterfaceBulkCreateForm
    queryset = VMInterface.objects.all()
    model_form = forms.VMInterfaceForm
    filterset = filtersets.VirtualMachineFilterSet
    table = tables.VirtualMachineTable
    default_return_url = 'virtualization:virtualmachine_list'

    def get_required_permission(self):
        return f'virtualization.add_vminterface'
