from django.urls import include, path

from utilities.urls import get_model_urls
from . import views

app_name = 'dcim'
urlpatterns = [

    # Regions
    path('regions/', views.RegionListView.as_view(), name='region_list'),
    path('regions/add/', views.RegionEditView.as_view(), name='region_add'),
    path('regions/import/', views.RegionBulkImportView.as_view(), name='region_import'),
    path('regions/edit/', views.RegionBulkEditView.as_view(), name='region_bulk_edit'),
    path('regions/delete/', views.RegionBulkDeleteView.as_view(), name='region_bulk_delete'),
    path('regions/<int:pk>/', include(get_model_urls('dcim', 'region'))),

    # Site groups
    path('site-groups/', views.SiteGroupListView.as_view(), name='sitegroup_list'),
    path('site-groups/add/', views.SiteGroupEditView.as_view(), name='sitegroup_add'),
    path('site-groups/import/', views.SiteGroupBulkImportView.as_view(), name='sitegroup_import'),
    path('site-groups/edit/', views.SiteGroupBulkEditView.as_view(), name='sitegroup_bulk_edit'),
    path('site-groups/delete/', views.SiteGroupBulkDeleteView.as_view(), name='sitegroup_bulk_delete'),
    path('site-groups/<int:pk>/', include(get_model_urls('dcim', 'sitegroup'))),

    # Sites
    path('sites/', views.SiteListView.as_view(), name='site_list'),
    path('sites/add/', views.SiteEditView.as_view(), name='site_add'),
    path('sites/import/', views.SiteBulkImportView.as_view(), name='site_import'),
    path('sites/edit/', views.SiteBulkEditView.as_view(), name='site_bulk_edit'),
    path('sites/delete/', views.SiteBulkDeleteView.as_view(), name='site_bulk_delete'),
    path('sites/<int:pk>/', include(get_model_urls('dcim', 'site'))),

    # Locations
    path('locations/', views.LocationListView.as_view(), name='location_list'),
    path('locations/add/', views.LocationEditView.as_view(), name='location_add'),
    path('locations/import/', views.LocationBulkImportView.as_view(), name='location_import'),
    path('locations/edit/', views.LocationBulkEditView.as_view(), name='location_bulk_edit'),
    path('locations/delete/', views.LocationBulkDeleteView.as_view(), name='location_bulk_delete'),
    path('locations/<int:pk>/', include(get_model_urls('dcim', 'location'))),

    # Rack roles
    path('rack-roles/', views.RackRoleListView.as_view(), name='rackrole_list'),
    path('rack-roles/add/', views.RackRoleEditView.as_view(), name='rackrole_add'),
    path('rack-roles/import/', views.RackRoleBulkImportView.as_view(), name='rackrole_import'),
    path('rack-roles/edit/', views.RackRoleBulkEditView.as_view(), name='rackrole_bulk_edit'),
    path('rack-roles/delete/', views.RackRoleBulkDeleteView.as_view(), name='rackrole_bulk_delete'),
    path('rack-roles/<int:pk>/', include(get_model_urls('dcim', 'rackrole'))),

    # Rack reservations
    path('rack-reservations/', views.RackReservationListView.as_view(), name='rackreservation_list'),
    path('rack-reservations/add/', views.RackReservationEditView.as_view(), name='rackreservation_add'),
    path('rack-reservations/import/', views.RackReservationImportView.as_view(), name='rackreservation_import'),
    path('rack-reservations/edit/', views.RackReservationBulkEditView.as_view(), name='rackreservation_bulk_edit'),
    path('rack-reservations/delete/', views.RackReservationBulkDeleteView.as_view(), name='rackreservation_bulk_delete'),
    path('rack-reservations/<int:pk>/', include(get_model_urls('dcim', 'rackreservation'))),

    # Racks
    path('racks/', views.RackListView.as_view(), name='rack_list'),
    path('rack-elevations/', views.RackElevationListView.as_view(), name='rack_elevation_list'),
    path('racks/add/', views.RackEditView.as_view(), name='rack_add'),
    path('racks/import/', views.RackBulkImportView.as_view(), name='rack_import'),
    path('racks/edit/', views.RackBulkEditView.as_view(), name='rack_bulk_edit'),
    path('racks/delete/', views.RackBulkDeleteView.as_view(), name='rack_bulk_delete'),
    path('racks/<int:pk>/', include(get_model_urls('dcim', 'rack'))),

    # Rack Types
    path('rack-types/', views.RackTypeListView.as_view(), name='racktype_list'),
    path('rack-types/add/', views.RackTypeEditView.as_view(), name='racktype_add'),
    path('rack-types/import/', views.RackTypeBulkImportView.as_view(), name='racktype_import'),
    path('rack-types/edit/', views.RackTypeBulkEditView.as_view(), name='racktype_bulk_edit'),
    path('rack-types/delete/', views.RackTypeBulkDeleteView.as_view(), name='racktype_bulk_delete'),
    path('rack-types/<int:pk>/', include(get_model_urls('dcim', 'racktype'))),

    # Manufacturers
    path('manufacturers/', views.ManufacturerListView.as_view(), name='manufacturer_list'),
    path('manufacturers/add/', views.ManufacturerEditView.as_view(), name='manufacturer_add'),
    path('manufacturers/import/', views.ManufacturerBulkImportView.as_view(), name='manufacturer_import'),
    path('manufacturers/edit/', views.ManufacturerBulkEditView.as_view(), name='manufacturer_bulk_edit'),
    path('manufacturers/delete/', views.ManufacturerBulkDeleteView.as_view(), name='manufacturer_bulk_delete'),
    path('manufacturers/<int:pk>/', include(get_model_urls('dcim', 'manufacturer'))),

    # Device types
    path('device-types/', views.DeviceTypeListView.as_view(), name='devicetype_list'),
    path('device-types/add/', views.DeviceTypeEditView.as_view(), name='devicetype_add'),
    path('device-types/import/', views.DeviceTypeImportView.as_view(), name='devicetype_import'),
    path('device-types/edit/', views.DeviceTypeBulkEditView.as_view(), name='devicetype_bulk_edit'),
    path('device-types/delete/', views.DeviceTypeBulkDeleteView.as_view(), name='devicetype_bulk_delete'),
    path('device-types/<int:pk>/', include(get_model_urls('dcim', 'devicetype'))),

    # Module types
    path('module-types/', views.ModuleTypeListView.as_view(), name='moduletype_list'),
    path('module-types/add/', views.ModuleTypeEditView.as_view(), name='moduletype_add'),
    path('module-types/import/', views.ModuleTypeImportView.as_view(), name='moduletype_import'),
    path('module-types/edit/', views.ModuleTypeBulkEditView.as_view(), name='moduletype_bulk_edit'),
    path('module-types/delete/', views.ModuleTypeBulkDeleteView.as_view(), name='moduletype_bulk_delete'),
    path('module-types/<int:pk>/', include(get_model_urls('dcim', 'moduletype'))),

    # Console port templates
    path('console-port-templates/add/', views.ConsolePortTemplateCreateView.as_view(), name='consoleporttemplate_add'),
    path('console-port-templates/edit/', views.ConsolePortTemplateBulkEditView.as_view(), name='consoleporttemplate_bulk_edit'),
    path('console-port-templates/rename/', views.ConsolePortTemplateBulkRenameView.as_view(), name='consoleporttemplate_bulk_rename'),
    path('console-port-templates/delete/', views.ConsolePortTemplateBulkDeleteView.as_view(), name='consoleporttemplate_bulk_delete'),
    path('console-port-templates/<int:pk>/', include(get_model_urls('dcim', 'consoleporttemplate'))),

    # Console server port templates
    path('console-server-port-templates/add/', views.ConsoleServerPortTemplateCreateView.as_view(), name='consoleserverporttemplate_add'),
    path('console-server-port-templates/edit/', views.ConsoleServerPortTemplateBulkEditView.as_view(), name='consoleserverporttemplate_bulk_edit'),
    path('console-server-port-templates/rename/', views.ConsoleServerPortTemplateBulkRenameView.as_view(), name='consoleserverporttemplate_bulk_rename'),
    path('console-server-port-templates/delete/', views.ConsoleServerPortTemplateBulkDeleteView.as_view(), name='consoleserverporttemplate_bulk_delete'),
    path('console-server-port-templates/<int:pk>/', include(get_model_urls('dcim', 'consoleserverporttemplate'))),

    # Power port templates
    path('power-port-templates/add/', views.PowerPortTemplateCreateView.as_view(), name='powerporttemplate_add'),
    path('power-port-templates/edit/', views.PowerPortTemplateBulkEditView.as_view(), name='powerporttemplate_bulk_edit'),
    path('power-port-templates/rename/', views.PowerPortTemplateBulkRenameView.as_view(), name='powerporttemplate_bulk_rename'),
    path('power-port-templates/delete/', views.PowerPortTemplateBulkDeleteView.as_view(), name='powerporttemplate_bulk_delete'),
    path('power-port-templates/<int:pk>/', include(get_model_urls('dcim', 'powerporttemplate'))),

    # Power outlet templates
    path('power-outlet-templates/add/', views.PowerOutletTemplateCreateView.as_view(), name='poweroutlettemplate_add'),
    path('power-outlet-templates/edit/', views.PowerOutletTemplateBulkEditView.as_view(), name='poweroutlettemplate_bulk_edit'),
    path('power-outlet-templates/rename/', views.PowerOutletTemplateBulkRenameView.as_view(), name='poweroutlettemplate_bulk_rename'),
    path('power-outlet-templates/delete/', views.PowerOutletTemplateBulkDeleteView.as_view(), name='poweroutlettemplate_bulk_delete'),
    path('power-outlet-templates/<int:pk>/', include(get_model_urls('dcim', 'poweroutlettemplate'))),

    # Interface templates
    path('interface-templates/add/', views.InterfaceTemplateCreateView.as_view(), name='interfacetemplate_add'),
    path('interface-templates/edit/', views.InterfaceTemplateBulkEditView.as_view(), name='interfacetemplate_bulk_edit'),
    path('interface-templates/rename/', views.InterfaceTemplateBulkRenameView.as_view(), name='interfacetemplate_bulk_rename'),
    path('interface-templates/delete/', views.InterfaceTemplateBulkDeleteView.as_view(), name='interfacetemplate_bulk_delete'),
    path('interface-templates/<int:pk>/', include(get_model_urls('dcim', 'interfacetemplate'))),

    # Front port templates
    path('front-port-templates/add/', views.FrontPortTemplateCreateView.as_view(), name='frontporttemplate_add'),
    path('front-port-templates/edit/', views.FrontPortTemplateBulkEditView.as_view(), name='frontporttemplate_bulk_edit'),
    path('front-port-templates/rename/', views.FrontPortTemplateBulkRenameView.as_view(), name='frontporttemplate_bulk_rename'),
    path('front-port-templates/delete/', views.FrontPortTemplateBulkDeleteView.as_view(), name='frontporttemplate_bulk_delete'),
    path('front-port-templates/<int:pk>/', include(get_model_urls('dcim', 'frontporttemplate'))),

    # Rear port templates
    path('rear-port-templates/add/', views.RearPortTemplateCreateView.as_view(), name='rearporttemplate_add'),
    path('rear-port-templates/edit/', views.RearPortTemplateBulkEditView.as_view(), name='rearporttemplate_bulk_edit'),
    path('rear-port-templates/rename/', views.RearPortTemplateBulkRenameView.as_view(), name='rearporttemplate_bulk_rename'),
    path('rear-port-templates/delete/', views.RearPortTemplateBulkDeleteView.as_view(), name='rearporttemplate_bulk_delete'),
    path('rear-port-templates/<int:pk>/', include(get_model_urls('dcim', 'rearporttemplate'))),

    # Device bay templates
    path('device-bay-templates/add/', views.DeviceBayTemplateCreateView.as_view(), name='devicebaytemplate_add'),
    path('device-bay-templates/edit/', views.DeviceBayTemplateBulkEditView.as_view(), name='devicebaytemplate_bulk_edit'),
    path('device-bay-templates/rename/', views.DeviceBayTemplateBulkRenameView.as_view(), name='devicebaytemplate_bulk_rename'),
    path('device-bay-templates/delete/', views.DeviceBayTemplateBulkDeleteView.as_view(), name='devicebaytemplate_bulk_delete'),
    path('device-bay-templates/<int:pk>/', include(get_model_urls('dcim', 'devicebaytemplate'))),

    # Module bay templates
    path('module-bay-templates/add/', views.ModuleBayTemplateCreateView.as_view(), name='modulebaytemplate_add'),
    path('module-bay-templates/edit/', views.ModuleBayTemplateBulkEditView.as_view(), name='modulebaytemplate_bulk_edit'),
    path('module-bay-templates/rename/', views.ModuleBayTemplateBulkRenameView.as_view(), name='modulebaytemplate_bulk_rename'),
    path('module-bay-templates/delete/', views.ModuleBayTemplateBulkDeleteView.as_view(), name='modulebaytemplate_bulk_delete'),
    path('module-bay-templates/<int:pk>/', include(get_model_urls('dcim', 'modulebaytemplate'))),

    # Inventory item templates
    path('inventory-item-templates/add/', views.InventoryItemTemplateCreateView.as_view(), name='inventoryitemtemplate_add'),
    path('inventory-item-templates/edit/', views.InventoryItemTemplateBulkEditView.as_view(), name='inventoryitemtemplate_bulk_edit'),
    path('inventory-item-templates/rename/', views.InventoryItemTemplateBulkRenameView.as_view(), name='inventoryitemtemplate_bulk_rename'),
    path('inventory-item-templates/delete/', views.InventoryItemTemplateBulkDeleteView.as_view(), name='inventoryitemtemplate_bulk_delete'),
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

    # MAC addresses
    path('mac-addresses/', views.MACAddressListView.as_view(), name='macaddress_list'),
    path('mac-addresses/add/', views.MACAddressEditView.as_view(), name='macaddress_add'),
    path('mac-addresses/import/', views.MACAddressBulkImportView.as_view(), name='macaddress_import'),
    path('mac-addresses/edit/', views.MACAddressBulkEditView.as_view(), name='macaddress_bulk_edit'),
    path('mac-addresses/delete/', views.MACAddressBulkDeleteView.as_view(), name='macaddress_bulk_delete'),
    path('mac-addresses/<int:pk>/', include(get_model_urls('dcim', 'macaddress'))),

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
