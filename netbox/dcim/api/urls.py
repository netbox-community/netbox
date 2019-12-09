from rest_framework import routers

from . import views


class DCIMRootView(routers.APIRootView):
    """
    DCIM API root view
    """
    def get_view_name(self):
        return 'DCIM'


router = routers.DefaultRouter()
router.APIRootView = DCIMRootView

# Field choices
router.register(r'_choices', views.DCIMFieldChoicesViewSet, basename='field-choice')

# Sites
router.register(r'regions', views.RegionViewSet)
router.register(r'sites', views.SiteViewSet)

# Racks
router.register(r'rack-groups', views.RackGroupViewSet)
router.register(r'rack-roles', views.RackRoleViewSet)
router.register(r'racks', views.RackViewSet)
router.register(r'rack-elevations', views.RackElevationViewSet, basename='rack-elevation')
router.register(r'rack-reservations', views.RackReservationViewSet)

# Device types
router.register(r'manufacturers', views.ManufacturerViewSet)
router.register(r'device-types', views.DeviceTypeViewSet)

# Device type components
router.register(r'console-port-templates', views.ConsolePortTemplateViewSet)
router.register(r'console-server-port-templates', views.ConsoleServerPortTemplateViewSet)
router.register(r'power-port-templates', views.PowerPortTemplateViewSet)
router.register(r'power-outlet-templates', views.PowerOutletTemplateViewSet)
router.register(r'interface-templates', views.InterfaceTemplateViewSet)
router.register(r'front-port-templates', views.FrontPortTemplateViewSet)
router.register(r'rear-port-templates', views.RearPortTemplateViewSet)
router.register(r'device-bay-templates', views.DeviceBayTemplateViewSet)

# Devices
router.register(r'device-roles', views.DeviceRoleViewSet)
router.register(r'platforms', views.PlatformViewSet)
router.register(r'devices', views.DeviceViewSet)

# Device components
router.register(r'console-ports', views.ConsolePortViewSet)
router.register(r'console-server-ports', views.ConsoleServerPortViewSet)
router.register(r'power-ports', views.PowerPortViewSet)
router.register(r'power-outlets', views.PowerOutletViewSet)
router.register(r'interfaces', views.InterfaceViewSet)
router.register(r'front-ports', views.FrontPortViewSet)
router.register(r'rear-ports', views.RearPortViewSet)
router.register(r'device-bays', views.DeviceBayViewSet)
router.register(r'inventory-items', views.InventoryItemViewSet)

# Connections
router.register(r'console-connections', views.ConsoleConnectionViewSet, basename='consoleconnections')
router.register(r'power-connections', views.PowerConnectionViewSet, basename='powerconnections')
router.register(r'interface-connections', views.InterfaceConnectionViewSet, basename='interfaceconnections')

# Cables
router.register(r'cables', views.CableViewSet)

# Virtual chassis
router.register(r'virtual-chassis', views.VirtualChassisViewSet)

# Power
router.register(r'power-panels', views.PowerPanelViewSet)
router.register(r'power-feeds', views.PowerFeedViewSet)

# Miscellaneous
router.register(r'connected-device', views.ConnectedDeviceViewSet, basename='connected-device')

app_name = 'dcim-api'
urlpatterns = router.urls
