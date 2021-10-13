from dataclasses import dataclass
from typing import Sequence, Optional

from extras.registry import registry
from utilities.choices import ButtonColorChoices


#
# Nav menu data classes
#

@dataclass
class MenuItemButton:

    link: str
    title: str
    icon_class: str
    permissions: Optional[Sequence[str]] = ()
    color: Optional[str] = None


@dataclass
class MenuItem:

    link: str
    link_text: str
    permissions: Optional[Sequence[str]] = ()
    buttons: Optional[Sequence[MenuItemButton]] = ()


@dataclass
class MenuGroup:

    label: str
    items: Sequence[MenuItem]


@dataclass
class Menu:

    label: str
    icon_class: str
    groups: Sequence[MenuGroup]


#
# Utility functions
#

def get_model_item(app_label, model_name, label, actions=('add', 'import')):
    return MenuItem(
        link=f'{app_label}:{model_name}_list',
        link_text=label,
        permissions=[f'{app_label}.view_{model_name}'],
        buttons=get_model_buttons(app_label, model_name, actions)
    )


def get_model_buttons(app_label, model_name, actions=('add', 'import')):
    buttons = []

    if 'add' in actions:
        buttons.append(
            MenuItemButton(
                link=f'{app_label}:{model_name}_add',
                title='Add',
                icon_class='mdi mdi-plus-thick',
                permissions=[f'{app_label}.add_{model_name}'],
                color=ButtonColorChoices.GREEN
            )
        )
    if 'import' in actions:
        buttons.append(
            MenuItemButton(
                link=f'{app_label}:{model_name}_import',
                title='Import',
                icon_class='mdi mdi-upload',
                permissions=[f'{app_label}.add_{model_name}'],
                color=ButtonColorChoices.CYAN
            )
        )

    return buttons


#
# Nav menus
#

ORGANIZATION_MENU = Menu(
    label='Organization',
    icon_class='mdi mdi-domain',
    groups=(
        MenuGroup(
            label='Sites',
            items=(
                get_model_item('dcim', 'site', 'Sites'),
                get_model_item('dcim', 'region', 'Regions'),
                get_model_item('dcim', 'sitegroup', 'Site Groups'),
                get_model_item('dcim', 'location', 'Locations'),
            ),
        ),
        MenuGroup(
            label='Racks',
            items=(
                get_model_item('dcim', 'rack', 'Racks'),
                get_model_item('dcim', 'rackrole', 'Rack Roles'),
                get_model_item('dcim', 'rackreservation', 'Reservations'),
                MenuItem(
                    link='dcim:rack_elevation_list',
                    link_text='Elevations',
                    permissions=['dcim.view_rack']
                ),
            ),
        ),
        MenuGroup(
            label='Tenancy',
            items=(
                get_model_item('tenancy', 'tenant', 'Tenants'),
                get_model_item('tenancy', 'tenantgroup', 'Tenant Groups'),
            ),
        ),
    ),
)

DEVICES_MENU = Menu(
    label='Devices',
    icon_class='mdi mdi-server',
    groups=(
        MenuGroup(
            label='Devices',
            items=(
                get_model_item('dcim', 'device', 'Devices'),
                get_model_item('dcim', 'devicerole', 'Device Roles'),
                get_model_item('dcim', 'platform', 'Platforms'),
                get_model_item('dcim', 'virtualchassis', 'Virtual Chassis'),
            ),
        ),
        MenuGroup(
            label='Device Types',
            items=(
                get_model_item('dcim', 'devicetype', 'Device Types'),
                get_model_item('dcim', 'manufacturer', 'Manufacturers'),
            ),
        ),
        MenuGroup(
            label='Device Components',
            items=(
                get_model_item('dcim', 'interface', 'Interfaces', actions=['import']),
                get_model_item('dcim', 'frontport', 'Front Ports', actions=['import']),
                get_model_item('dcim', 'rearport', 'Rear Ports', actions=['import']),
                get_model_item('dcim', 'consoleport', 'Console Ports', actions=['import']),
                get_model_item('dcim', 'consoleserverport', 'Console Server Ports', actions=['import']),
                get_model_item('dcim', 'powerport', 'Power Ports', actions=['import']),
                get_model_item('dcim', 'poweroutlet', 'Power Outlets', actions=['import']),
                get_model_item('dcim', 'devicebay', 'Device Bays', actions=['import']),
                get_model_item('dcim', 'inventoryitem', 'Inventory Items', actions=['import']),
            ),
        ),
    ),
)

CONNECTIONS_MENU = Menu(
    label='Connections',
    icon_class='mdi mdi-ethernet',
    groups=(
        MenuGroup(
            label='Connections',
            items=(
                get_model_item('dcim', 'cable', 'Cables', actions=['import']),
                MenuItem(
                    link='dcim:interface_connections_list',
                    link_text='Interface Connections',
                    permissions=['dcim.view_interface']
                ),
                MenuItem(
                    link='dcim:console_connections_list',
                    link_text='Console Connections',
                    permissions=['dcim.view_consoleport']
                ),
                MenuItem(
                    link='dcim:power_connections_list',
                    link_text='Power Connections',
                    permissions=['dcim.view_powerport']
                ),
            ),
        ),
    ),
)

WIRELESS_MENU = Menu(
    label='Wireless',
    icon_class='mdi mdi-wifi',
    groups=(
        MenuGroup(
            label='Wireless',
            items=(
                get_model_item('wireless', 'wirelesslan', 'Wireless LANs'),
                get_model_item('wireless', 'wirelesslink', 'Wirelesss Links', actions=['import']),
            ),
        ),
    ),
)

IPAM_MENU = Menu(
    label='IPAM',
    icon_class='mdi mdi-counter',
    groups=(
        MenuGroup(
            label='IP Addresses',
            items=(
                get_model_item('ipam', 'ipaddress', 'IP Addresses'),
                get_model_item('ipam', 'iprange', 'IP Ranges'),
            ),
        ),
        MenuGroup(
            label='Prefixes',
            items=(
                get_model_item('ipam', 'prefix', 'Prefixes'),
                get_model_item('ipam', 'role', 'Prefix & VLAN Roles'),
            ),
        ),
        MenuGroup(
            label='Aggregates',
            items=(
                get_model_item('ipam', 'aggregate', 'Aggregates'),
                get_model_item('ipam', 'rir', 'RIRs'),
            ),
        ),
        MenuGroup(
            label='VRFs',
            items=(
                get_model_item('ipam', 'vrf', 'VRFs'),
                get_model_item('ipam', 'routetarget', 'Route Targets'),
            ),
        ),
        MenuGroup(
            label='VLANs',
            items=(
                get_model_item('ipam', 'vlan', 'VLANs'),
                get_model_item('ipam', 'vlangroup', 'VLAN Groups'),
            ),
        ),
        MenuGroup(
            label='Services',
            items=(
                get_model_item('ipam', 'service', 'Services', actions=['import']),
            ),
        ),
    ),
)

VIRTUALIZATION_MENU = Menu(
    label='Virtualization',
    icon_class='mdi mdi-monitor',
    groups=(
        MenuGroup(
            label='Virtual Machines',
            items=(
                get_model_item('virtualization', 'virtualmachine', 'Virtual Machines'),
                get_model_item('virtualization', 'vminterface', 'Interfaces', actions=['import']),
            ),
        ),
        MenuGroup(
            label='Clusters',
            items=(
                get_model_item('virtualization', 'cluster', 'Clusters'),
                get_model_item('virtualization', 'clustertype', 'Cluster Types'),
                get_model_item('virtualization', 'clustergroup', 'Cluster Groups'),
            ),
        ),
    ),
)

CIRCUITS_MENU = Menu(
    label='Circuits',
    icon_class='mdi mdi-transit-connection-variant',
    groups=(
        MenuGroup(
            label='Circuits',
            items=(
                get_model_item('circuits', 'circuit', 'Circuits'),
                get_model_item('circuits', 'circuittype', 'Circuit Types'),
            ),
        ),
        MenuGroup(
            label='Providers',
            items=(
                get_model_item('circuits', 'provider', 'Providers'),
                get_model_item('circuits', 'providernetwork', 'Provider Networks'),
            ),
        ),
    ),
)

POWER_MENU = Menu(
    label='Power',
    icon_class='mdi mdi-flash',
    groups=(
        MenuGroup(
            label='Power',
            items=(
                get_model_item('dcim', 'powerfeed', 'Power Feeds'),
                get_model_item('dcim', 'powerpanel', 'Power Panels'),
            ),
        ),
    ),
)

OTHER_MENU = Menu(
    label='Other',
    icon_class='mdi mdi-notification-clear-all',
    groups=(
        MenuGroup(
            label='Logging',
            items=(
                get_model_item('extras', 'journalentry', 'Journal Entries', actions=[]),
                get_model_item('extras', 'objectchange', 'Change Log', actions=[]),
            ),
        ),
        MenuGroup(
            label='Customization',
            items=(
                get_model_item('extras', 'customfield', 'Custom Fields'),
                get_model_item('extras', 'customlink', 'Custom Links'),
                get_model_item('extras', 'exporttemplate', 'Export Templates'),
            ),
        ),
        MenuGroup(
            label='Integrations',
            items=(
                get_model_item('extras', 'webhook', 'Webhooks'),
                MenuItem(
                    link='extras:report_list',
                    link_text='Reports',
                    permissions=['extras.view_report']
                ),
                MenuItem(
                    link='extras:script_list',
                    link_text='Scripts',
                    permissions=['extras.view_script']
                ),
            ),
        ),
        MenuGroup(
            label='Other',
            items=(
                get_model_item('extras', 'tag', 'Tags'),
                get_model_item('extras', 'configcontext', 'Config Contexts', actions=['add']),
            ),
        ),
    ),
)


MENUS = [
    ORGANIZATION_MENU,
    DEVICES_MENU,
    CONNECTIONS_MENU,
    WIRELESS_MENU,
    IPAM_MENU,
    VIRTUALIZATION_MENU,
    CIRCUITS_MENU,
    POWER_MENU,
    OTHER_MENU,
]

#
# Add plugin menus
#

if registry['plugin_menu_items']:
    plugin_menu_groups = []

    for plugin_name, items in registry['plugin_menu_items'].items():
        plugin_menu_groups.append(
            MenuGroup(
                label=plugin_name,
                items=items
            )
        )

    PLUGIN_MENU = Menu(
        label="Plugins",
        icon_class="mdi mdi-puzzle",
        groups=plugin_menu_groups
    )

    MENUS.append(PLUGIN_MENU)
