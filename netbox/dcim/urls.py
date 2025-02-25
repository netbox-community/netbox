from django.urls import include, path

from utilities.urls import get_model_urls
from . import views

app_name = 'dcim'
urlpatterns = [

    path('regions/', include(get_model_urls('dcim', 'region', detail=False))),
    path('regions/<int:pk>/', include(get_model_urls('dcim', 'region'))),

    path('site-groups/', include(get_model_urls('dcim', 'sitegroup', detail=False))),
    path('site-groups/<int:pk>/', include(get_model_urls('dcim', 'sitegroup'))),

    path('sites/', include(get_model_urls('dcim', 'site', detail=False))),
    path('sites/<int:pk>/', include(get_model_urls('dcim', 'site'))),

    path('locations/', include(get_model_urls('dcim', 'location', detail=False))),
    path('locations/<int:pk>/', include(get_model_urls('dcim', 'location'))),

    path('rack-roles/', include(get_model_urls('dcim', 'rackrole', detail=False))),
    path('rack-roles/<int:pk>/', include(get_model_urls('dcim', 'rackrole'))),

    path('rack-reservations/', include(get_model_urls('dcim', 'rackreservation', detail=False))),
    path('rack-reservations/<int:pk>/', include(get_model_urls('dcim', 'rackreservation'))),

    path('racks/', include(get_model_urls('dcim', 'rack', detail=False))),
    path('racks/<int:pk>/', include(get_model_urls('dcim', 'rack'))),
    path('rack-elevations/', views.RackElevationListView.as_view(), name='rack_elevation_list'),

    path('rack-types/', include(get_model_urls('dcim', 'racktype', detail=False))),
    path('rack-types/<int:pk>/', include(get_model_urls('dcim', 'racktype'))),

    path('manufacturers/', include(get_model_urls('dcim', 'manufacturer', detail=False))),
    path('manufacturers/<int:pk>/', include(get_model_urls('dcim', 'manufacturer'))),

    path('device-types/', include(get_model_urls('dcim', 'devicetype', detail=False))),
    path('device-types/<int:pk>/', include(get_model_urls('dcim', 'devicetype'))),

    path('module-types/', include(get_model_urls('dcim', 'moduletype', detail=False))),
    path('module-types/<int:pk>/', include(get_model_urls('dcim', 'moduletype'))),

    path('console-port-templates/', include(get_model_urls('dcim', 'consoleporttemplate', detail=False))),
    path('console-port-templates/<int:pk>/', include(get_model_urls('dcim', 'consoleporttemplate'))),

    path('console-server-port-templates/', include(get_model_urls('dcim', 'consoleserverporttemplate', detail=False))),
    path('console-server-port-templates/<int:pk>/', include(get_model_urls('dcim', 'consoleserverporttemplate'))),

    path('power-port-templates/', include(get_model_urls('dcim', 'powerporttemplate', detail=False))),
    path('power-port-templates/<int:pk>/', include(get_model_urls('dcim', 'powerporttemplate'))),

    path('power-outlet-templates/', include(get_model_urls('dcim', 'poweroutlettemplate', detail=False))),
    path('power-outlet-templates/<int:pk>/', include(get_model_urls('dcim', 'poweroutlettemplate'))),

    path('interface-templates/', include(get_model_urls('dcim', 'interfacetemplate', detail=False))),
    path('interface-templates/<int:pk>/', include(get_model_urls('dcim', 'interfacetemplate'))),

    path('front-port-templates/', include(get_model_urls('dcim', 'frontporttemplate', detail=False))),
    path('front-port-templates/<int:pk>/', include(get_model_urls('dcim', 'frontporttemplate'))),

    path('rear-port-templates/', include(get_model_urls('dcim', 'rearporttemplate', detail=False))),
    path('rear-port-templates/<int:pk>/', include(get_model_urls('dcim', 'rearporttemplate'))),

    path('device-bay-templates/', include(get_model_urls('dcim', 'devicebaytemplate', detail=False))),
    path('device-bay-templates/<int:pk>/', include(get_model_urls('dcim', 'devicebaytemplate'))),

    path('module-bay-templates/', include(get_model_urls('dcim', 'modulebaytemplate', detail=False))),
    path('module-bay-templates/<int:pk>/', include(get_model_urls('dcim', 'modulebaytemplate'))),

    path('inventory-item-templates/', include(get_model_urls('dcim', 'inventoryitemtemplate', detail=False))),
    path('inventory-item-templates/<int:pk>/', include(get_model_urls('dcim', 'inventoryitemtemplate'))),

    path('device-roles/', include(get_model_urls('dcim', 'devicerole', detail=False))),
    path('device-roles/<int:pk>/', include(get_model_urls('dcim', 'devicerole'))),

    path('platforms/', include(get_model_urls('dcim', 'platform', detail=False))),
    path('platforms/<int:pk>/', include(get_model_urls('dcim', 'platform'))),

    path('devices/', include(get_model_urls('dcim', 'device', detail=False))),
    path('devices/<int:pk>/', include(get_model_urls('dcim', 'device'))),

    path('virtual-device-contexts/', include(get_model_urls('dcim', 'virtualdevicecontext', detail=False))),
    path('virtual-device-contexts/<int:pk>/', include(get_model_urls('dcim', 'virtualdevicecontext'))),

    path('modules/', include(get_model_urls('dcim', 'module', detail=False))),
    path('modules/<int:pk>/', include(get_model_urls('dcim', 'module'))),

    path('console-ports/', include(get_model_urls('dcim', 'consoleport', detail=False))),
    path('console-ports/<int:pk>/', include(get_model_urls('dcim', 'consoleport'))),
    path(
        'devices/console-ports/add/',
        views.DeviceBulkAddConsolePortView.as_view(),
        name='device_bulk_add_consoleport'
    ),

    path('console-server-ports/', include(get_model_urls('dcim', 'consoleserverport', detail=False))),
    path('console-server-ports/<int:pk>/', include(get_model_urls('dcim', 'consoleserverport'))),
    path(
        'devices/console-server-ports/add/',
        views.DeviceBulkAddConsoleServerPortView.as_view(),
        name='device_bulk_add_consoleserverport'
    ),

    path('power-ports/', include(get_model_urls('dcim', 'powerport', detail=False))),
    path('power-ports/<int:pk>/', include(get_model_urls('dcim', 'powerport'))),
    path('devices/power-ports/add/', views.DeviceBulkAddPowerPortView.as_view(), name='device_bulk_add_powerport'),

    path('power-outlets/', include(get_model_urls('dcim', 'poweroutlet', detail=False))),
    path('power-outlets/<int:pk>/', include(get_model_urls('dcim', 'poweroutlet'))),
    path(
        'devices/power-outlets/add/',
        views.DeviceBulkAddPowerOutletView.as_view(),
        name='device_bulk_add_poweroutlet'
    ),

    path('interfaces/', include(get_model_urls('dcim', 'interface', detail=False))),
    path('interfaces/<int:pk>/', include(get_model_urls('dcim', 'interface'))),
    path('devices/interfaces/add/', views.DeviceBulkAddInterfaceView.as_view(), name='device_bulk_add_interface'),

    path('front-ports/', include(get_model_urls('dcim', 'frontport', detail=False))),
    path('front-ports/<int:pk>/', include(get_model_urls('dcim', 'frontport'))),

    path('rear-ports/', include(get_model_urls('dcim', 'rearport', detail=False))),
    path('rear-ports/<int:pk>/', include(get_model_urls('dcim', 'rearport'))),
    path('devices/rear-ports/add/', views.DeviceBulkAddRearPortView.as_view(), name='device_bulk_add_rearport'),

    path('module-bays/', include(get_model_urls('dcim', 'modulebay', detail=False))),
    path('module-bays/<int:pk>/', include(get_model_urls('dcim', 'modulebay'))),
    path('devices/module-bays/add/', views.DeviceBulkAddModuleBayView.as_view(), name='device_bulk_add_modulebay'),

    path('device-bays/', include(get_model_urls('dcim', 'devicebay', detail=False))),
    path('device-bays/<int:pk>/', include(get_model_urls('dcim', 'devicebay'))),
    path('devices/device-bays/add/', views.DeviceBulkAddDeviceBayView.as_view(), name='device_bulk_add_devicebay'),

    path('inventory-items/', include(get_model_urls('dcim', 'inventoryitem', detail=False))),
    path('inventory-items/<int:pk>/', include(get_model_urls('dcim', 'inventoryitem'))),
    path(
        'devices/inventory-items/add/',
        views.DeviceBulkAddInventoryItemView.as_view(),
        name='device_bulk_add_inventoryitem'
    ),

    path('inventory-item-roles/', include(get_model_urls('dcim', 'inventoryitemrole', detail=False))),
    path('inventory-item-roles/<int:pk>/', include(get_model_urls('dcim', 'inventoryitemrole'))),

    path('cables/', include(get_model_urls('dcim', 'cable', detail=False))),
    path('cables/<int:pk>/', include(get_model_urls('dcim', 'cable'))),

    # Console/power/interface connections (read-only)
    path('console-connections/', views.ConsoleConnectionsListView.as_view(), name='console_connections_list'),
    path('power-connections/', views.PowerConnectionsListView.as_view(), name='power_connections_list'),
    path('interface-connections/', views.InterfaceConnectionsListView.as_view(), name='interface_connections_list'),

    path('virtual-chassis/', include(get_model_urls('dcim', 'virtualchassis', detail=False))),
    path('virtual-chassis/<int:pk>/', include(get_model_urls('dcim', 'virtualchassis'))),
    path(
        'virtual-chassis-members/<int:pk>/delete/',
        views.VirtualChassisRemoveMemberView.as_view(),
        name='virtualchassis_remove_member'
    ),

    path('power-panels/', include(get_model_urls('dcim', 'powerpanel', detail=False))),
    path('power-panels/<int:pk>/', include(get_model_urls('dcim', 'powerpanel'))),

    path('power-feeds/', include(get_model_urls('dcim', 'powerfeed', detail=False))),
    path('power-feeds/<int:pk>/', include(get_model_urls('dcim', 'powerfeed'))),

    path('mac-addresses/', include(get_model_urls('dcim', 'macaddress', detail=False))),
    path('mac-addresses/<int:pk>/', include(get_model_urls('dcim', 'macaddress'))),

]
