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

    # Device roles
    path('device-roles/', views.DeviceRoleListView.as_view(), name='devicerole_list'),
    path('device-roles/add/', views.DeviceRoleEditView.as_view(), name='devicerole_add'),
    path('device-roles/import/', views.DeviceRoleBulkImportView.as_view(), name='devicerole_import'),
    path('device-roles/edit/', views.DeviceRoleBulkEditView.as_view(), name='devicerole_bulk_edit'),
    path('device-roles/delete/', views.DeviceRoleBulkDeleteView.as_view(), name='devicerole_bulk_delete'),
    path('device-roles/<int:pk>/', include(get_model_urls('dcim', 'devicerole'))),

    # Platforms
    path('platforms/', views.PlatformListView.as_view(), name='platform_list'),
    path('platforms/add/', views.PlatformEditView.as_view(), name='platform_add'),
    path('platforms/import/', views.PlatformBulkImportView.as_view(), name='platform_import'),
    path('platforms/edit/', views.PlatformBulkEditView.as_view(), name='platform_bulk_edit'),
    path('platforms/delete/', views.PlatformBulkDeleteView.as_view(), name='platform_bulk_delete'),
    path('platforms/<int:pk>/', include(get_model_urls('dcim', 'platform'))),

    # Devices
    path('devices/', views.DeviceListView.as_view(), name='device_list'),
    path('devices/add/', views.DeviceEditView.as_view(), name='device_add'),
    path('devices/import/', views.DeviceBulkImportView.as_view(), name='device_import'),
    path('devices/edit/', views.DeviceBulkEditView.as_view(), name='device_bulk_edit'),
    path('devices/rename/', views.DeviceBulkRenameView.as_view(), name='device_bulk_rename'),
    path('devices/delete/', views.DeviceBulkDeleteView.as_view(), name='device_bulk_delete'),
    path('devices/<int:pk>/', include(get_model_urls('dcim', 'device'))),

    # Virtual Device Context
    path('virtual-device-contexts/', views.VirtualDeviceContextListView.as_view(), name='virtualdevicecontext_list'),
    path('virtual-device-contexts/add/', views.VirtualDeviceContextEditView.as_view(), name='virtualdevicecontext_add'),
    path('virtual-device-contexts/import/', views.VirtualDeviceContextBulkImportView.as_view(), name='virtualdevicecontext_import'),
    path('virtual-device-contexts/edit/', views.VirtualDeviceContextBulkEditView.as_view(), name='virtualdevicecontext_bulk_edit'),
    path('virtual-device-contexts/delete/', views.VirtualDeviceContextBulkDeleteView.as_view(), name='virtualdevicecontext_bulk_delete'),
    path('virtual-device-contexts/<int:pk>/', include(get_model_urls('dcim', 'virtualdevicecontext'))),

    # Modules
    path('modules/', views.ModuleListView.as_view(), name='module_list'),
    path('modules/add/', views.ModuleEditView.as_view(), name='module_add'),
    path('modules/import/', views.ModuleBulkImportView.as_view(), name='module_import'),
    path('modules/edit/', views.ModuleBulkEditView.as_view(), name='module_bulk_edit'),
    path('modules/delete/', views.ModuleBulkDeleteView.as_view(), name='module_bulk_delete'),
    path('modules/<int:pk>/', include(get_model_urls('dcim', 'module'))),

    # Console ports
    path('console-ports/', views.ConsolePortListView.as_view(), name='consoleport_list'),
    path('console-ports/add/', views.ConsolePortCreateView.as_view(), name='consoleport_add'),
    path('console-ports/import/', views.ConsolePortBulkImportView.as_view(), name='consoleport_import'),
    path('console-ports/edit/', views.ConsolePortBulkEditView.as_view(), name='consoleport_bulk_edit'),
    path('console-ports/rename/', views.ConsolePortBulkRenameView.as_view(), name='consoleport_bulk_rename'),
    path('console-ports/disconnect/', views.ConsolePortBulkDisconnectView.as_view(), name='consoleport_bulk_disconnect'),
    path('console-ports/delete/', views.ConsolePortBulkDeleteView.as_view(), name='consoleport_bulk_delete'),
    path('console-ports/<int:pk>/', include(get_model_urls('dcim', 'consoleport'))),
    path('devices/console-ports/add/', views.DeviceBulkAddConsolePortView.as_view(), name='device_bulk_add_consoleport'),

    # Console server ports
    path('console-server-ports/', views.ConsoleServerPortListView.as_view(), name='consoleserverport_list'),
    path('console-server-ports/add/', views.ConsoleServerPortCreateView.as_view(), name='consoleserverport_add'),
    path('console-server-ports/import/', views.ConsoleServerPortBulkImportView.as_view(), name='consoleserverport_import'),
    path('console-server-ports/edit/', views.ConsoleServerPortBulkEditView.as_view(), name='consoleserverport_bulk_edit'),
    path('console-server-ports/rename/', views.ConsoleServerPortBulkRenameView.as_view(), name='consoleserverport_bulk_rename'),
    path('console-server-ports/disconnect/', views.ConsoleServerPortBulkDisconnectView.as_view(), name='consoleserverport_bulk_disconnect'),
    path('console-server-ports/delete/', views.ConsoleServerPortBulkDeleteView.as_view(), name='consoleserverport_bulk_delete'),
    path('console-server-ports/<int:pk>/', include(get_model_urls('dcim', 'consoleserverport'))),
    path('devices/console-server-ports/add/', views.DeviceBulkAddConsoleServerPortView.as_view(), name='device_bulk_add_consoleserverport'),

    # Power ports
    path('power-ports/', views.PowerPortListView.as_view(), name='powerport_list'),
    path('power-ports/add/', views.PowerPortCreateView.as_view(), name='powerport_add'),
    path('power-ports/import/', views.PowerPortBulkImportView.as_view(), name='powerport_import'),
    path('power-ports/edit/', views.PowerPortBulkEditView.as_view(), name='powerport_bulk_edit'),
    path('power-ports/rename/', views.PowerPortBulkRenameView.as_view(), name='powerport_bulk_rename'),
    path('power-ports/disconnect/', views.PowerPortBulkDisconnectView.as_view(), name='powerport_bulk_disconnect'),
    path('power-ports/delete/', views.PowerPortBulkDeleteView.as_view(), name='powerport_bulk_delete'),
    path('power-ports/<int:pk>/', include(get_model_urls('dcim', 'powerport'))),
    path('devices/power-ports/add/', views.DeviceBulkAddPowerPortView.as_view(), name='device_bulk_add_powerport'),

    # Power outlets
    path('power-outlets/', views.PowerOutletListView.as_view(), name='poweroutlet_list'),
    path('power-outlets/add/', views.PowerOutletCreateView.as_view(), name='poweroutlet_add'),
    path('power-outlets/import/', views.PowerOutletBulkImportView.as_view(), name='poweroutlet_import'),
    path('power-outlets/edit/', views.PowerOutletBulkEditView.as_view(), name='poweroutlet_bulk_edit'),
    path('power-outlets/rename/', views.PowerOutletBulkRenameView.as_view(), name='poweroutlet_bulk_rename'),
    path('power-outlets/disconnect/', views.PowerOutletBulkDisconnectView.as_view(), name='poweroutlet_bulk_disconnect'),
    path('power-outlets/delete/', views.PowerOutletBulkDeleteView.as_view(), name='poweroutlet_bulk_delete'),
    path('power-outlets/<int:pk>/', include(get_model_urls('dcim', 'poweroutlet'))),
    path('devices/power-outlets/add/', views.DeviceBulkAddPowerOutletView.as_view(), name='device_bulk_add_poweroutlet'),

    # Interfaces
    path('interfaces/', views.InterfaceListView.as_view(), name='interface_list'),
    path('interfaces/add/', views.InterfaceCreateView.as_view(), name='interface_add'),
    path('interfaces/import/', views.InterfaceBulkImportView.as_view(), name='interface_import'),
    path('interfaces/edit/', views.InterfaceBulkEditView.as_view(), name='interface_bulk_edit'),
    path('interfaces/rename/', views.InterfaceBulkRenameView.as_view(), name='interface_bulk_rename'),
    path('interfaces/disconnect/', views.InterfaceBulkDisconnectView.as_view(), name='interface_bulk_disconnect'),
    path('interfaces/delete/', views.InterfaceBulkDeleteView.as_view(), name='interface_bulk_delete'),
    path('interfaces/<int:pk>/', include(get_model_urls('dcim', 'interface'))),
    path('devices/interfaces/add/', views.DeviceBulkAddInterfaceView.as_view(), name='device_bulk_add_interface'),

    # Front ports
    path('front-ports/', views.FrontPortListView.as_view(), name='frontport_list'),
    path('front-ports/add/', views.FrontPortCreateView.as_view(), name='frontport_add'),
    path('front-ports/import/', views.FrontPortBulkImportView.as_view(), name='frontport_import'),
    path('front-ports/edit/', views.FrontPortBulkEditView.as_view(), name='frontport_bulk_edit'),
    path('front-ports/rename/', views.FrontPortBulkRenameView.as_view(), name='frontport_bulk_rename'),
    path('front-ports/disconnect/', views.FrontPortBulkDisconnectView.as_view(), name='frontport_bulk_disconnect'),
    path('front-ports/delete/', views.FrontPortBulkDeleteView.as_view(), name='frontport_bulk_delete'),
    path('front-ports/<int:pk>/', include(get_model_urls('dcim', 'frontport'))),
    # path('devices/front-ports/add/', views.DeviceBulkAddFrontPortView.as_view(), name='device_bulk_add_frontport'),

    # Rear ports
    path('rear-ports/', views.RearPortListView.as_view(), name='rearport_list'),
    path('rear-ports/add/', views.RearPortCreateView.as_view(), name='rearport_add'),
    path('rear-ports/import/', views.RearPortBulkImportView.as_view(), name='rearport_import'),
    path('rear-ports/edit/', views.RearPortBulkEditView.as_view(), name='rearport_bulk_edit'),
    path('rear-ports/rename/', views.RearPortBulkRenameView.as_view(), name='rearport_bulk_rename'),
    path('rear-ports/disconnect/', views.RearPortBulkDisconnectView.as_view(), name='rearport_bulk_disconnect'),
    path('rear-ports/delete/', views.RearPortBulkDeleteView.as_view(), name='rearport_bulk_delete'),
    path('rear-ports/<int:pk>/', include(get_model_urls('dcim', 'rearport'))),
    path('devices/rear-ports/add/', views.DeviceBulkAddRearPortView.as_view(), name='device_bulk_add_rearport'),

    # Module bays
    path('module-bays/', views.ModuleBayListView.as_view(), name='modulebay_list'),
    path('module-bays/add/', views.ModuleBayCreateView.as_view(), name='modulebay_add'),
    path('module-bays/import/', views.ModuleBayBulkImportView.as_view(), name='modulebay_import'),
    path('module-bays/edit/', views.ModuleBayBulkEditView.as_view(), name='modulebay_bulk_edit'),
    path('module-bays/rename/', views.ModuleBayBulkRenameView.as_view(), name='modulebay_bulk_rename'),
    path('module-bays/delete/', views.ModuleBayBulkDeleteView.as_view(), name='modulebay_bulk_delete'),
    path('module-bays/<int:pk>/', include(get_model_urls('dcim', 'modulebay'))),
    path('devices/module-bays/add/', views.DeviceBulkAddModuleBayView.as_view(), name='device_bulk_add_modulebay'),

    # Device bays
    path('device-bays/', views.DeviceBayListView.as_view(), name='devicebay_list'),
    path('device-bays/add/', views.DeviceBayCreateView.as_view(), name='devicebay_add'),
    path('device-bays/import/', views.DeviceBayBulkImportView.as_view(), name='devicebay_import'),
    path('device-bays/edit/', views.DeviceBayBulkEditView.as_view(), name='devicebay_bulk_edit'),
    path('device-bays/rename/', views.DeviceBayBulkRenameView.as_view(), name='devicebay_bulk_rename'),
    path('device-bays/delete/', views.DeviceBayBulkDeleteView.as_view(), name='devicebay_bulk_delete'),
    path('device-bays/<int:pk>/', include(get_model_urls('dcim', 'devicebay'))),
    path('devices/device-bays/add/', views.DeviceBulkAddDeviceBayView.as_view(), name='device_bulk_add_devicebay'),

    # Inventory items
    path('inventory-items/', views.InventoryItemListView.as_view(), name='inventoryitem_list'),
    path('inventory-items/add/', views.InventoryItemCreateView.as_view(), name='inventoryitem_add'),
    path('inventory-items/import/', views.InventoryItemBulkImportView.as_view(), name='inventoryitem_import'),
    path('inventory-items/edit/', views.InventoryItemBulkEditView.as_view(), name='inventoryitem_bulk_edit'),
    path('inventory-items/rename/', views.InventoryItemBulkRenameView.as_view(), name='inventoryitem_bulk_rename'),
    path('inventory-items/delete/', views.InventoryItemBulkDeleteView.as_view(), name='inventoryitem_bulk_delete'),
    path('inventory-items/<int:pk>/', include(get_model_urls('dcim', 'inventoryitem'))),
    path('devices/inventory-items/add/', views.DeviceBulkAddInventoryItemView.as_view(), name='device_bulk_add_inventoryitem'),

    # Inventory item roles
    path('inventory-item-roles/', views.InventoryItemRoleListView.as_view(), name='inventoryitemrole_list'),
    path('inventory-item-roles/add/', views.InventoryItemRoleEditView.as_view(), name='inventoryitemrole_add'),
    path('inventory-item-roles/import/', views.InventoryItemRoleBulkImportView.as_view(), name='inventoryitemrole_import'),
    path('inventory-item-roles/edit/', views.InventoryItemRoleBulkEditView.as_view(), name='inventoryitemrole_bulk_edit'),
    path('inventory-item-roles/delete/', views.InventoryItemRoleBulkDeleteView.as_view(), name='inventoryitemrole_bulk_delete'),
    path('inventory-item-roles/<int:pk>/', include(get_model_urls('dcim', 'inventoryitemrole'))),

    # Cables
    path('cables/', views.CableListView.as_view(), name='cable_list'),
    path('cables/add/', views.CableEditView.as_view(), name='cable_add'),
    path('cables/import/', views.CableBulkImportView.as_view(), name='cable_import'),
    path('cables/edit/', views.CableBulkEditView.as_view(), name='cable_bulk_edit'),
    path('cables/delete/', views.CableBulkDeleteView.as_view(), name='cable_bulk_delete'),
    path('cables/<int:pk>/', include(get_model_urls('dcim', 'cable'))),

    # Console/power/interface connections (read-only)
    path('console-connections/', views.ConsoleConnectionsListView.as_view(), name='console_connections_list'),
    path('power-connections/', views.PowerConnectionsListView.as_view(), name='power_connections_list'),
    path('interface-connections/', views.InterfaceConnectionsListView.as_view(), name='interface_connections_list'),

    # Virtual chassis
    path('virtual-chassis/', views.VirtualChassisListView.as_view(), name='virtualchassis_list'),
    path('virtual-chassis/add/', views.VirtualChassisCreateView.as_view(), name='virtualchassis_add'),
    path('virtual-chassis/import/', views.VirtualChassisBulkImportView.as_view(), name='virtualchassis_import'),
    path('virtual-chassis/edit/', views.VirtualChassisBulkEditView.as_view(), name='virtualchassis_bulk_edit'),
    path('virtual-chassis/delete/', views.VirtualChassisBulkDeleteView.as_view(), name='virtualchassis_bulk_delete'),
    path('virtual-chassis/<int:pk>/', include(get_model_urls('dcim', 'virtualchassis'))),
    path('virtual-chassis-members/<int:pk>/delete/', views.VirtualChassisRemoveMemberView.as_view(), name='virtualchassis_remove_member'),

    # Power panels
    path('power-panels/', views.PowerPanelListView.as_view(), name='powerpanel_list'),
    path('power-panels/add/', views.PowerPanelEditView.as_view(), name='powerpanel_add'),
    path('power-panels/import/', views.PowerPanelBulkImportView.as_view(), name='powerpanel_import'),
    path('power-panels/edit/', views.PowerPanelBulkEditView.as_view(), name='powerpanel_bulk_edit'),
    path('power-panels/delete/', views.PowerPanelBulkDeleteView.as_view(), name='powerpanel_bulk_delete'),
    path('power-panels/<int:pk>/', include(get_model_urls('dcim', 'powerpanel'))),

    # Power feeds
    path('power-feeds/', views.PowerFeedListView.as_view(), name='powerfeed_list'),
    path('power-feeds/add/', views.PowerFeedEditView.as_view(), name='powerfeed_add'),
    path('power-feeds/import/', views.PowerFeedBulkImportView.as_view(), name='powerfeed_import'),
    path('power-feeds/edit/', views.PowerFeedBulkEditView.as_view(), name='powerfeed_bulk_edit'),
    path('power-feeds/disconnect/', views.PowerFeedBulkDisconnectView.as_view(), name='powerfeed_bulk_disconnect'),
    path('power-feeds/delete/', views.PowerFeedBulkDeleteView.as_view(), name='powerfeed_bulk_delete'),
    path('power-feeds/<int:pk>/', include(get_model_urls('dcim', 'powerfeed'))),

]
