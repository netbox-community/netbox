from django.urls import path

from extras.views import ObjectChangeLogView, ImageAttachmentEditView
from ipam.views import ServiceCreateView
from secrets.views import secret_add
from . import views
from .models import (
    Cable, ConsolePort, ConsoleServerPort, Device, DeviceRole, DeviceType, FrontPort, Interface, Manufacturer, Platform,
    PowerFeed, PowerPanel, PowerPort, PowerOutlet, Rack, RackGroup, RackReservation, RackRole, RearPort, Region, Site,
    VirtualChassis,
)

app_name = 'dcim'
urlpatterns = [

    # Regions
    path(r'regions/', views.RegionListView.as_view(), name='region_list'),
    path(r'regions/add/', views.RegionCreateView.as_view(), name='region_add'),
    path(r'regions/import/', views.RegionBulkImportView.as_view(), name='region_import'),
    path(r'regions/delete/', views.RegionBulkDeleteView.as_view(), name='region_bulk_delete'),
    path(r'regions/<int:pk>/edit/', views.RegionEditView.as_view(), name='region_edit'),
    path(r'regions/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='region_changelog', kwargs={'model': Region}),

    # Sites
    path(r'sites/', views.SiteListView.as_view(), name='site_list'),
    path(r'sites/add/', views.SiteCreateView.as_view(), name='site_add'),
    path(r'sites/import/', views.SiteBulkImportView.as_view(), name='site_import'),
    path(r'sites/edit/', views.SiteBulkEditView.as_view(), name='site_bulk_edit'),
    path(r'sites/delete/', views.SiteBulkDeleteView.as_view(), name='site_bulk_delete'),
    path(r'sites/<slug:slug>/', views.SiteView.as_view(), name='site'),
    path(r'sites/<slug:slug>/edit/', views.SiteEditView.as_view(), name='site_edit'),
    path(r'sites/<slug:slug>/delete/', views.SiteDeleteView.as_view(), name='site_delete'),
    path(r'sites/<slug:slug>/changelog/', ObjectChangeLogView.as_view(), name='site_changelog', kwargs={'model': Site}),
    path(r'sites/<int:object_id>/images/add/', ImageAttachmentEditView.as_view(), name='site_add_image', kwargs={'model': Site}),

    # Rack groups
    path(r'rack-groups/', views.RackGroupListView.as_view(), name='rackgroup_list'),
    path(r'rack-groups/add/', views.RackGroupCreateView.as_view(), name='rackgroup_add'),
    path(r'rack-groups/import/', views.RackGroupBulkImportView.as_view(), name='rackgroup_import'),
    path(r'rack-groups/delete/', views.RackGroupBulkDeleteView.as_view(), name='rackgroup_bulk_delete'),
    path(r'rack-groups/<int:pk>/edit/', views.RackGroupEditView.as_view(), name='rackgroup_edit'),
    path(r'rack-groups/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='rackgroup_changelog', kwargs={'model': RackGroup}),

    # Rack roles
    path(r'rack-roles/', views.RackRoleListView.as_view(), name='rackrole_list'),
    path(r'rack-roles/add/', views.RackRoleCreateView.as_view(), name='rackrole_add'),
    path(r'rack-roles/import/', views.RackRoleBulkImportView.as_view(), name='rackrole_import'),
    path(r'rack-roles/delete/', views.RackRoleBulkDeleteView.as_view(), name='rackrole_bulk_delete'),
    path(r'rack-roles/<int:pk>/edit/', views.RackRoleEditView.as_view(), name='rackrole_edit'),
    path(r'rack-roles/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='rackrole_changelog', kwargs={'model': RackRole}),

    # Rack reservations
    path(r'rack-reservations/', views.RackReservationListView.as_view(), name='rackreservation_list'),
    path(r'rack-reservations/edit/', views.RackReservationBulkEditView.as_view(), name='rackreservation_bulk_edit'),
    path(r'rack-reservations/delete/', views.RackReservationBulkDeleteView.as_view(), name='rackreservation_bulk_delete'),
    path(r'rack-reservations/<int:pk>/edit/', views.RackReservationEditView.as_view(), name='rackreservation_edit'),
    path(r'rack-reservations/<int:pk>/delete/', views.RackReservationDeleteView.as_view(), name='rackreservation_delete'),
    path(r'rack-reservations/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='rackreservation_changelog', kwargs={'model': RackReservation}),

    # Racks
    path(r'racks/', views.RackListView.as_view(), name='rack_list'),
    path(r'rack-elevations/', views.RackElevationListView.as_view(), name='rack_elevation_list'),
    path(r'racks/add/', views.RackEditView.as_view(), name='rack_add'),
    path(r'racks/import/', views.RackBulkImportView.as_view(), name='rack_import'),
    path(r'racks/edit/', views.RackBulkEditView.as_view(), name='rack_bulk_edit'),
    path(r'racks/delete/', views.RackBulkDeleteView.as_view(), name='rack_bulk_delete'),
    path(r'racks/<int:pk>/', views.RackView.as_view(), name='rack'),
    path(r'racks/<int:pk>/edit/', views.RackEditView.as_view(), name='rack_edit'),
    path(r'racks/<int:pk>/delete/', views.RackDeleteView.as_view(), name='rack_delete'),
    path(r'racks/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='rack_changelog', kwargs={'model': Rack}),
    path(r'racks/<int:rack>/reservations/add/', views.RackReservationCreateView.as_view(), name='rack_add_reservation'),
    path(r'racks/<int:object_id>/images/add/', ImageAttachmentEditView.as_view(), name='rack_add_image', kwargs={'model': Rack}),

    # Manufacturers
    path(r'manufacturers/', views.ManufacturerListView.as_view(), name='manufacturer_list'),
    path(r'manufacturers/add/', views.ManufacturerCreateView.as_view(), name='manufacturer_add'),
    path(r'manufacturers/import/', views.ManufacturerBulkImportView.as_view(), name='manufacturer_import'),
    path(r'manufacturers/delete/', views.ManufacturerBulkDeleteView.as_view(), name='manufacturer_bulk_delete'),
    path(r'manufacturers/<slug:slug>/edit/', views.ManufacturerEditView.as_view(), name='manufacturer_edit'),
    path(r'manufacturers/<slug:slug>/changelog/', ObjectChangeLogView.as_view(), name='manufacturer_changelog', kwargs={'model': Manufacturer}),

    # Device types
    path(r'device-types/', views.DeviceTypeListView.as_view(), name='devicetype_list'),
    path(r'device-types/add/', views.DeviceTypeCreateView.as_view(), name='devicetype_add'),
    # path(r'device-types/import/', views.DeviceTypeBulkImportView.as_view(), name='devicetype_import'),
    path(r'device-types/import/', views.DeviceTypeImportView.as_view(), name='devicetype_import'),
    path(r'device-types/edit/', views.DeviceTypeBulkEditView.as_view(), name='devicetype_bulk_edit'),
    path(r'device-types/delete/', views.DeviceTypeBulkDeleteView.as_view(), name='devicetype_bulk_delete'),
    path(r'device-types/<int:pk>/', views.DeviceTypeView.as_view(), name='devicetype'),
    path(r'device-types/<int:pk>/edit/', views.DeviceTypeEditView.as_view(), name='devicetype_edit'),
    path(r'device-types/<int:pk>/delete/', views.DeviceTypeDeleteView.as_view(), name='devicetype_delete'),
    path(r'device-types/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='devicetype_changelog', kwargs={'model': DeviceType}),

    # Console port templates
    path(r'device-types/<int:pk>/console-ports/add/', views.ConsolePortTemplateCreateView.as_view(), name='devicetype_add_consoleport'),
    path(r'device-types/<int:pk>/console-ports/delete/', views.ConsolePortTemplateBulkDeleteView.as_view(), name='devicetype_delete_consoleport'),

    # Console server port templates
    path(r'device-types/<int:pk>/console-server-ports/add/', views.ConsoleServerPortTemplateCreateView.as_view(), name='devicetype_add_consoleserverport'),
    path(r'device-types/<int:pk>/console-server-ports/delete/', views.ConsoleServerPortTemplateBulkDeleteView.as_view(), name='devicetype_delete_consoleserverport'),

    # Power port templates
    path(r'device-types/<int:pk>/power-ports/add/', views.PowerPortTemplateCreateView.as_view(), name='devicetype_add_powerport'),
    path(r'device-types/<int:pk>/power-ports/delete/', views.PowerPortTemplateBulkDeleteView.as_view(), name='devicetype_delete_powerport'),

    # Power outlet templates
    path(r'device-types/<int:pk>/power-outlets/add/', views.PowerOutletTemplateCreateView.as_view(), name='devicetype_add_poweroutlet'),
    path(r'device-types/<int:pk>/power-outlets/delete/', views.PowerOutletTemplateBulkDeleteView.as_view(), name='devicetype_delete_poweroutlet'),

    # Interface templates
    path(r'device-types/<int:pk>/interfaces/add/', views.InterfaceTemplateCreateView.as_view(), name='devicetype_add_interface'),
    path(r'device-types/<int:pk>/interfaces/edit/', views.InterfaceTemplateBulkEditView.as_view(), name='devicetype_bulkedit_interface'),
    path(r'device-types/<int:pk>/interfaces/delete/', views.InterfaceTemplateBulkDeleteView.as_view(), name='devicetype_delete_interface'),

    # Front port templates
    path(r'device-types/<int:pk>/front-ports/add/', views.FrontPortTemplateCreateView.as_view(), name='devicetype_add_frontport'),
    path(r'device-types/<int:pk>/front-ports/delete/', views.FrontPortTemplateBulkDeleteView.as_view(), name='devicetype_delete_frontport'),

    # Rear port templates
    path(r'device-types/<int:pk>/rear-ports/add/', views.RearPortTemplateCreateView.as_view(), name='devicetype_add_rearport'),
    path(r'device-types/<int:pk>/rear-ports/delete/', views.RearPortTemplateBulkDeleteView.as_view(), name='devicetype_delete_rearport'),

    # Device bay templates
    path(r'device-types/<int:pk>/device-bays/add/', views.DeviceBayTemplateCreateView.as_view(), name='devicetype_add_devicebay'),
    path(r'device-types/<int:pk>/device-bays/delete/', views.DeviceBayTemplateBulkDeleteView.as_view(), name='devicetype_delete_devicebay'),

    # Device roles
    path(r'device-roles/', views.DeviceRoleListView.as_view(), name='devicerole_list'),
    path(r'device-roles/add/', views.DeviceRoleCreateView.as_view(), name='devicerole_add'),
    path(r'device-roles/import/', views.DeviceRoleBulkImportView.as_view(), name='devicerole_import'),
    path(r'device-roles/delete/', views.DeviceRoleBulkDeleteView.as_view(), name='devicerole_bulk_delete'),
    path(r'device-roles/<slug:slug>/edit/', views.DeviceRoleEditView.as_view(), name='devicerole_edit'),
    path(r'device-roles/<slug:slug>/changelog/', ObjectChangeLogView.as_view(), name='devicerole_changelog', kwargs={'model': DeviceRole}),

    # Platforms
    path(r'platforms/', views.PlatformListView.as_view(), name='platform_list'),
    path(r'platforms/add/', views.PlatformCreateView.as_view(), name='platform_add'),
    path(r'platforms/import/', views.PlatformBulkImportView.as_view(), name='platform_import'),
    path(r'platforms/delete/', views.PlatformBulkDeleteView.as_view(), name='platform_bulk_delete'),
    path(r'platforms/<slug:slug>/edit/', views.PlatformEditView.as_view(), name='platform_edit'),
    path(r'platforms/<slug:slug>/changelog/', ObjectChangeLogView.as_view(), name='platform_changelog', kwargs={'model': Platform}),

    # Devices
    path(r'devices/', views.DeviceListView.as_view(), name='device_list'),
    path(r'devices/add/', views.DeviceCreateView.as_view(), name='device_add'),
    path(r'devices/import/', views.DeviceBulkImportView.as_view(), name='device_import'),
    path(r'devices/import/child-devices/', views.ChildDeviceBulkImportView.as_view(), name='device_import_child'),
    path(r'devices/edit/', views.DeviceBulkEditView.as_view(), name='device_bulk_edit'),
    path(r'devices/delete/', views.DeviceBulkDeleteView.as_view(), name='device_bulk_delete'),
    path(r'devices/<int:pk>/', views.DeviceView.as_view(), name='device'),
    path(r'devices/<int:pk>/edit/', views.DeviceEditView.as_view(), name='device_edit'),
    path(r'devices/<int:pk>/delete/', views.DeviceDeleteView.as_view(), name='device_delete'),
    path(r'devices/<int:pk>/config-context/', views.DeviceConfigContextView.as_view(), name='device_configcontext'),
    path(r'devices/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='device_changelog', kwargs={'model': Device}),
    path(r'devices/<int:pk>/inventory/', views.DeviceInventoryView.as_view(), name='device_inventory'),
    path(r'devices/<int:pk>/status/', views.DeviceStatusView.as_view(), name='device_status'),
    path(r'devices/<int:pk>/lldp-neighbors/', views.DeviceLLDPNeighborsView.as_view(), name='device_lldp_neighbors'),
    path(r'devices/<int:pk>/config/', views.DeviceConfigView.as_view(), name='device_config'),
    path(r'devices/<int:pk>/add-secret/', secret_add, name='device_addsecret'),
    path(r'devices/<int:device>/services/assign/', ServiceCreateView.as_view(), name='device_service_assign'),
    path(r'devices/<int:object_id>/images/add/', ImageAttachmentEditView.as_view(), name='device_add_image', kwargs={'model': Device}),

    # Console ports
    path(r'devices/console-ports/add/', views.DeviceBulkAddConsolePortView.as_view(), name='device_bulk_add_consoleport'),
    path(r'devices/<int:pk>/console-ports/add/', views.ConsolePortCreateView.as_view(), name='consoleport_add'),
    path(r'devices/<int:pk>/console-ports/delete/', views.ConsolePortBulkDeleteView.as_view(), name='consoleport_bulk_delete'),
    path(r'console-ports/<int:termination_a_id>/connect/<str:termination_b_type>/', views.CableCreateView.as_view(), name='consoleport_connect', kwargs={'termination_a_type': ConsolePort}),
    path(r'console-ports/<int:pk>/edit/', views.ConsolePortEditView.as_view(), name='consoleport_edit'),
    path(r'console-ports/<int:pk>/delete/', views.ConsolePortDeleteView.as_view(), name='consoleport_delete'),
    path(r'console-ports/<int:pk>/trace/', views.CableTraceView.as_view(), name='consoleport_trace', kwargs={'model': ConsolePort}),

    # Console server ports
    path(r'devices/console-server-ports/add/', views.DeviceBulkAddConsoleServerPortView.as_view(), name='device_bulk_add_consoleserverport'),
    path(r'devices/<int:pk>/console-server-ports/add/', views.ConsoleServerPortCreateView.as_view(), name='consoleserverport_add'),
    path(r'devices/<int:pk>/console-server-ports/edit/', views.ConsoleServerPortBulkEditView.as_view(), name='consoleserverport_bulk_edit'),
    path(r'devices/<int:pk>/console-server-ports/delete/', views.ConsoleServerPortBulkDeleteView.as_view(), name='consoleserverport_bulk_delete'),
    path(r'console-server-ports/<int:termination_a_id>/connect/<str:termination_b_type>/', views.CableCreateView.as_view(), name='consoleserverport_connect', kwargs={'termination_a_type': ConsoleServerPort}),
    path(r'console-server-ports/<int:pk>/edit/', views.ConsoleServerPortEditView.as_view(), name='consoleserverport_edit'),
    path(r'console-server-ports/<int:pk>/delete/', views.ConsoleServerPortDeleteView.as_view(), name='consoleserverport_delete'),
    path(r'console-server-ports/<int:pk>/trace/', views.CableTraceView.as_view(), name='consoleserverport_trace', kwargs={'model': ConsoleServerPort}),
    path(r'console-server-ports/rename/', views.ConsoleServerPortBulkRenameView.as_view(), name='consoleserverport_bulk_rename'),
    path(r'console-server-ports/disconnect/', views.ConsoleServerPortBulkDisconnectView.as_view(), name='consoleserverport_bulk_disconnect'),

    # Power ports
    path(r'devices/power-ports/add/', views.DeviceBulkAddPowerPortView.as_view(), name='device_bulk_add_powerport'),
    path(r'devices/<int:pk>/power-ports/add/', views.PowerPortCreateView.as_view(), name='powerport_add'),
    path(r'devices/<int:pk>/power-ports/delete/', views.PowerPortBulkDeleteView.as_view(), name='powerport_bulk_delete'),
    path(r'power-ports/<int:termination_a_id>/connect/<str:termination_b_type>/', views.CableCreateView.as_view(), name='powerport_connect', kwargs={'termination_a_type': PowerPort}),
    path(r'power-ports/<int:pk>/edit/', views.PowerPortEditView.as_view(), name='powerport_edit'),
    path(r'power-ports/<int:pk>/delete/', views.PowerPortDeleteView.as_view(), name='powerport_delete'),
    path(r'power-ports/<int:pk>/trace/', views.CableTraceView.as_view(), name='powerport_trace', kwargs={'model': PowerPort}),

    # Power outlets
    path(r'devices/power-outlets/add/', views.DeviceBulkAddPowerOutletView.as_view(), name='device_bulk_add_poweroutlet'),
    path(r'devices/<int:pk>/power-outlets/add/', views.PowerOutletCreateView.as_view(), name='poweroutlet_add'),
    path(r'devices/<int:pk>/power-outlets/edit/', views.PowerOutletBulkEditView.as_view(), name='poweroutlet_bulk_edit'),
    path(r'devices/<int:pk>/power-outlets/delete/', views.PowerOutletBulkDeleteView.as_view(), name='poweroutlet_bulk_delete'),
    path(r'power-outlets/<int:termination_a_id>/connect/<str:termination_b_type>/', views.CableCreateView.as_view(), name='poweroutlet_connect', kwargs={'termination_a_type': PowerOutlet}),
    path(r'power-outlets/<int:pk>/edit/', views.PowerOutletEditView.as_view(), name='poweroutlet_edit'),
    path(r'power-outlets/<int:pk>/delete/', views.PowerOutletDeleteView.as_view(), name='poweroutlet_delete'),
    path(r'power-outlets/<int:pk>/trace/', views.CableTraceView.as_view(), name='poweroutlet_trace', kwargs={'model': PowerOutlet}),
    path(r'power-outlets/rename/', views.PowerOutletBulkRenameView.as_view(), name='poweroutlet_bulk_rename'),
    path(r'power-outlets/disconnect/', views.PowerOutletBulkDisconnectView.as_view(), name='poweroutlet_bulk_disconnect'),

    # Interfaces
    path(r'devices/interfaces/add/', views.DeviceBulkAddInterfaceView.as_view(), name='device_bulk_add_interface'),
    path(r'devices/<int:pk>/interfaces/add/', views.InterfaceCreateView.as_view(), name='interface_add'),
    path(r'devices/<int:pk>/interfaces/edit/', views.InterfaceBulkEditView.as_view(), name='interface_bulk_edit'),
    path(r'devices/<int:pk>/interfaces/delete/', views.InterfaceBulkDeleteView.as_view(), name='interface_bulk_delete'),
    path(r'interfaces/<int:termination_a_id>/connect/<str:termination_b_type>/', views.CableCreateView.as_view(), name='interface_connect', kwargs={'termination_a_type': Interface}),
    path(r'interfaces/<int:pk>/', views.InterfaceView.as_view(), name='interface'),
    path(r'interfaces/<int:pk>/edit/', views.InterfaceEditView.as_view(), name='interface_edit'),
    path(r'interfaces/<int:pk>/delete/', views.InterfaceDeleteView.as_view(), name='interface_delete'),
    path(r'interfaces/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='interface_changelog', kwargs={'model': Interface}),
    path(r'interfaces/<int:pk>/trace/', views.CableTraceView.as_view(), name='interface_trace', kwargs={'model': Interface}),
    path(r'interfaces/rename/', views.InterfaceBulkRenameView.as_view(), name='interface_bulk_rename'),
    path(r'interfaces/disconnect/', views.InterfaceBulkDisconnectView.as_view(), name='interface_bulk_disconnect'),

    # Front ports
    # path(r'devices/front-ports/add/', views.DeviceBulkAddFrontPortView.as_view(), name='device_bulk_add_frontport'),
    path(r'devices/<int:pk>/front-ports/add/', views.FrontPortCreateView.as_view(), name='frontport_add'),
    path(r'devices/<int:pk>/front-ports/edit/', views.FrontPortBulkEditView.as_view(), name='frontport_bulk_edit'),
    path(r'devices/<int:pk>/front-ports/delete/', views.FrontPortBulkDeleteView.as_view(), name='frontport_bulk_delete'),
    path(r'front-ports/<int:termination_a_id>/connect/<str:termination_b_type>/', views.CableCreateView.as_view(), name='frontport_connect', kwargs={'termination_a_type': FrontPort}),
    path(r'front-ports/<int:pk>/edit/', views.FrontPortEditView.as_view(), name='frontport_edit'),
    path(r'front-ports/<int:pk>/delete/', views.FrontPortDeleteView.as_view(), name='frontport_delete'),
    path(r'front-ports/<int:pk>/trace/', views.CableTraceView.as_view(), name='frontport_trace', kwargs={'model': FrontPort}),
    path(r'front-ports/rename/', views.FrontPortBulkRenameView.as_view(), name='frontport_bulk_rename'),
    path(r'front-ports/disconnect/', views.FrontPortBulkDisconnectView.as_view(), name='frontport_bulk_disconnect'),

    # Rear ports
    # path(r'devices/rear-ports/add/', views.DeviceBulkAddRearPortView.as_view(), name='device_bulk_add_rearport'),
    path(r'devices/<int:pk>/rear-ports/add/', views.RearPortCreateView.as_view(), name='rearport_add'),
    path(r'devices/<int:pk>/rear-ports/edit/', views.RearPortBulkEditView.as_view(), name='rearport_bulk_edit'),
    path(r'devices/<int:pk>/rear-ports/delete/', views.RearPortBulkDeleteView.as_view(), name='rearport_bulk_delete'),
    path(r'rear-ports/<int:termination_a_id>/connect/<str:termination_b_type>/', views.CableCreateView.as_view(), name='rearport_connect', kwargs={'termination_a_type': RearPort}),
    path(r'rear-ports/<int:pk>/edit/', views.RearPortEditView.as_view(), name='rearport_edit'),
    path(r'rear-ports/<int:pk>/delete/', views.RearPortDeleteView.as_view(), name='rearport_delete'),
    path(r'rear-ports/<int:pk>/trace/', views.CableTraceView.as_view(), name='rearport_trace', kwargs={'model': RearPort}),
    path(r'rear-ports/rename/', views.RearPortBulkRenameView.as_view(), name='rearport_bulk_rename'),
    path(r'rear-ports/disconnect/', views.RearPortBulkDisconnectView.as_view(), name='rearport_bulk_disconnect'),

    # Device bays
    path(r'devices/device-bays/add/', views.DeviceBulkAddDeviceBayView.as_view(), name='device_bulk_add_devicebay'),
    path(r'devices/<int:pk>/bays/add/', views.DeviceBayCreateView.as_view(), name='devicebay_add'),
    path(r'devices/<int:pk>/bays/delete/', views.DeviceBayBulkDeleteView.as_view(), name='devicebay_bulk_delete'),
    path(r'device-bays/<int:pk>/edit/', views.DeviceBayEditView.as_view(), name='devicebay_edit'),
    path(r'device-bays/<int:pk>/delete/', views.DeviceBayDeleteView.as_view(), name='devicebay_delete'),
    path(r'device-bays/<int:pk>/populate/', views.DeviceBayPopulateView.as_view(), name='devicebay_populate'),
    path(r'device-bays/<int:pk>/depopulate/', views.DeviceBayDepopulateView.as_view(), name='devicebay_depopulate'),
    path(r'device-bays/rename/', views.DeviceBayBulkRenameView.as_view(), name='devicebay_bulk_rename'),

    # Inventory items
    path(r'inventory-items/', views.InventoryItemListView.as_view(), name='inventoryitem_list'),
    path(r'inventory-items/import/', views.InventoryItemBulkImportView.as_view(), name='inventoryitem_import'),
    path(r'inventory-items/edit/', views.InventoryItemBulkEditView.as_view(), name='inventoryitem_bulk_edit'),
    path(r'inventory-items/delete/', views.InventoryItemBulkDeleteView.as_view(), name='inventoryitem_bulk_delete'),
    path(r'inventory-items/<int:pk>/edit/', views.InventoryItemEditView.as_view(), name='inventoryitem_edit'),
    path(r'inventory-items/<int:pk>/delete/', views.InventoryItemDeleteView.as_view(), name='inventoryitem_delete'),
    path(r'devices/<int:device>/inventory-items/add/', views.InventoryItemEditView.as_view(), name='inventoryitem_add'),

    # Cables
    path(r'cables/', views.CableListView.as_view(), name='cable_list'),
    path(r'cables/import/', views.CableBulkImportView.as_view(), name='cable_import'),
    path(r'cables/edit/', views.CableBulkEditView.as_view(), name='cable_bulk_edit'),
    path(r'cables/delete/', views.CableBulkDeleteView.as_view(), name='cable_bulk_delete'),
    path(r'cables/<int:pk>/', views.CableView.as_view(), name='cable'),
    path(r'cables/<int:pk>/edit/', views.CableEditView.as_view(), name='cable_edit'),
    path(r'cables/<int:pk>/delete/', views.CableDeleteView.as_view(), name='cable_delete'),
    path(r'cables/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='cable_changelog', kwargs={'model': Cable}),

    # Console/power/interface connections (read-only)
    path(r'console-connections/', views.ConsoleConnectionsListView.as_view(), name='console_connections_list'),
    path(r'power-connections/', views.PowerConnectionsListView.as_view(), name='power_connections_list'),
    path(r'interface-connections/', views.InterfaceConnectionsListView.as_view(), name='interface_connections_list'),

    # Virtual chassis
    path(r'virtual-chassis/', views.VirtualChassisListView.as_view(), name='virtualchassis_list'),
    path(r'virtual-chassis/add/', views.VirtualChassisCreateView.as_view(), name='virtualchassis_add'),
    path(r'virtual-chassis/<int:pk>/edit/', views.VirtualChassisEditView.as_view(), name='virtualchassis_edit'),
    path(r'virtual-chassis/<int:pk>/delete/', views.VirtualChassisDeleteView.as_view(), name='virtualchassis_delete'),
    path(r'virtual-chassis/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='virtualchassis_changelog', kwargs={'model': VirtualChassis}),
    path(r'virtual-chassis/<int:pk>/add-member/', views.VirtualChassisAddMemberView.as_view(), name='virtualchassis_add_member'),
    path(r'virtual-chassis-members/<int:pk>/delete/', views.VirtualChassisRemoveMemberView.as_view(), name='virtualchassis_remove_member'),

    # Power panels
    path(r'power-panels/', views.PowerPanelListView.as_view(), name='powerpanel_list'),
    path(r'power-panels/add/', views.PowerPanelCreateView.as_view(), name='powerpanel_add'),
    path(r'power-panels/import/', views.PowerPanelBulkImportView.as_view(), name='powerpanel_import'),
    path(r'power-panels/delete/', views.PowerPanelBulkDeleteView.as_view(), name='powerpanel_bulk_delete'),
    path(r'power-panels/<int:pk>/', views.PowerPanelView.as_view(), name='powerpanel'),
    path(r'power-panels/<int:pk>/edit/', views.PowerPanelEditView.as_view(), name='powerpanel_edit'),
    path(r'power-panels/<int:pk>/delete/', views.PowerPanelDeleteView.as_view(), name='powerpanel_delete'),
    path(r'power-panels/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='powerpanel_changelog', kwargs={'model': PowerPanel}),

    # Power feeds
    path(r'power-feeds/', views.PowerFeedListView.as_view(), name='powerfeed_list'),
    path(r'power-feeds/add/', views.PowerFeedEditView.as_view(), name='powerfeed_add'),
    path(r'power-feeds/import/', views.PowerFeedBulkImportView.as_view(), name='powerfeed_import'),
    path(r'power-feeds/edit/', views.PowerFeedBulkEditView.as_view(), name='powerfeed_bulk_edit'),
    path(r'power-feeds/delete/', views.PowerFeedBulkDeleteView.as_view(), name='powerfeed_bulk_delete'),
    path(r'power-feeds/<int:pk>/', views.PowerFeedView.as_view(), name='powerfeed'),
    path(r'power-feeds/<int:pk>/edit/', views.PowerFeedEditView.as_view(), name='powerfeed_edit'),
    path(r'power-feeds/<int:pk>/delete/', views.PowerFeedDeleteView.as_view(), name='powerfeed_delete'),
    path(r'power-feeds/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='powerfeed_changelog', kwargs={'model': PowerFeed}),

]
