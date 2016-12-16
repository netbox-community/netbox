from django.conf.urls import url

from ipam.views import ServiceEditView
from secrets.views import secret_add

from . import views


urlpatterns = [

    # Sites
    url(r'^sites/$', views.SiteListView.as_view(), name='site_list'),
    url(r'^sites/add/$', views.SiteEditView.as_view(), name='site_add'),
    url(r'^sites/import/$', views.SiteBulkImportView.as_view(), name='site_import'),
    url(r'^sites/edit/$', views.SiteBulkEditView.as_view(), name='site_bulk_edit'),
    url(r'^sites/(?P<slug>[\w-]+)/$', views.site, name='site'),
    url(r'^sites/(?P<slug>[\w-]+)/edit/$', views.SiteEditView.as_view(), name='site_edit'),
    url(r'^sites/(?P<slug>[\w-]+)/delete/$', views.SiteDeleteView.as_view(), name='site_delete'),

    # Rack groups
    url(r'^rack-groups/$', views.RackGroupListView.as_view(), name='rackgroup_list'),
    url(r'^rack-groups/add/$', views.RackGroupEditView.as_view(), name='rackgroup_add'),
    url(r'^rack-groups/delete/$', views.RackGroupBulkDeleteView.as_view(), name='rackgroup_bulk_delete'),
    url(r'^rack-groups/(?P<pk>\d+)/edit/$', views.RackGroupEditView.as_view(), name='rackgroup_edit'),

    # Rack roles
    url(r'^rack-roles/$', views.RackRoleListView.as_view(), name='rackrole_list'),
    url(r'^rack-roles/add/$', views.RackRoleEditView.as_view(), name='rackrole_add'),
    url(r'^rack-roles/delete/$', views.RackRoleBulkDeleteView.as_view(), name='rackrole_bulk_delete'),
    url(r'^rack-roles/(?P<pk>\d+)/edit/$', views.RackRoleEditView.as_view(), name='rackrole_edit'),

    # Racks
    url(r'^racks/$', views.RackListView.as_view(), name='rack_list'),
    url(r'^racks/add/$', views.RackEditView.as_view(), name='rack_add'),
    url(r'^racks/import/$', views.RackBulkImportView.as_view(), name='rack_import'),
    url(r'^racks/edit/$', views.RackBulkEditView.as_view(), name='rack_bulk_edit'),
    url(r'^racks/delete/$', views.RackBulkDeleteView.as_view(), name='rack_bulk_delete'),
    url(r'^racks/(?P<pk>\d+)/$', views.rack, name='rack'),
    url(r'^racks/(?P<pk>\d+)/edit/$', views.RackEditView.as_view(), name='rack_edit'),
    url(r'^racks/(?P<pk>\d+)/delete/$', views.RackDeleteView.as_view(), name='rack_delete'),

    # Manufacturers
    url(r'^manufacturers/$', views.ManufacturerListView.as_view(), name='manufacturer_list'),
    url(r'^manufacturers/add/$', views.ManufacturerEditView.as_view(), name='manufacturer_add'),
    url(r'^manufacturers/delete/$', views.ManufacturerBulkDeleteView.as_view(), name='manufacturer_bulk_delete'),
    url(r'^manufacturers/(?P<slug>[\w-]+)/edit/$', views.ManufacturerEditView.as_view(), name='manufacturer_edit'),

    # Device types
    url(r'^device-types/$', views.DeviceTypeListView.as_view(), name='devicetype_list'),
    url(r'^device-types/add/$', views.DeviceTypeEditView.as_view(), name='devicetype_add'),
    url(r'^device-types/edit/$', views.DeviceTypeBulkEditView.as_view(), name='devicetype_bulk_edit'),
    url(r'^device-types/delete/$', views.DeviceTypeBulkDeleteView.as_view(), name='devicetype_bulk_delete'),
    url(r'^device-types/(?P<pk>\d+)/$', views.devicetype, name='devicetype'),
    url(r'^device-types/(?P<pk>\d+)/edit/$', views.DeviceTypeEditView.as_view(), name='devicetype_edit'),
    url(r'^device-types/(?P<pk>\d+)/delete/$', views.DeviceTypeDeleteView.as_view(), name='devicetype_delete'),

    # Console port templates
    url(r'^device-types/(?P<pk>\d+)/console-ports/add/$', views.ConsolePortTemplateAddView.as_view(), name='devicetype_add_consoleport'),
    url(r'^device-types/(?P<pk>\d+)/console-ports/delete/$', views.ConsolePortTemplateBulkDeleteView.as_view(), name='devicetype_delete_consoleport'),

    # Console server port templates
    url(r'^device-types/(?P<pk>\d+)/console-server-ports/add/$', views.ConsoleServerPortTemplateAddView.as_view(), name='devicetype_add_consoleserverport'),
    url(r'^device-types/(?P<pk>\d+)/console-server-ports/delete/$', views.ConsoleServerPortTemplateBulkDeleteView.as_view(), name='devicetype_delete_consoleserverport'),

    # Power port templates
    url(r'^device-types/(?P<pk>\d+)/power-ports/add/$', views.PowerPortTemplateAddView.as_view(), name='devicetype_add_powerport'),
    url(r'^device-types/(?P<pk>\d+)/power-ports/delete/$', views.PowerPortTemplateBulkDeleteView.as_view(), name='devicetype_delete_powerport'),

    # Power outlet templates
    url(r'^device-types/(?P<pk>\d+)/power-outlets/add/$', views.PowerOutletTemplateAddView.as_view(), name='devicetype_add_poweroutlet'),
    url(r'^device-types/(?P<pk>\d+)/power-outlets/delete/$', views.PowerOutletTemplateBulkDeleteView.as_view(), name='devicetype_delete_poweroutlet'),

    # Interface templates
    url(r'^device-types/(?P<pk>\d+)/interfaces/add/$', views.InterfaceTemplateAddView.as_view(), name='devicetype_add_interface'),
    url(r'^device-types/(?P<pk>\d+)/interfaces/edit/$', views.InterfaceTemplateBulkEditView.as_view(), name='devicetype_bulkedit_interface'),
    url(r'^device-types/(?P<pk>\d+)/interfaces/delete/$', views.InterfaceTemplateBulkDeleteView.as_view(), name='devicetype_delete_interface'),

    # Device bay templates
    url(r'^device-types/(?P<pk>\d+)/device-bays/add/$', views.DeviceBayTemplateAddView.as_view(), name='devicetype_add_devicebay'),
    url(r'^device-types/(?P<pk>\d+)/device-bays/delete/$', views.DeviceBayTemplateBulkDeleteView.as_view(), name='devicetype_delete_devicebay'),

    # Device roles
    url(r'^device-roles/$', views.DeviceRoleListView.as_view(), name='devicerole_list'),
    url(r'^device-roles/add/$', views.DeviceRoleEditView.as_view(), name='devicerole_add'),
    url(r'^device-roles/delete/$', views.DeviceRoleBulkDeleteView.as_view(), name='devicerole_bulk_delete'),
    url(r'^device-roles/(?P<slug>[\w-]+)/edit/$', views.DeviceRoleEditView.as_view(), name='devicerole_edit'),

    # Platforms
    url(r'^platforms/$', views.PlatformListView.as_view(), name='platform_list'),
    url(r'^platforms/add/$', views.PlatformEditView.as_view(), name='platform_add'),
    url(r'^platforms/delete/$', views.PlatformBulkDeleteView.as_view(), name='platform_bulk_delete'),
    url(r'^platforms/(?P<slug>[\w-]+)/edit/$', views.PlatformEditView.as_view(), name='platform_edit'),

    # Devices
    url(r'^devices/$', views.DeviceListView.as_view(), name='device_list'),
    url(r'^devices/add/$', views.DeviceEditView.as_view(), name='device_add'),
    url(r'^devices/import/$', views.DeviceBulkImportView.as_view(), name='device_import'),
    url(r'^devices/import/child-devices/$', views.ChildDeviceBulkImportView.as_view(), name='device_import_child'),
    url(r'^devices/edit/$', views.DeviceBulkEditView.as_view(), name='device_bulk_edit'),
    url(r'^devices/delete/$', views.DeviceBulkDeleteView.as_view(), name='device_bulk_delete'),
    url(r'^devices/(?P<pk>\d+)/$', views.device, name='device'),
    url(r'^devices/(?P<pk>\d+)/edit/$', views.DeviceEditView.as_view(), name='device_edit'),
    url(r'^devices/(?P<pk>\d+)/delete/$', views.DeviceDeleteView.as_view(), name='device_delete'),
    url(r'^devices/(?P<pk>\d+)/inventory/$', views.device_inventory, name='device_inventory'),
    url(r'^devices/(?P<pk>\d+)/lldp-neighbors/$', views.device_lldp_neighbors, name='device_lldp_neighbors'),
    url(r'^devices/(?P<pk>\d+)/ip-addresses/assign/$', views.ipaddress_assign, name='ipaddress_assign'),
    url(r'^devices/(?P<pk>\d+)/add-secret/$', secret_add, name='device_addsecret'),
    url(r'^devices/(?P<device>\d+)/services/assign/$', ServiceEditView.as_view(), name='service_assign'),

    # Console ports
    url(r'^devices/(?P<pk>\d+)/console-ports/add/$', views.consoleport_add, name='consoleport_add'),
    url(r'^devices/(?P<pk>\d+)/console-ports/delete/$', views.ConsolePortBulkDeleteView.as_view(), name='consoleport_bulk_delete'),
    url(r'^console-ports/(?P<pk>\d+)/connect/$', views.consoleport_connect, name='consoleport_connect'),
    url(r'^console-ports/(?P<pk>\d+)/disconnect/$', views.consoleport_disconnect, name='consoleport_disconnect'),
    url(r'^console-ports/(?P<pk>\d+)/edit/$', views.ConsolePortEditView.as_view(), name='consoleport_edit'),
    url(r'^console-ports/(?P<pk>\d+)/delete/$', views.ConsolePortDeleteView.as_view(), name='consoleport_delete'),

    # Console server ports
    url(r'^devices/(?P<pk>\d+)/console-server-ports/add/$', views.consoleserverport_add, name='consoleserverport_add'),
    url(r'^devices/(?P<pk>\d+)/console-server-ports/delete/$', views.ConsoleServerPortBulkDeleteView.as_view(), name='consoleserverport_bulk_delete'),
    url(r'^console-server-ports/(?P<pk>\d+)/connect/$', views.consoleserverport_connect, name='consoleserverport_connect'),
    url(r'^console-server-ports/(?P<pk>\d+)/disconnect/$', views.consoleserverport_disconnect, name='consoleserverport_disconnect'),
    url(r'^console-server-ports/(?P<pk>\d+)/edit/$', views.ConsoleServerPortEditView.as_view(), name='consoleserverport_edit'),
    url(r'^console-server-ports/(?P<pk>\d+)/delete/$', views.ConsoleServerPortDeleteView.as_view(), name='consoleserverport_delete'),

    # Power ports
    url(r'^devices/(?P<pk>\d+)/power-ports/add/$', views.powerport_add, name='powerport_add'),
    url(r'^devices/(?P<pk>\d+)/power-ports/delete/$', views.PowerPortBulkDeleteView.as_view(), name='powerport_bulk_delete'),
    url(r'^power-ports/(?P<pk>\d+)/connect/$', views.powerport_connect, name='powerport_connect'),
    url(r'^power-ports/(?P<pk>\d+)/disconnect/$', views.powerport_disconnect, name='powerport_disconnect'),
    url(r'^power-ports/(?P<pk>\d+)/edit/$', views.PowerPortEditView.as_view(), name='powerport_edit'),
    url(r'^power-ports/(?P<pk>\d+)/delete/$', views.PowerPortDeleteView.as_view(), name='powerport_delete'),

    # Power outlets
    url(r'^devices/(?P<pk>\d+)/power-outlets/add/$', views.poweroutlet_add, name='poweroutlet_add'),
    url(r'^devices/(?P<pk>\d+)/power-outlets/delete/$', views.PowerOutletBulkDeleteView.as_view(), name='poweroutlet_bulk_delete'),
    url(r'^power-outlets/(?P<pk>\d+)/connect/$', views.poweroutlet_connect, name='poweroutlet_connect'),
    url(r'^power-outlets/(?P<pk>\d+)/disconnect/$', views.poweroutlet_disconnect, name='poweroutlet_disconnect'),
    url(r'^power-outlets/(?P<pk>\d+)/edit/$', views.PowerOutletEditView.as_view(), name='poweroutlet_edit'),
    url(r'^power-outlets/(?P<pk>\d+)/delete/$', views.PowerOutletDeleteView.as_view(), name='poweroutlet_delete'),

    # Device bays
    url(r'^devices/(?P<pk>\d+)/bays/add/$', views.devicebay_add, name='devicebay_add'),
    url(r'^devices/(?P<pk>\d+)/bays/delete/$', views.DeviceBayBulkDeleteView.as_view(), name='devicebay_bulk_delete'),
    url(r'^device-bays/(?P<pk>\d+)/edit/$', views.DeviceBayEditView.as_view(), name='devicebay_edit'),
    url(r'^device-bays/(?P<pk>\d+)/delete/$', views.DeviceBayDeleteView.as_view(), name='devicebay_delete'),
    url(r'^device-bays/(?P<pk>\d+)/populate/$', views.devicebay_populate, name='devicebay_populate'),
    url(r'^device-bays/(?P<pk>\d+)/depopulate/$', views.devicebay_depopulate, name='devicebay_depopulate'),

    # Console/power/interface connections
    url(r'^console-connections/$', views.ConsoleConnectionsListView.as_view(), name='console_connections_list'),
    url(r'^console-connections/import/$', views.ConsoleConnectionsBulkImportView.as_view(), name='console_connections_import'),
    url(r'^power-connections/$', views.PowerConnectionsListView.as_view(), name='power_connections_list'),
    url(r'^power-connections/import/$', views.PowerConnectionsBulkImportView.as_view(), name='power_connections_import'),
    url(r'^interface-connections/$', views.InterfaceConnectionsListView.as_view(), name='interface_connections_list'),
    url(r'^interface-connections/import/$', views.InterfaceConnectionsBulkImportView.as_view(), name='interface_connections_import'),

    # Interfaces
    url(r'^devices/interfaces/add/$', views.DeviceBulkAddInterfaceView.as_view(), name='device_bulk_add_interface'),
    url(r'^devices/(?P<pk>\d+)/interfaces/add/$', views.interface_add, name='interface_add'),
    url(r'^devices/(?P<pk>\d+)/interfaces/edit/$', views.InterfaceBulkEditView.as_view(), name='interface_bulk_edit'),
    url(r'^devices/(?P<pk>\d+)/interfaces/delete/$', views.InterfaceBulkDeleteView.as_view(), name='interface_bulk_delete'),
    url(r'^devices/(?P<pk>\d+)/interface-connections/add/$', views.interfaceconnection_add, name='interfaceconnection_add'),
    url(r'^interface-connections/(?P<pk>\d+)/delete/$', views.interfaceconnection_delete, name='interfaceconnection_delete'),
    url(r'^interfaces/(?P<pk>\d+)/edit/$', views.InterfaceEditView.as_view(), name='interface_edit'),
    url(r'^interfaces/(?P<pk>\d+)/delete/$', views.InterfaceDeleteView.as_view(), name='interface_delete'),

    # Modules
    url(r'^devices/(?P<device>\d+)/modules/add/$', views.ModuleEditView.as_view(), name='module_add'),
    url(r'^modules/(?P<pk>\d+)/edit/$', views.ModuleEditView.as_view(), name='module_edit'),
    url(r'^modules/(?P<pk>\d+)/delete/$', views.ModuleDeleteView.as_view(), name='module_delete'),

]
