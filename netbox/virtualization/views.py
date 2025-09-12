from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db import router, transaction
from django.db.models import Prefetch, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from dcim.filtersets import DeviceFilterSet
from dcim.forms import DeviceFilterForm
from dcim.models import Device
from dcim.tables import DeviceTable
from extras.views import ObjectConfigContextView, ObjectRenderConfigView
from ipam.models import IPAddress, VLANGroup
from ipam.tables import InterfaceVLANTable, VLANTranslationRuleTable
from netbox.object_actions import (
    AddObject, BulkDelete, BulkEdit, BulkExport, BulkImport, BulkRename, DeleteObject, EditObject,
)
from netbox.views import generic
from utilities.query import count_related
from utilities.query_functions import CollateAsChar
from utilities.views import GetRelatedModelsMixin, ViewTab, register_model_view
from . import filtersets, forms, tables
from .models import *
from .object_actions import BulkAddComponents


#
# Cluster types
#

@register_model_view(ClusterType, 'list', path='', detail=False)
class ClusterTypeListView(generic.ObjectListView):
    queryset = ClusterType.objects.annotate(
        cluster_count=count_related(Cluster, 'type')
    )
    filterset = filtersets.ClusterTypeFilterSet
    filterset_form = forms.ClusterTypeFilterForm
    table = tables.ClusterTypeTable


@register_model_view(ClusterType)
class ClusterTypeView(GetRelatedModelsMixin, generic.ObjectView):
    queryset = ClusterType.objects.all()

    def get_extra_context(self, request, instance):
        return {
            'related_models': self.get_related_models(request, instance),
        }


@register_model_view(ClusterType, 'add', detail=False)
@register_model_view(ClusterType, 'edit')
class ClusterTypeEditView(generic.ObjectEditView):
    queryset = ClusterType.objects.all()
    form = forms.ClusterTypeForm


@register_model_view(ClusterType, 'delete')
class ClusterTypeDeleteView(generic.ObjectDeleteView):
    queryset = ClusterType.objects.all()


@register_model_view(ClusterType, 'bulk_import', path='import', detail=False)
class ClusterTypeBulkImportView(generic.BulkImportView):
    queryset = ClusterType.objects.all()
    model_form = forms.ClusterTypeImportForm


@register_model_view(ClusterType, 'bulk_edit', path='edit', detail=False)
class ClusterTypeBulkEditView(generic.BulkEditView):
    queryset = ClusterType.objects.annotate(
        cluster_count=count_related(Cluster, 'type')
    )
    filterset = filtersets.ClusterTypeFilterSet
    table = tables.ClusterTypeTable
    form = forms.ClusterTypeBulkEditForm


@register_model_view(ClusterType, 'bulk_rename', path='rename', detail=False)
class ClusterTypeBulkRenameView(generic.BulkRenameView):
    queryset = ClusterType.objects.all()


@register_model_view(ClusterType, 'bulk_delete', path='delete', detail=False)
class ClusterTypeBulkDeleteView(generic.BulkDeleteView):
    queryset = ClusterType.objects.annotate(
        cluster_count=count_related(Cluster, 'type')
    )
    filterset = filtersets.ClusterTypeFilterSet
    table = tables.ClusterTypeTable


#
# Cluster groups
#

@register_model_view(ClusterGroup, 'list', path='', detail=False)
class ClusterGroupListView(generic.ObjectListView):
    queryset = ClusterGroup.objects.annotate(
        cluster_count=count_related(Cluster, 'group')
    )
    filterset = filtersets.ClusterGroupFilterSet
    filterset_form = forms.ClusterGroupFilterForm
    table = tables.ClusterGroupTable


@register_model_view(ClusterGroup)
class ClusterGroupView(GetRelatedModelsMixin, generic.ObjectView):
    queryset = ClusterGroup.objects.all()

    def get_extra_context(self, request, instance):
        return {
            'related_models': self.get_related_models(
                request,
                instance,
                extra=(
                    (
                    VLANGroup.objects.restrict(request.user, 'view').filter(
                        scope_type=ContentType.objects.get_for_model(ClusterGroup),
                        scope_id=instance.pk
                    ), 'cluster_group'),
                ),
            ),
        }


@register_model_view(ClusterGroup, 'add', detail=False)
@register_model_view(ClusterGroup, 'edit')
class ClusterGroupEditView(generic.ObjectEditView):
    queryset = ClusterGroup.objects.all()
    form = forms.ClusterGroupForm


@register_model_view(ClusterGroup, 'delete')
class ClusterGroupDeleteView(generic.ObjectDeleteView):
    queryset = ClusterGroup.objects.all()


@register_model_view(ClusterGroup, 'bulk_import', path='import', detail=False)
class ClusterGroupBulkImportView(generic.BulkImportView):
    queryset = ClusterGroup.objects.annotate(
        cluster_count=count_related(Cluster, 'group')
    )
    model_form = forms.ClusterGroupImportForm


@register_model_view(ClusterGroup, 'bulk_edit', path='edit', detail=False)
class ClusterGroupBulkEditView(generic.BulkEditView):
    queryset = ClusterGroup.objects.annotate(
        cluster_count=count_related(Cluster, 'group')
    )
    filterset = filtersets.ClusterGroupFilterSet
    table = tables.ClusterGroupTable
    form = forms.ClusterGroupBulkEditForm


@register_model_view(ClusterGroup, 'bulk_rename', path='rename', detail=False)
class ClusterGroupBulkRenameView(generic.BulkRenameView):
    queryset = ClusterGroup.objects.all()


@register_model_view(ClusterGroup, 'bulk_delete', path='delete', detail=False)
class ClusterGroupBulkDeleteView(generic.BulkDeleteView):
    queryset = ClusterGroup.objects.annotate(
        cluster_count=count_related(Cluster, 'group')
    )
    filterset = filtersets.ClusterGroupFilterSet
    table = tables.ClusterGroupTable


#
# Clusters
#

@register_model_view(Cluster, 'list', path='', detail=False)
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
class ClusterView(GetRelatedModelsMixin, generic.ObjectView):
    queryset = Cluster.objects.all()

    def get_extra_context(self, request, instance):
        return {
            **instance.virtual_machines.aggregate(
                vcpus_sum=Sum('vcpus'),
                memory_sum=Sum('memory'),
                disk_sum=Sum('disk')
            ),
            'related_models': self.get_related_models(
                request,
                instance,
                omit=(),
                extra=(
                    (VLANGroup.objects.restrict(request.user, 'view').filter(
                        scope_type=ContentType.objects.get_for_model(Cluster),
                        scope_id=instance.pk
                    ), 'cluster'),
                )
                ),
        }


@register_model_view(Cluster, 'virtualmachines', path='virtual-machines')
class ClusterVirtualMachinesView(generic.ObjectChildrenView):
    queryset = Cluster.objects.all()
    child_model = VirtualMachine
    table = tables.VirtualMachineTable
    filterset = filtersets.VirtualMachineFilterSet
    filterset_form = forms.VirtualMachineFilterForm
    actions = (EditObject, DeleteObject, BulkEdit)
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
    filterset_form = DeviceFilterForm
    actions = (EditObject, DeleteObject, BulkEdit)
    tab = ViewTab(
        label=_('Devices'),
        badge=lambda obj: obj.devices.count(),
        permission='virtualization.view_virtualmachine',
        weight=600
    )

    def get_children(self, request, parent):
        return Device.objects.restrict(request.user, 'view').filter(cluster=parent)


@register_model_view(Cluster, 'add', detail=False)
@register_model_view(Cluster, 'edit')
class ClusterEditView(generic.ObjectEditView):
    queryset = Cluster.objects.all()
    form = forms.ClusterForm


@register_model_view(Cluster, 'delete')
class ClusterDeleteView(generic.ObjectDeleteView):
    queryset = Cluster.objects.all()


@register_model_view(Cluster, 'bulk_import', path='import', detail=False)
class ClusterBulkImportView(generic.BulkImportView):
    queryset = Cluster.objects.all()
    model_form = forms.ClusterImportForm


@register_model_view(Cluster, 'bulk_edit', path='edit', detail=False)
class ClusterBulkEditView(generic.BulkEditView):
    queryset = Cluster.objects.all()
    filterset = filtersets.ClusterFilterSet
    table = tables.ClusterTable
    form = forms.ClusterBulkEditForm


@register_model_view(Cluster, 'bulk_rename', path='rename', detail=False)
class ClusterBulkRenameView(generic.BulkRenameView):
    queryset = Cluster.objects.all()


@register_model_view(Cluster, 'bulk_delete', path='delete', detail=False)
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
            with transaction.atomic(using=router.db_for_write(Device)):

                # Assign the selected Devices to the Cluster
                for device in Device.objects.filter(pk__in=device_pks):
                    device.cluster = cluster
                    device.save()

            messages.success(request, _("Added {count} devices to cluster {cluster}").format(
                count=len(device_pks),
                cluster=cluster
            ))
            return redirect(cluster.get_absolute_url())

        return render(request, self.template_name, {
            'cluster': cluster,
            'form': form,
            'return_url': cluster.get_absolute_url(),
        })


#
# Virtual machines
#

@register_model_view(VirtualMachine, 'list', path='', detail=False)
class VirtualMachineListView(generic.ObjectListView):
    queryset = VirtualMachine.objects.prefetch_related('primary_ip4', 'primary_ip6')
    filterset = filtersets.VirtualMachineFilterSet
    filterset_form = forms.VirtualMachineFilterForm
    table = tables.VirtualMachineTable
    actions = (AddObject, BulkImport, BulkExport, BulkAddComponents, BulkEdit, BulkRename, BulkDelete)


@register_model_view(VirtualMachine)
class VirtualMachineView(generic.ObjectView):
    queryset = VirtualMachine.objects.all()


@register_model_view(VirtualMachine, 'interfaces')
class VirtualMachineInterfacesView(generic.ObjectChildrenView):
    queryset = VirtualMachine.objects.all()
    child_model = VMInterface
    table = tables.VirtualMachineVMInterfaceTable
    filterset = filtersets.VMInterfaceFilterSet
    filterset_form = forms.VMInterfaceFilterForm
    actions = (EditObject, DeleteObject, BulkEdit, BulkRename, BulkDelete)
    tab = ViewTab(
        label=_('Interfaces'),
        badge=lambda obj: obj.interface_count,
        permission='virtualization.view_vminterface',
        weight=500
    )

    def get_children(self, request, parent):
        return parent.interfaces.restrict(request.user, 'view').prefetch_related(
            Prefetch('ip_addresses', queryset=IPAddress.objects.restrict(request.user)),
            'tags',
        )


@register_model_view(VirtualMachine, 'disks')
class VirtualMachineVirtualDisksView(generic.ObjectChildrenView):
    queryset = VirtualMachine.objects.all()
    child_model = VirtualDisk
    table = tables.VirtualMachineVirtualDiskTable
    filterset = filtersets.VirtualDiskFilterSet
    filterset_form = forms.VirtualDiskFilterForm
    actions = (EditObject, DeleteObject, BulkEdit, BulkRename, BulkDelete)
    tab = ViewTab(
        label=_('Virtual Disks'),
        badge=lambda obj: obj.virtual_disk_count,
        permission='virtualization.view_virtualdisk',
        weight=500
    )

    def get_children(self, request, parent):
        return parent.virtualdisks.restrict(request.user, 'view').prefetch_related('tags')


@register_model_view(VirtualMachine, 'configcontext', path='config-context')
class VirtualMachineConfigContextView(ObjectConfigContextView):
    queryset = VirtualMachine.objects.annotate_config_context_data()
    base_template = 'virtualization/virtualmachine.html'
    tab = ViewTab(
        label=_('Config Context'),
        weight=2000
    )


@register_model_view(VirtualMachine, 'render-config')
class VirtualMachineRenderConfigView(ObjectRenderConfigView):
    queryset = VirtualMachine.objects.all()
    base_template = 'virtualization/virtualmachine/base.html'
    tab = ViewTab(
        label=_('Render Config'),
        weight=2100,
    )


@register_model_view(VirtualMachine, 'add', detail=False)
@register_model_view(VirtualMachine, 'edit')
class VirtualMachineEditView(generic.ObjectEditView):
    queryset = VirtualMachine.objects.all()
    form = forms.VirtualMachineForm


@register_model_view(VirtualMachine, 'delete')
class VirtualMachineDeleteView(generic.ObjectDeleteView):
    queryset = VirtualMachine.objects.all()


@register_model_view(VirtualMachine, 'bulk_import', path='import', detail=False)
class VirtualMachineBulkImportView(generic.BulkImportView):
    queryset = VirtualMachine.objects.all()
    model_form = forms.VirtualMachineImportForm


@register_model_view(VirtualMachine, 'bulk_edit', path='edit', detail=False)
class VirtualMachineBulkEditView(generic.BulkEditView):
    queryset = VirtualMachine.objects.prefetch_related('primary_ip4', 'primary_ip6')
    filterset = filtersets.VirtualMachineFilterSet
    table = tables.VirtualMachineTable
    form = forms.VirtualMachineBulkEditForm


@register_model_view(VirtualMachine, 'bulk_rename', path='rename', detail=False)
class VirtualMachineBulkRenameView(generic.BulkRenameView):
    queryset = VirtualMachine.objects.all()


@register_model_view(VirtualMachine, 'bulk_delete', path='delete', detail=False)
class VirtualMachineBulkDeleteView(generic.BulkDeleteView):
    queryset = VirtualMachine.objects.prefetch_related('primary_ip4', 'primary_ip6')
    filterset = filtersets.VirtualMachineFilterSet
    table = tables.VirtualMachineTable


#
# VM interfaces
#

@register_model_view(VMInterface, 'list', path='', detail=False)
class VMInterfaceListView(generic.ObjectListView):
    queryset = VMInterface.objects.all()
    filterset = filtersets.VMInterfaceFilterSet
    filterset_form = forms.VMInterfaceFilterForm
    table = tables.VMInterfaceTable


@register_model_view(VMInterface)
class VMInterfaceView(generic.ObjectView):
    queryset = VMInterface.objects.all()

    def get_extra_context(self, request, instance):

        # Get child interfaces
        child_interfaces = VMInterface.objects.restrict(request.user, 'view').filter(parent=instance)
        child_interfaces_tables = tables.VMInterfaceTable(
            child_interfaces,
            exclude=('virtual_machine',),
            orderable=False
        )
        child_interfaces_tables.configure(request)

        # Get VLAN translation rules
        vlan_translation_table = None
        if instance.vlan_translation_policy:
            vlan_translation_table = VLANTranslationRuleTable(
                data=instance.vlan_translation_policy.rules.all(),
                orderable=False
            )
            vlan_translation_table.configure(request)

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
        vlan_table.configure(request)

        return {
            'child_interfaces_table': child_interfaces_tables,
            'vlan_table': vlan_table,
            'vlan_translation_table': vlan_translation_table,
        }


@register_model_view(VMInterface, 'add', detail=False)
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


@register_model_view(VMInterface, 'bulk_import', path='import', detail=False)
class VMInterfaceBulkImportView(generic.BulkImportView):
    queryset = VMInterface.objects.all()
    model_form = forms.VMInterfaceImportForm


@register_model_view(VMInterface, 'bulk_edit', path='edit', detail=False)
class VMInterfaceBulkEditView(generic.BulkEditView):
    queryset = VMInterface.objects.all()
    filterset = filtersets.VMInterfaceFilterSet
    table = tables.VMInterfaceTable
    form = forms.VMInterfaceBulkEditForm


@register_model_view(VMInterface, 'bulk_rename', path='rename', detail=False)
class VMInterfaceBulkRenameView(generic.BulkRenameView):
    queryset = VMInterface.objects.all()
    form = forms.VMInterfaceBulkRenameForm


@register_model_view(VMInterface, 'bulk_delete', path='delete', detail=False)
class VMInterfaceBulkDeleteView(generic.BulkDeleteView):
    # Ensure child interfaces are deleted prior to their parents
    queryset = VMInterface.objects.order_by('virtual_machine', 'parent', CollateAsChar('_name'))
    filterset = filtersets.VMInterfaceFilterSet
    table = tables.VMInterfaceTable


#
# Virtual disks
#

@register_model_view(VirtualDisk, 'list', path='', detail=False)
class VirtualDiskListView(generic.ObjectListView):
    queryset = VirtualDisk.objects.all()
    filterset = filtersets.VirtualDiskFilterSet
    filterset_form = forms.VirtualDiskFilterForm
    table = tables.VirtualDiskTable


@register_model_view(VirtualDisk)
class VirtualDiskView(generic.ObjectView):
    queryset = VirtualDisk.objects.all()


@register_model_view(VirtualDisk, 'add', detail=False)
class VirtualDiskCreateView(generic.ComponentCreateView):
    queryset = VirtualDisk.objects.all()
    form = forms.VirtualDiskCreateForm
    model_form = forms.VirtualDiskForm


@register_model_view(VirtualDisk, 'edit')
class VirtualDiskEditView(generic.ObjectEditView):
    queryset = VirtualDisk.objects.all()
    form = forms.VirtualDiskForm


@register_model_view(VirtualDisk, 'delete')
class VirtualDiskDeleteView(generic.ObjectDeleteView):
    queryset = VirtualDisk.objects.all()


@register_model_view(VirtualDisk, 'bulk_import', path='import', detail=False)
class VirtualDiskBulkImportView(generic.BulkImportView):
    queryset = VirtualDisk.objects.all()
    model_form = forms.VirtualDiskImportForm


@register_model_view(VirtualDisk, 'bulk_edit', path='edit', detail=False)
class VirtualDiskBulkEditView(generic.BulkEditView):
    queryset = VirtualDisk.objects.all()
    filterset = filtersets.VirtualDiskFilterSet
    table = tables.VirtualDiskTable
    form = forms.VirtualDiskBulkEditForm


@register_model_view(VirtualDisk, 'bulk_rename', path='rename', detail=False)
class VirtualDiskBulkRenameView(generic.BulkRenameView):
    queryset = VirtualDisk.objects.all()
    form = forms.VirtualDiskBulkRenameForm


@register_model_view(VirtualDisk, 'bulk_delete', path='delete', detail=False)
class VirtualDiskBulkDeleteView(generic.BulkDeleteView):
    queryset = VirtualDisk.objects.all()
    filterset = filtersets.VirtualDiskFilterSet
    table = tables.VirtualDiskTable


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
        return 'virtualization.add_vminterface'


class VirtualMachineBulkAddVirtualDiskView(generic.BulkComponentCreateView):
    parent_model = VirtualMachine
    parent_field = 'virtual_machine'
    form = forms.VirtualDiskBulkCreateForm
    queryset = VirtualDisk.objects.all()
    model_form = forms.VirtualDiskForm
    filterset = filtersets.VirtualMachineFilterSet
    table = tables.VirtualMachineTable
    default_return_url = 'virtualization:virtualmachine_list'

    def get_required_permission(self):
        return 'virtualization.add_virtualdisk'
