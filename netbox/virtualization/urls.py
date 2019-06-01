from django.urls import path

from extras.views import ObjectChangeLogView
from ipam.views import ServiceCreateView
from . import views
from .models import Cluster, ClusterGroup, ClusterType, VirtualMachine

app_name = 'virtualization'
urlpatterns = [

    # Cluster types
    path(r'cluster-types/', views.ClusterTypeListView.as_view(), name='clustertype_list'),
    path(r'cluster-types/add/', views.ClusterTypeCreateView.as_view(), name='clustertype_add'),
    path(r'cluster-types/import/', views.ClusterTypeBulkImportView.as_view(), name='clustertype_import'),
    path(r'cluster-types/delete/', views.ClusterTypeBulkDeleteView.as_view(), name='clustertype_bulk_delete'),
    path(r'cluster-types/<slug:slug>/edit/', views.ClusterTypeEditView.as_view(), name='clustertype_edit'),
    path(r'cluster-types/<slug:slug>/changelog/', ObjectChangeLogView.as_view(), name='clustertype_changelog', kwargs={'model': ClusterType}),

    # Cluster groups
    path(r'cluster-groups/', views.ClusterGroupListView.as_view(), name='clustergroup_list'),
    path(r'cluster-groups/add/', views.ClusterGroupCreateView.as_view(), name='clustergroup_add'),
    path(r'cluster-groups/import/', views.ClusterGroupBulkImportView.as_view(), name='clustergroup_import'),
    path(r'cluster-groups/delete/', views.ClusterGroupBulkDeleteView.as_view(), name='clustergroup_bulk_delete'),
    path(r'cluster-groups/<slug:slug>/edit/', views.ClusterGroupEditView.as_view(), name='clustergroup_edit'),
    path(r'cluster-groups/<slug:slug>/changelog/', ObjectChangeLogView.as_view(), name='clustergroup_changelog', kwargs={'model': ClusterGroup}),

    # Clusters
    path(r'clusters/', views.ClusterListView.as_view(), name='cluster_list'),
    path(r'clusters/add/', views.ClusterCreateView.as_view(), name='cluster_add'),
    path(r'clusters/import/', views.ClusterBulkImportView.as_view(), name='cluster_import'),
    path(r'clusters/edit/', views.ClusterBulkEditView.as_view(), name='cluster_bulk_edit'),
    path(r'clusters/delete/', views.ClusterBulkDeleteView.as_view(), name='cluster_bulk_delete'),
    path(r'clusters/<int:pk>/', views.ClusterView.as_view(), name='cluster'),
    path(r'clusters/<int:pk>/edit/', views.ClusterEditView.as_view(), name='cluster_edit'),
    path(r'clusters/<int:pk>/delete/', views.ClusterDeleteView.as_view(), name='cluster_delete'),
    path(r'clusters/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='cluster_changelog', kwargs={'model': Cluster}),
    path(r'clusters/<int:pk>/devices/add/', views.ClusterAddDevicesView.as_view(), name='cluster_add_devices'),
    path(r'clusters/<int:pk>/devices/remove/', views.ClusterRemoveDevicesView.as_view(), name='cluster_remove_devices'),

    # Virtual machines
    path(r'virtual-machines/', views.VirtualMachineListView.as_view(), name='virtualmachine_list'),
    path(r'virtual-machines/add/', views.VirtualMachineCreateView.as_view(), name='virtualmachine_add'),
    path(r'virtual-machines/import/', views.VirtualMachineBulkImportView.as_view(), name='virtualmachine_import'),
    path(r'virtual-machines/edit/', views.VirtualMachineBulkEditView.as_view(), name='virtualmachine_bulk_edit'),
    path(r'virtual-machines/delete/', views.VirtualMachineBulkDeleteView.as_view(), name='virtualmachine_bulk_delete'),
    path(r'virtual-machines/<int:pk>/', views.VirtualMachineView.as_view(), name='virtualmachine'),
    path(r'virtual-machines/<int:pk>/edit/', views.VirtualMachineEditView.as_view(), name='virtualmachine_edit'),
    path(r'virtual-machines/<int:pk>/delete/', views.VirtualMachineDeleteView.as_view(), name='virtualmachine_delete'),
    path(r'virtual-machines/<int:pk>/config-context/', views.VirtualMachineConfigContextView.as_view(), name='virtualmachine_configcontext'),
    path(r'virtual-machines/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='virtualmachine_changelog', kwargs={'model': VirtualMachine}),
    path(r'virtual-machines/<int:virtualmachine>/services/assign/', ServiceCreateView.as_view(), name='virtualmachine_service_assign'),

    # VM interfaces
    path(r'virtual-machines/interfaces/add/', views.VirtualMachineBulkAddInterfaceView.as_view(), name='virtualmachine_bulk_add_interface'),
    path(r'virtual-machines/<int:pk>/interfaces/add/', views.InterfaceCreateView.as_view(), name='interface_add'),
    path(r'virtual-machines/<int:pk>/interfaces/edit/', views.InterfaceBulkEditView.as_view(), name='interface_bulk_edit'),
    path(r'virtual-machines/<int:pk>/interfaces/delete/', views.InterfaceBulkDeleteView.as_view(), name='interface_bulk_delete'),
    path(r'vm-interfaces/<int:pk>/edit/', views.InterfaceEditView.as_view(), name='interface_edit'),
    path(r'vm-interfaces/<int:pk>/delete/', views.InterfaceDeleteView.as_view(), name='interface_delete'),

]
