from dataclasses import dataclass
from typing import Dict, Sequence
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


@dataclass
class MenuGroup:
    """A group of menu items within a menu."""

    label: str
    items: Sequence[MenuItem]


@dataclass
class Menu:
    """A top level menu group. Example: Organization, Devices, IPAM."""

    label: str
    groups: Sequence[MenuGroup]


ORGANIZATION_MENU = Menu(
    label="Organization",
    groups=(
        MenuGroup(
            label="Sites",
            items=(
                MenuItem(label="Sites", url="dcim:site_list"),
                MenuItem(label="Site Groups", url="dcim:sitegroup_list"),
                MenuItem(label="Regions", url="dcim:region_list"),
                MenuItem(label="Locations", url="dcim:location_list"),
            ),
        ),
        MenuGroup(
            label="Racks",
            items=(
                MenuItem(label="Racks", url="dcim:rack_list"),
                MenuItem(label="Rack Roles", url="dcim:rackrole_list"),
                MenuItem(label="Elevations", url="dcim:rack_elevation_list"),
            ),
        ),
        MenuGroup(
            label="Tenancy",
            items=(
                MenuItem(label="Tenants", url="tenancy:tenant_list"),
                MenuItem(label="Tenant Groups", url="tenancy:tenantgroup_list"),
            ),
        ),
        MenuGroup(
            label="Tags",
            items=(MenuItem(label="Tags", url="extras:tag_list"),),
        ),
    ),
)

DEVICES_MENU = Menu(
    label="Devices",
    groups=(
        MenuGroup(
            label="Devices",
            items=(
                MenuItem(label="Devices", url="dcim:device_list"),
                MenuItem(label="Device Roles", url="dcim:devicerole_list"),
                MenuItem(label="Platforms", url="dcim:platform_list"),
                MenuItem(label="Virtual Chassis", url="dcim:virtualchassis_list"),
            ),
        ),
        MenuGroup(
            label="Device Types",
            items=(
                MenuItem(label="Device Types", url="dcim:devicetype_list"),
                MenuItem(label="Manufacturers", url="dcim:manufacturer_list"),
            ),
        ),
        MenuGroup(
            label="Connections",
            items=(
                MenuItem(label="Cables", url="dcim:cable_list"),
                MenuItem(
                    label="Console Connections", url="dcim:console_connections_list"
                ),
                MenuItem(
                    label="Interface Connections", url="dcim:interface_connections_list"
                ),
                MenuItem(label="Power Connections", url="dcim:power_connections_list"),
            ),
        ),
        MenuGroup(
            label="Device Components",
            items=(
                MenuItem(label="Interfaces", url="dcim:interface_list"),
                MenuItem(label="Front Ports", url="dcim:frontport_list"),
                MenuItem(label="Rear Ports", url="dcim:rearport_list"),
                MenuItem(label="Console Ports", url="dcim:consoleport_list"),
                MenuItem(
                    label="Console Server Ports", url="dcim:consoleserverport_list"
                ),
                MenuItem(label="Power Ports", url="dcim:powerport_list"),
                MenuItem(label="Power Outlets", url="dcim:poweroutlet_list"),
                MenuItem(label="Device Bays", url="dcim:devicebay_list"),
                MenuItem(label="Inventory Items", url="dcim:inventoryitem_list"),
            ),
        ),
    ),
)

IPAM_MENU = Menu(
    label="IPAM",
    groups=(
        MenuGroup(
            label="IP Addresses",
            items=(MenuItem(label="IP Addresses", url="ipam:ipaddress_list"),),
        ),
        MenuGroup(
            label="Prefixes",
            items=(
                MenuItem(label="Prefixes", url="ipam:prefix_list"),
                MenuItem(label="Prefix & VLAN Roles", url="ipam:role_list"),
            ),
        ),
        MenuGroup(
            label="Aggregates",
            items=(
                MenuItem(label="Aggregates", url="ipam:aggregate_list"),
                MenuItem(label="RIRs", url="ipam:rir_list"),
            ),
        ),
        MenuGroup(
            label="VRFs",
            items=(
                MenuItem(label="VRFs", url="ipam:vrf_list"),
                MenuItem(label="Route Targets", url="ipam:routetarget_list"),
            ),
        ),
        MenuGroup(
            label="VLANs",
            items=(
                MenuItem(label="VLANs", url="ipam:vlan_list"),
                MenuItem(label="VLAN Groups", url="ipam:vlangroup_list"),
            ),
        ),
        MenuGroup(
            label="Services",
            items=(MenuItem(label="Services", url="ipam:service_list"),),
        ),
    ),
)

VIRTUALIZATION_MENU = Menu(
    label="Virtualization",
    groups=(
        MenuGroup(
            label="Virtual Machines",
            items=(
                MenuItem(
                    label="Virtual Machines",
                    url="virtualization:virtualmachine_list",
                ),
                MenuItem(label="Interfaces", url="virtualization:vminterface_list"),
            ),
        ),
        MenuGroup(
            label="Clusters",
            items=(
                MenuItem(label="Clusters", url="virtualization:cluster_list"),
                MenuItem(label="Cluster Types", url="virtualization:clustertype_list"),
                MenuItem(
                    label="Cluster Groups", url="virtualization:clustergroup_list"
                ),
            ),
        ),
    ),
)

CIRCUITS_MENU = Menu(
    label="Circuits",
    groups=(
        MenuGroup(
            label="Circuits",
            items=(
                MenuItem(label="Circuits", url="circuits:circuit_list"),
                MenuItem(label="Circuit Types", url="circuits:circuittype_list"),
            ),
        ),
        MenuGroup(
            label="Providers",
            items=(
                MenuItem(label="Providers", url="circuits:provider_list"),
                MenuItem(
                    label="Provider Networks", url="circuits:providernetwork_list"
                ),
            ),
        ),
    ),
)

POWER_MENU = Menu(
    label="Power",
    groups=(
        MenuGroup(
            label="Power",
            items=(
                MenuItem(label="Power Feeds", url="dcim:powerfeed_list"),
                MenuItem(label="Power Panels", url="dcim:powerpanel_list"),
            ),
        ),
    ),
)

OTHER_MENU = Menu(
    label="Other",
    groups=(
        MenuGroup(
            label="Logging",
            items=(
                MenuItem(label="Change Log", url="extras:objectchange_list"),
                MenuItem(label="Journal Entries", url="extras:journalentry_list"),
            ),
        ),
        MenuGroup(
            label="Miscellaneous",
            items=(
                MenuItem(label="Config Contexts", url="extras:configcontext_list"),
                MenuItem(label="Reports", url="extras:report_list"),
                MenuItem(label="Scripts", url="extras:script_list"),
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
            view_perm = f"{app}.view_{scope}"
            if view_perm in perms:
                # If the view permission for each item exists, toggle
                # the `disabled` field, which will be used in the UI.
                item.disabled = False

    return menu


@register.inclusion_tag("navigation/nav_items.html", takes_context=True)
def nav(context: Context) -> Dict:
    """Provide navigation items to template."""
    perms: PermWrapper = context["perms"]
    groups = [process_menu(g, perms) for g in MENUS]

    return {"nav_items": groups, "request": context["request"]}
