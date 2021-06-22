from dataclasses import dataclass
from typing import Dict, Sequence, Optional
from django import template
from django.template import Context
from django.contrib.auth.context_processors import PermWrapper

register = template.Library()


@dataclass
class MenuItem:
    """A navigation menu item link. Example: Sites, Platforms, RIRs, etc."""

    label: str
    url: str
    disabled: bool = True
    add_url: Optional[str] = None
    import_url: Optional[str] = None
    has_add: bool = False
    has_import: bool = False


@dataclass
class MenuGroup:
    """A group of menu items within a menu."""

    label: str
    items: Sequence[MenuItem]


@dataclass
class Menu:
    """A top level menu group. Example: Organization, Devices, IPAM."""

    label: str
    icon: str
    groups: Sequence[MenuGroup]


ORGANIZATION_MENU = Menu(
    label="Organization",
    icon="domain",
    groups=(
        MenuGroup(
            label="Sites",
            items=(
                MenuItem(label="Sites", url="dcim:site_list",
                         add_url="dcim:site_add", import_url="dcim:site_import"),
                MenuItem(label="Site Groups", url="dcim:sitegroup_list",
                         add_url="dcim:sitegroup_add", import_url="dcim:sitegroup_import"),
                MenuItem(label="Regions", url="dcim:region_list",
                         add_url="dcim:region_add", import_url="dcim:region_import"),
                MenuItem(label="Locations", url="dcim:location_list",
                         add_url="dcim:location_add", import_url="dcim:location_import"),
            ),
        ),
        MenuGroup(
            label="Racks",
            items=(
                MenuItem(label="Racks", url="dcim:rack_list",
                         add_url="dcim:rack_add", import_url="dcim:rack_import"),
                MenuItem(label="Rack Roles", url="dcim:rackrole_list",
                         add_url="dcim:rackrole_add", import_url="dcim:rackrole_import"),
                MenuItem(label="Elevations", url="dcim:rack_elevation_list",
                         add_url=None, import_url=None),
            ),
        ),
        MenuGroup(
            label="Tenancy",
            items=(
                MenuItem(label="Tenants", url="tenancy:tenant_list",
                         add_url="tenancy:tenant_add", import_url="tenancy:tenant_import"),
                MenuItem(label="Tenant Groups",
                         url="tenancy:tenantgroup_list", add_url="tenancy:tenantgroup_add",
                         import_url="tenancy:tenantgroup_import"),
            ),
        ),
        MenuGroup(
            label="Tags",
            items=(MenuItem(label="Tags", url="extras:tag_list",
                   add_url="extras:tag_add", import_url="extras:tag_import"),),
        ),
    ),
)

DEVICES_MENU = Menu(
    label="Devices",
    icon="server",
    groups=(
        MenuGroup(
            label="Devices",
            items=(
                MenuItem(label="Devices", url="dcim:device_list",
                         add_url="dcim:device_add", import_url="dcim:device_import"),
                MenuItem(label="Device Roles", url="dcim:devicerole_list",
                         add_url="dcim:devicerole_add", import_url="dcim:devicerole_import"),
                MenuItem(label="Platforms", url="dcim:platform_list",
                         add_url="dcim:platform_add", import_url="dcim:platform_import"),
                MenuItem(label="Virtual Chassis",
                         url="dcim:virtualchassis_list", add_url="dcim:virtualchassis_add",
                         import_url="dcim:virtualchassis_import"),
            ),
        ),
        MenuGroup(
            label="Device Types",
            items=(
                MenuItem(label="Device Types", url="dcim:devicetype_list",
                         add_url="dcim:devicetype_add", import_url="dcim:devicetype_import"),
                MenuItem(label="Manufacturers", url="dcim:manufacturer_list",
                         add_url="dcim:manufacturer_add", import_url="dcim:manufacturer_import"),
            ),
        ),
        MenuGroup(
            label="Connections",
            items=(
                MenuItem(label="Cables", url="dcim:cable_list",
                         add_url=None, import_url="dcim:cable_import"),
                MenuItem(
                    label="Console Connections", url="dcim:console_connections_list", add_url=None, import_url=None,
                ),
                MenuItem(
                    label="Interface Connections", url="dcim:interface_connections_list", add_url=None, import_url=None,
                ),
                MenuItem(label="Power Connections",
                         url="dcim:power_connections_list", add_url=None, import_url=None,),
            ),
        ),
        MenuGroup(
            label="Device Components",
            items=(
                MenuItem(label="Interfaces", url="dcim:interface_list",
                         add_url=None, import_url="dcim:interface_import"),
                MenuItem(label="Front Ports", url="dcim:frontport_list",
                         add_url=None, import_url="dcim:frontport_import"),
                MenuItem(label="Rear Ports", url="dcim:rearport_list",
                         add_url=None, import_url="dcim:rearport_import"),
                MenuItem(label="Console Ports", url="dcim:consoleport_list",
                         add_url=None, import_url="dcim:consoleport_import"),
                MenuItem(label="Console Server Ports", url="dcim:consoleserverport_list",
                         add_url=None, import_url="dcim:consoleserverport_import"),
                MenuItem(label="Power Ports", url="dcim:powerport_list",
                         add_url=None, import_url="dcim:powerport_import"),
                MenuItem(label="Power Outlets", url="dcim:poweroutlet_list",
                         add_url=None, import_url="dcim:poweroutlet_import"),
                MenuItem(label="Device Bays", url="dcim:devicebay_list",
                         add_url=None, import_url="dcim:devicebay_import"),
                MenuItem(label="Inventory Items",
                         url="dcim:inventoryitem_list", add_url=None, import_url="dcim:inventoryitem_import"),
            ),
        ),
    ),
)

IPAM_MENU = Menu(
    label="IPAM",
    icon="counter",
    groups=(
        MenuGroup(
            label="IP Addresses",
            items=(
                MenuItem(label="IP Addresses", url="ipam:ipaddress_list",
                         add_url="ipam:ipaddress_add", import_url="ipam:ipaddress_import"),
            ),
        ),
        MenuGroup(
            label="Prefixes",
            items=(
                MenuItem(label="Prefixes", url="ipam:prefix_list",
                         add_url="ipam:prefix_add", import_url="ipam:prefix_import"),
                MenuItem(label="Prefix & VLAN Roles", url="ipam:role_list",
                         add_url="ipam:role_add", import_url="ipam:role_import"),
            ),
        ),
        MenuGroup(
            label="Aggregates",
            items=(
                MenuItem(label="Aggregates", url="ipam:aggregate_list",
                         add_url="ipam:aggregate_add", import_url="ipam:aggregate_import"),
                MenuItem(label="RIRs", url="ipam:rir_list",
                         add_url="ipam:rir_add", import_url="ipam:rir_import"),
            ),
        ),
        MenuGroup(
            label="VRFs",
            items=(
                MenuItem(label="VRFs", url="ipam:vrf_list",
                         add_url="ipam:vrf_add", import_url="ipam:vrf_import"),
                MenuItem(label="Route Targets", url="ipam:routetarget_list",
                         add_url="ipam:routetarget_add", import_url="ipam:routetarget_import"),
            ),
        ),
        MenuGroup(
            label="VLANs",
            items=(
                MenuItem(label="VLANs", url="ipam:vlan_list",
                         add_url="ipam:vlan_add", import_url="ipam:vlan_import"),
                MenuItem(label="VLAN Groups", url="ipam:vlangroup_list",
                         add_url="ipam:vlangroup_add", import_url="ipam:vlangroup_import"),
            ),
        ),
        MenuGroup(
            label="Services",
            items=(MenuItem(label="Services", url="ipam:service_list",
                   add_url=None, import_url="ipam:service_import"),),
        ),
    ),
)

VIRTUALIZATION_MENU = Menu(
    label="Virtualization",
    icon="monitor",
    groups=(
        MenuGroup(
            label="Virtual Machines",
            items=(
                MenuItem(
                    label="Virtual Machines",
                    url="virtualization:virtualmachine_list", add_url="virtualization:virtualmachine_add", import_url="virtualization:virtualmachine_import"),
                MenuItem(label="Interfaces",
                         url="virtualization:vminterface_list", add_url="virtualization:vminterface_add", import_url="virtualization:vminterface_import"),
            ),
        ),
        MenuGroup(
            label="Clusters",
            items=(
                MenuItem(label="Clusters", url="virtualization:cluster_list",
                         add_url="virtualization:cluster_add", import_url="virtualization:cluster_import"),
                MenuItem(label="Cluster Types",
                         url="virtualization:clustertype_list", add_url="virtualization:clustertype_add", import_url="virtualization:clustertype_import"),
                MenuItem(
                    label="Cluster Groups", url="virtualization:clustergroup_list", add_url="virtualization:clustergroup_add", import_url="virtualization:clustergroup_import"),
            ),
        ),
    ),
)

CIRCUITS_MENU = Menu(
    label="Circuits",
    icon="transit-connection-variant",
    groups=(
        MenuGroup(
            label="Circuits",
            items=(
                MenuItem(label="Circuits", url="circuits:circuit_list",
                         add_url="circuits:circuit_add", import_url="circuits:circuit_import"),
                MenuItem(label="Circuit Types",
                         url="circuits:circuittype_list", add_url="circuits:circuittype_add", import_url="circuits:circuittype_import"),
            ),
        ),
        MenuGroup(
            label="Providers",
            items=(
                MenuItem(label="Providers", url="circuits:provider_list",
                         add_url="circuits:provider_add", import_url="circuits:provider_import"),
                MenuItem(
                    label="Provider Networks", url="circuits:providernetwork_list", add_url="circuits:providernetwork_add", import_url="circuits:providernetwork_import"
                ),
            ),
        ),
    ),
)

POWER_MENU = Menu(
    label="Power",
    icon="flash",
    groups=(
        MenuGroup(
            label="Power",
            items=(
                MenuItem(label="Power Feeds", url="dcim:powerfeed_list",
                         add_url="dcim:powerfeed_add", import_url="dcim:powerfeed_import"),
                MenuItem(label="Power Panels", url="dcim:powerpanel_list",
                         add_url="dcim:powerpanel_add", import_url="dcim:powerpanel_import"),
            ),
        ),
    ),
)

OTHER_MENU = Menu(
    label="Other",
    icon="notification-clear-all",
    groups=(
        MenuGroup(
            label="Logging",
            items=(
                MenuItem(label="Change Log", url="extras:objectchange_list",
                         add_url=None, import_url=None),
                MenuItem(label="Journal Entries",
                         url="extras:journalentry_list", add_url=None, import_url=None),
            ),
        ),
        MenuGroup(
            label="Customization",
            items=(
                MenuItem(label="Custom Fields", url="extras:customfield_list",
                         add_url="extras:customfield_add", import_url="extras:customfield_import"),
            ),
        ),
        MenuGroup(
            label="Miscellaneous",
            items=(
                MenuItem(label="Config Contexts",
                         url="extras:configcontext_list", add_url=None, import_url=None),
                MenuItem(label="Reports", url="extras:report_list",
                         add_url=None, import_url=None),
                MenuItem(label="Scripts", url="extras:script_list",
                         add_url=None, import_url=None),
            ),
        ),
    ),
)

MENUS = (
    ORGANIZATION_MENU,
    DEVICES_MENU,
    IPAM_MENU,
    VIRTUALIZATION_MENU,
    CIRCUITS_MENU,
    POWER_MENU,
    OTHER_MENU,
)


def process_menu(menu: Menu, perms: PermWrapper) -> MenuGroup:
    """Enable a menu item if view permissions exist for the user."""
    for group in menu.groups:
        for item in group.items:
            # Parse the URL template tag to a permission string.
            app, scope = item.url.split(":")
            object_name = scope.replace("_list", "")

            view_perm = f"{app}.view_{scope}"
            add_perm = f"{app}.add_object_name"

            if view_perm in perms:
                # If the view permission for each item exists, toggle
                # the `disabled` field, which will be used in the UI.
                item.disabled = False

            if add_perm in perms:
                if item.add_url is not None:
                    item.has_add = True
                if item.import_url is not None:
                    item.has_import = True

    return menu


@register.inclusion_tag("navigation/nav_items.html", takes_context=True)
def nav(context: Context) -> Dict:
    """Provide navigation items to template."""
    perms: PermWrapper = context["perms"]
    groups = [process_menu(g, perms) for g in MENUS]

    return {"nav_items": groups, "request": context["request"]}
