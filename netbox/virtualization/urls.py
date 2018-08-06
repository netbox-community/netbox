from __future__ import unicode_literals

from django.conf.urls import url

from extras.views import ObjectChangeLogView
from ipam.views import ServiceCreateView
from . import views
from .models import Cluster, ClusterGroup, ClusterType, VirtualMachine

app_name = 'virtualization'
urlpatterns = [

    # Cluster types
    url(r'^cluster-types/$', views.ClusterTypeListView.as_view(), name='clustertype_list'),
    url(r'^cluster-types/add/$', views.ClusterTypeCreateView.as_view(), name='clustertype_add'),
    url(r'^cluster-types/import/$', views.ClusterTypeBulkImportView.as_view(), name='clustertype_import'),
    url(r'^cluster-types/delete/$', views.ClusterTypeBulkDeleteView.as_view(), name='clustertype_bulk_delete'),
    url(r'^cluster-types/(?P<slug>[\w-]+)/edit/$', views.ClusterTypeEditView.as_view(), name='clustertype_edit'),
    url(r'^cluster-types/(?P<slug>[\w-]+)/changelog/$', ObjectChangeLogView.as_view(), name='clustertype_changelog', kwargs={'model': ClusterType}),

    # Cluster groups
    url(r'^cluster-groups/$', views.ClusterGroupListView.as_view(), name='clustergroup_list'),
    url(r'^cluster-groups/add/$', views.ClusterGroupCreateView.as_view(), name='clustergroup_add'),
    url(r'^cluster-groups/import/$', views.ClusterGroupBulkImportView.as_view(), name='clustergroup_import'),
    url(r'^cluster-groups/delete/$', views.ClusterGroupBulkDeleteView.as_view(), name='clustergroup_bulk_delete'),
    url(r'^cluster-groups/(?P<slug>[\w-]+)/edit/$', views.ClusterGroupEditView.as_view(), name='clustergroup_edit'),
    url(r'^cluster-groups/(?P<slug>[\w-]+)/changelog/$', ObjectChangeLogView.as_view(), name='clustergroup_changelog', kwargs={'model': ClusterGroup}),

    # Clusters
    url(r'^clusters/$', views.ClusterListView.as_view(), name='cluster_list'),
    url(r'^clusters/add/$', views.ClusterCreateView.as_view(), name='cluster_add'),
    url(r'^clusters/import/$', views.ClusterBulkImportView.as_view(), name='cluster_import'),
    url(r'^clusters/edit/$', views.ClusterBulkEditView.as_view(), name='cluster_bulk_edit'),
    url(r'^clusters/delete/$', views.ClusterBulkDeleteView.as_view(), name='cluster_bulk_delete'),
    url(r'^clusters/(?P<pk>\d+)/$', views.ClusterView.as_view(), name='cluster'),
    url(r'^clusters/(?P<pk>\d+)/edit/$', views.ClusterEditView.as_view(), name='cluster_edit'),
    url(r'^clusters/(?P<pk>\d+)/delete/$', views.ClusterDeleteView.as_view(), name='cluster_delete'),
    url(r'^clusters/(?P<pk>\d+)/changelog/$', ObjectChangeLogView.as_view(), name='cluster_changelog', kwargs={'model': Cluster}),
    url(r'^clusters/(?P<pk>\d+)/devices/add/$', views.ClusterAddDevicesView.as_view(), name='cluster_add_devices'),
    url(r'^clusters/(?P<pk>\d+)/devices/remove/$', views.ClusterRemoveDevicesView.as_view(), name='cluster_remove_devices'),

    # Virtual machines
    url(r'^virtual-machines/$', views.VirtualMachineListView.as_view(), name='virtualmachine_list'),
    url(r'^virtual-machines/add/$', views.VirtualMachineCreateView.as_view(), name='virtualmachine_add'),
    url(r'^virtual-machines/import/$', views.VirtualMachineBulkImportView.as_view(), name='virtualmachine_import'),
    url(r'^virtual-machines/edit/$', views.VirtualMachineBulkEditView.as_view(), name='virtualmachine_bulk_edit'),
    url(r'^virtual-machines/delete/$', views.VirtualMachineBulkDeleteView.as_view(), name='virtualmachine_bulk_delete'),
    url(r'^virtual-machines/(?P<pk>\d+)/$', views.VirtualMachineView.as_view(), name='virtualmachine'),
    url(r'^virtual-machines/(?P<pk>\d+)/edit/$', views.VirtualMachineEditView.as_view(), name='virtualmachine_edit'),
    url(r'^virtual-machines/(?P<pk>\d+)/delete/$', views.VirtualMachineDeleteView.as_view(), name='virtualmachine_delete'),
    url(r'^virtual-machines/(?P<pk>\d+)/config-context/$', views.VirtualMachineConfigContextView.as_view(), name='virtualmachine_configcontext'),
    url(r'^virtual-machines/(?P<pk>\d+)/changelog/$', ObjectChangeLogView.as_view(), name='virtualmachine_changelog', kwargs={'model': VirtualMachine}),
    url(r'^virtual-machines/(?P<virtualmachine>\d+)/services/assign/$', ServiceCreateView.as_view(), name='virtualmachine_service_assign'),

    # VM interfaces
    url(r'^virtual-machines/interfaces/add/$', views.VirtualMachineBulkAddInterfaceView.as_view(), name='virtualmachine_bulk_add_interface'),
    url(r'^virtual-machines/(?P<pk>\d+)/interfaces/add/$', views.InterfaceCreateView.as_view(), name='interface_add'),
    url(r'^virtual-machines/(?P<pk>\d+)/interfaces/edit/$', views.InterfaceBulkEditView.as_view(), name='interface_bulk_edit'),
    url(r'^virtual-machines/(?P<pk>\d+)/interfaces/delete/$', views.InterfaceBulkDeleteView.as_view(), name='interface_bulk_delete'),
    url(r'^vm-interfaces/(?P<pk>\d+)/edit/$', views.InterfaceEditView.as_view(), name='interface_edit'),
    url(r'^vm-interfaces/(?P<pk>\d+)/delete/$', views.InterfaceDeleteView.as_view(), name='interface_delete'),

]
