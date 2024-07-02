import traceback

from django.contrib import messages
from django.db import transaction
from django.db.models import Prefetch, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from jinja2.exceptions import TemplateError

from dcim.filtersets import DeviceFilterSet
from dcim.forms import DeviceFilterForm
from dcim.models import Device
from dcim.tables import DeviceTable
from extras.views import ObjectConfigContextView
from ipam.models import IPAddress
from ipam.tables import InterfaceVLANTable
from netbox.constants import DEFAULT_ACTION_PERMISSIONS
from netbox.views import generic
from tenancy.views import ObjectContactsView
from utilities.query import count_related
from utilities.query_functions import CollateAsChar
from utilities.views import GetRelatedModelsMixin, ViewTab, register_model_view
from . import filtersets, forms, tables
from .models import *


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
class ClusterTypeView(GetRelatedModelsMixin, generic.ObjectView):
    queryset = ClusterType.objects.all()

    def get_extra_context(self, request, instance):
        return {
            'related_models': self.get_related_models(request, instance),
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
class ClusterGroupView(GetRelatedModelsMixin, generic.ObjectView):
    queryset = ClusterGroup.objects.all()

    def get_extra_context(self, request, instance):
        return {
            'related_models': self.get_related_models(request, instance),
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


@register_model_view(ClusterGroup, 'contacts')
class ClusterGroupContactsView(ObjectContactsView):
    queryset = ClusterGroup.objects.all()


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
    filterset_form = forms.VirtualMachineFilterForm
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
    template_name = 'virtualization/cluster/devices.html'
    actions = {
        'add': {'add'},
        'import': {'add'},
        'export': {'view'},
        'bulk_edit': {'change'},
        'bulk_remove_devices': {'change'},
    }
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


@register_model_view(Cluster, 'contacts')
class ClusterContactsView(ObjectContactsView):
    queryset = Cluster.objects.all()


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
    queryset = VirtualMachine.objects.all()


@register_model_view(VirtualMachine, 'interfaces')
class VirtualMachineInterfacesView(generic.ObjectChildrenView):
    queryset = VirtualMachine.objects.all()
    child_model = VMInterface
    table = tables.VirtualMachineVMInterfaceTable
    filterset = filtersets.VMInterfaceFilterSet
    filterset_form = forms.VMInterfaceFilterForm
    template_name = 'virtualization/virtualmachine/interfaces.html'
    actions = {
        **DEFAULT_ACTION_PERMISSIONS,
        'bulk_rename': {'change'},
    }
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
    template_name = 'virtualization/virtualmachine/virtual_disks.html'
    tab = ViewTab(
        label=_('Virtual Disks'),
        badge=lambda obj: obj.virtual_disk_count,
        permission='virtualization.view_virtualdisk',
        weight=500
    )
    actions = {
        **DEFAULT_ACTION_PERMISSIONS,
        'bulk_rename': {'change'},
    }

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
class VirtualMachineRenderConfigView(generic.ObjectView):
    queryset = VirtualMachine.objects.all()
    template_name = 'virtualization/virtualmachine/render_config.html'
    tab = ViewTab(
        label=_('Render Config'),
        weight=2100
    )

    def get(self, request, **kwargs):
        instance = self.get_object(**kwargs)
        context = self.get_extra_context(request, instance)

        # If a direct export has been requested, return the rendered template content as a
        # downloadable file.
        if request.GET.get('export'):
            response = HttpResponse(context['rendered_config'], content_type='text')
            filename = f"{instance.name or 'config'}.txt"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

        return render(request, self.get_template_name(), {
            'object': instance,
            'tab': self.tab,
            **context,
        })

    def get_extra_context(self, request, instance):
        # Compile context data
        context_data = instance.get_config_context()
        context_data.update({'virtualmachine': instance})

        # Render the config template
        rendered_config = None
        if config_template := instance.get_config_template():
            try:
                rendered_config = config_template.render(context=context_data)
            except TemplateError as e:
                messages.error(request, f"An error occurred while rendering the template: {e}")
                rendered_config = traceback.format_exc()

        return {
            'config_template': config_template,
            'context_data': context_data,
            'rendered_config': rendered_config,
        }


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


class VirtualMachineBulkEditView(generic.BulkEditView):
    queryset = VirtualMachine.objects.prefetch_related('primary_ip4', 'primary_ip6')
    filterset = filtersets.VirtualMachineFilterSet
    table = tables.VirtualMachineTable
    form = forms.VirtualMachineBulkEditForm


class VirtualMachineBulkDeleteView(generic.BulkDeleteView):
    queryset = VirtualMachine.objects.prefetch_related('primary_ip4', 'primary_ip6')
    filterset = filtersets.VirtualMachineFilterSet
    table = tables.VirtualMachineTable


@register_model_view(VirtualMachine, 'contacts')
class VirtualMachineContactsView(ObjectContactsView):
    queryset = VirtualMachine.objects.all()


#
# VM interfaces
#

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


class VMInterfaceBulkEditView(generic.BulkEditView):
    queryset = VMInterface.objects.all()
    filterset = filtersets.VMInterfaceFilterSet
    table = tables.VMInterfaceTable
    form = forms.VMInterfaceBulkEditForm


class VMInterfaceBulkRenameView(generic.BulkRenameView):
    queryset = VMInterface.objects.all()
    form = forms.VMInterfaceBulkRenameForm


class VMInterfaceBulkDeleteView(generic.BulkDeleteView):
    # Ensure child interfaces are deleted prior to their parents
    queryset = VMInterface.objects.order_by('virtual_machine', 'parent', CollateAsChar('_name'))
    filterset = filtersets.VMInterfaceFilterSet
    table = tables.VMInterfaceTable


#
# Virtual disks
#

class VirtualDiskListView(generic.ObjectListView):
    queryset = VirtualDisk.objects.all()
    filterset = filtersets.VirtualDiskFilterSet
    filterset_form = forms.VirtualDiskFilterForm
    table = tables.VirtualDiskTable


@register_model_view(VirtualDisk)
class VirtualDiskView(generic.ObjectView):
    queryset = VirtualDisk.objects.all()


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


class VirtualDiskBulkImportView(generic.BulkImportView):
    queryset = VirtualDisk.objects.all()
    model_form = forms.VirtualDiskImportForm


class VirtualDiskBulkEditView(generic.BulkEditView):
    queryset = VirtualDisk.objects.all()
    filterset = filtersets.VirtualDiskFilterSet
    table = tables.VirtualDiskTable
    form = forms.VirtualDiskBulkEditForm


class VirtualDiskBulkRenameView(generic.BulkRenameView):
    queryset = VirtualDisk.objects.all()
    form = forms.VirtualDiskBulkRenameForm


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
        return f'virtualization.add_vminterface'


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
        return f'virtualization.add_virtualdisk'
