from django.urls import include, path

from utilities.urls import get_model_urls
from . import views

app_name = 'virtualization'
urlpatterns = [

    path('cluster-types/', include(get_model_urls('virtualization', 'clustertype', detail=False))),
    path('cluster-types/<int:pk>/', include(get_model_urls('virtualization', 'clustertype'))),

    path('cluster-groups/', include(get_model_urls('virtualization', 'clustergroup', detail=False))),
    path('cluster-groups/<int:pk>/', include(get_model_urls('virtualization', 'clustergroup'))),

    path('clusters/', include(get_model_urls('virtualization', 'cluster', detail=False))),
    path('clusters/<int:pk>/', include(get_model_urls('virtualization', 'cluster'))),

    path('virtual-machines/', include(get_model_urls('virtualization', 'virtualmachine', detail=False))),
    path('virtual-machines/<int:pk>/', include(get_model_urls('virtualization', 'virtualmachine'))),

    path('interfaces/', include(get_model_urls('virtualization', 'vminterface', detail=False))),
    path('interfaces/<int:pk>/', include(get_model_urls('virtualization', 'vminterface'))),
    path(
        'virtual-machines/interfaces/add/',
        views.VirtualMachineBulkAddInterfaceView.as_view(),
        name='virtualmachine_bulk_add_vminterface'
    ),

    path('virtual-disks/', include(get_model_urls('virtualization', 'virtualdisk', detail=False))),
    path('virtual-disks/<int:pk>/', include(get_model_urls('virtualization', 'virtualdisk'))),
    path(
        'virtual-machines/disks/add/',
        views.VirtualMachineBulkAddVirtualDiskView.as_view(),
        name='virtualmachine_bulk_add_virtualdisk'
    ),
]
