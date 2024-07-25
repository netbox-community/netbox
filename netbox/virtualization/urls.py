from django.urls import include, path, re_path

from utilities.urls import get_model_urls
from . import views

app_name = 'virtualization'
urlpatterns = [

    # Cluster types
    path('cluster-types/', views.ClusterTypeListView.as_view(), name='clustertype_list'),
    path('cluster-types/add/', views.ClusterTypeEditView.as_view(), name='clustertype_add'),
    path('cluster-types/import/', views.ClusterTypeBulkImportView.as_view(), name='clustertype_import'),
    path('cluster-types/edit/', views.ClusterTypeBulkEditView.as_view(), name='clustertype_bulk_edit'),
    path('cluster-types/delete/', views.ClusterTypeBulkDeleteView.as_view(), name='clustertype_bulk_delete'),
    path('cluster-types/<int:pk>/', include(get_model_urls('virtualization', 'clustertype'))),

    # Cluster groups
    path('cluster-groups/', views.ClusterGroupListView.as_view(), name='clustergroup_list'),
    path('cluster-groups/add/', views.ClusterGroupEditView.as_view(), name='clustergroup_add'),
    path('cluster-groups/import/', views.ClusterGroupBulkImportView.as_view(), name='clustergroup_import'),
    path('cluster-groups/edit/', views.ClusterGroupBulkEditView.as_view(), name='clustergroup_bulk_edit'),
    path('cluster-groups/delete/', views.ClusterGroupBulkDeleteView.as_view(), name='clustergroup_bulk_delete'),
    path('cluster-groups/<int:pk>/', include(get_model_urls('virtualization', 'clustergroup'))),

    # Clusters
    path('clusters/', views.ClusterListView.as_view(), name='cluster_list'),
    path('clusters/add/', views.ClusterEditView.as_view(), name='cluster_add'),
    path('clusters/import/', views.ClusterBulkImportView.as_view(), name='cluster_import'),
    path('clusters/edit/', views.ClusterBulkEditView.as_view(), name='cluster_bulk_edit'),
    path('clusters/delete/', views.ClusterBulkDeleteView.as_view(), name='cluster_bulk_delete'),
    path('clusters/<int:pk>/', include(get_model_urls('virtualization', 'cluster'))),

    # Virtual machines
    path('virtual-machines/', views.VirtualMachineListView.as_view(), name='virtualmachine_list'),
    path('virtual-machines/add/', views.VirtualMachineEditView.as_view(), name='virtualmachine_add'),
    path('virtual-machines/import/', views.VirtualMachineBulkImportView.as_view(), name='virtualmachine_import'),
    path('virtual-machines/edit/', views.VirtualMachineBulkEditView.as_view(), name='virtualmachine_bulk_edit'),
    path('virtual-machines/delete/', views.VirtualMachineBulkDeleteView.as_view(), name='virtualmachine_bulk_delete'),
    path('virtual-machines/<int:pk>/', include(get_model_urls('virtualization', 'virtualmachine'))),

    # VM interfaces
    path('interfaces/', views.VMInterfaceListView.as_view(), name='vminterface_list'),
    path('interfaces/add/', views.VMInterfaceCreateView.as_view(), name='vminterface_add'),
    path('interfaces/import/', views.VMInterfaceBulkImportView.as_view(), name='vminterface_import'),
    path('interfaces/edit/', views.VMInterfaceBulkEditView.as_view(), name='vminterface_bulk_edit'),
    path('interfaces/rename/', views.VMInterfaceBulkRenameView.as_view(), name='vminterface_bulk_rename'),
    path('interfaces/delete/', views.VMInterfaceBulkDeleteView.as_view(), name='vminterface_bulk_delete'),
    path('interfaces/<int:pk>/', include(get_model_urls('virtualization', 'vminterface'))),
    path('virtual-machines/interfaces/add/', views.VirtualMachineBulkAddInterfaceView.as_view(), name='virtualmachine_bulk_add_vminterface'),

    # Virtual disks
    path('virtual-disks/', views.VirtualDiskListView.as_view(), name='virtualdisk_list'),
    path('virtual-disks/add/', views.VirtualDiskCreateView.as_view(), name='virtualdisk_add'),
    path('virtual-disks/import/', views.VirtualDiskBulkImportView.as_view(), name='virtualdisk_import'),
    path('virtual-disks/edit/', views.VirtualDiskBulkEditView.as_view(), name='virtualdisk_bulk_edit'),
    path('virtual-disks/rename/', views.VirtualDiskBulkRenameView.as_view(), name='virtualdisk_bulk_rename'),
    path('virtual-disks/delete/', views.VirtualDiskBulkDeleteView.as_view(), name='virtualdisk_bulk_delete'),
    path('virtual-disks/<int:pk>/', include(get_model_urls('virtualization', 'virtualdisk'))),
    path('virtual-machines/disks/add/', views.VirtualMachineBulkAddVirtualDiskView.as_view(), name='virtualmachine_bulk_add_virtualdisk'),

    # TODO: Remove in v4.2
    # Redirect old (pre-v4.1) URLs for VirtualDisk views
    re_path('disks/(?P<path>[a-z0-9/-]*)', views.VirtualDiskRedirectView.as_view()),
]
