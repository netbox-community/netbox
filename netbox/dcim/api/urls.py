from __future__ import unicode_literals

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
router.register(r'_choices', views.DCIMFieldChoicesViewSet, base_name='field-choice')

# Sites
router.register(r'regions', views.RegionViewSet)
router.register(r'sites', views.SiteViewSet)

# Racks
router.register(r'rack-groups', views.RackGroupViewSet)
router.register(r'rack-roles', views.RackRoleViewSet)
router.register(r'racks', views.RackViewSet)
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
router.register(r'device-bays', views.DeviceBayViewSet)
router.register(r'inventory-items', views.InventoryItemViewSet)

# Connections
router.register(r'console-connections', views.ConsoleConnectionViewSet, base_name='consoleconnections')
router.register(r'power-connections', views.PowerConnectionViewSet, base_name='powerconnections')
router.register(r'interface-connections', views.InterfaceConnectionViewSet)

# Virtual chassis
router.register(r'virtual-chassis', views.VirtualChassisViewSet)

# Miscellaneous
router.register(r'connected-device', views.ConnectedDeviceViewSet, base_name='connected-device')

app_name = 'dcim-api'
urlpatterns = router.urls
