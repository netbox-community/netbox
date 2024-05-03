from django.utils.translation import gettext_lazy as _

from netbox.registry import registry
from . import *

#
# Nav menus
#

ORGANIZATION_MENU = Menu(
    label=_('Organization'),
    icon_class='mdi mdi-domain',
    groups=(
        MenuGroup(
            label=_('Sites'),
            items=(
                get_model_item('dcim', 'site', _('Sites')),
                get_model_item('dcim', 'region', _('Regions')),
                get_model_item('dcim', 'sitegroup', _('Site Groups')),
                get_model_item('dcim', 'location', _('Locations')),
            ),
        ),
        MenuGroup(
            label=_('Racks'),
            items=(
                get_model_item('dcim', 'rack', _('Racks')),
                get_model_item('dcim', 'rackrole', _('Rack Roles')),
                get_model_item('dcim', 'rackreservation', _('Reservations')),
                MenuItem(
                    link='dcim:rack_elevation_list',
                    link_text=_('Elevations'),
                    permissions=['dcim.view_rack']
                ),
            ),
        ),
        MenuGroup(
            label=_('Tenancy'),
            items=(
                get_model_item('tenancy', 'tenant', _('Tenants')),
                get_model_item('tenancy', 'tenantgroup', _('Tenant Groups')),
            ),
        ),
        MenuGroup(
            label=_('Contacts'),
            items=(
                get_model_item('tenancy', 'contact', _('Contacts')),
                get_model_item('tenancy', 'contactgroup', _('Contact Groups')),
                get_model_item('tenancy', 'contactrole', _('Contact Roles')),
                get_model_item('tenancy', 'contactassignment', _('Contact Assignments'), actions=['import']),
            ),
        ),
    ),
)

DEVICES_MENU = Menu(
    label=_('Devices'),
    icon_class='mdi mdi-server',
    groups=(
        MenuGroup(
            label=_('Devices'),
            items=(
                get_model_item('dcim', 'device', _('Devices')),
                get_model_item('dcim', 'module', _('Modules')),
                get_model_item('dcim', 'devicerole', _('Device Roles')),
                get_model_item('dcim', 'platform', _('Platforms')),
                get_model_item('dcim', 'virtualchassis', _('Virtual Chassis')),
                get_model_item('dcim', 'virtualdevicecontext', _('Virtual Device Contexts')),
            ),
        ),
        MenuGroup(
            label=_('Device Types'),
            items=(
                get_model_item('dcim', 'devicetype', _('Device Types')),
                get_model_item('dcim', 'moduletype', _('Module Types')),
                get_model_item('dcim', 'manufacturer', _('Manufacturers')),
            ),
        ),
        MenuGroup(
            label=_('Device Components'),
            items=(
                get_model_item('dcim', 'interface', _('Interfaces')),
                get_model_item('dcim', 'frontport', _('Front Ports')),
                get_model_item('dcim', 'rearport', _('Rear Ports')),
                get_model_item('dcim', 'consoleport', _('Console Ports')),
                get_model_item('dcim', 'consoleserverport', _('Console Server Ports')),
                get_model_item('dcim', 'powerport', _('Power Ports')),
                get_model_item('dcim', 'poweroutlet', _('Power Outlets')),
                get_model_item('dcim', 'modulebay', _('Module Bays')),
                get_model_item('dcim', 'devicebay', _('Device Bays')),
                get_model_item('dcim', 'inventoryitem', _('Inventory Items')),
                get_model_item('dcim', 'inventoryitemrole', _('Inventory Item Roles')),
            ),
        ),
    ),
)

CONNECTIONS_MENU = Menu(
    label=_('Connections'),
    icon_class='mdi mdi-connection',
    groups=(
        MenuGroup(
            label=_('Connections'),
            items=(
                get_model_item('dcim', 'cable', _('Cables'), actions=['import']),
                get_model_item('wireless', 'wirelesslink', _('Wireless Links')),
                MenuItem(
                    link='dcim:interface_connections_list',
                    link_text=_('Interface Connections'),
                    permissions=['dcim.view_interface']
                ),
                MenuItem(
                    link='dcim:console_connections_list',
                    link_text=_('Console Connections'),
                    permissions=['dcim.view_consoleport']
                ),
                MenuItem(
                    link='dcim:power_connections_list',
                    link_text=_('Power Connections'),
                    permissions=['dcim.view_powerport']
                ),
            ),
        ),
    ),
)

WIRELESS_MENU = Menu(
    label=_('Wireless'),
    icon_class='mdi mdi-wifi',
    groups=(
        MenuGroup(
            label=_('Wireless'),
            items=(
                get_model_item('wireless', 'wirelesslan', _('Wireless LANs')),
                get_model_item('wireless', 'wirelesslangroup', _('Wireless LAN Groups')),
            ),
        ),
    ),
)

IPAM_MENU = Menu(
    label=_('IPAM'),
    icon_class='mdi mdi-counter',
    groups=(
        MenuGroup(
            label=_('IP Addresses'),
            items=(
                get_model_item('ipam', 'ipaddress', _('IP Addresses')),
                get_model_item('ipam', 'iprange', _('IP Ranges')),
            ),
        ),
        MenuGroup(
            label=_('Prefixes'),
            items=(
                get_model_item('ipam', 'prefix', _('Prefixes')),
                get_model_item('ipam', 'role', _('Prefix & VLAN Roles')),
            ),
        ),
        MenuGroup(
            label=_('ASNs'),
            items=(
                get_model_item('ipam', 'asnrange', _('ASN Ranges')),
                get_model_item('ipam', 'asn', _('ASNs')),
            ),
        ),
        MenuGroup(
            label=_('Aggregates'),
            items=(
                get_model_item('ipam', 'aggregate', _('Aggregates')),
                get_model_item('ipam', 'rir', _('RIRs')),
            ),
        ),
        MenuGroup(
            label=_('VRFs'),
            items=(
                get_model_item('ipam', 'vrf', _('VRFs')),
                get_model_item('ipam', 'routetarget', _('Route Targets')),
            ),
        ),
        MenuGroup(
            label=_('VLANs'),
            items=(
                get_model_item('ipam', 'vlan', _('VLANs')),
                get_model_item('ipam', 'vlangroup', _('VLAN Groups')),
            ),
        ),
        MenuGroup(
            label=_('Other'),
            items=(
                get_model_item('ipam', 'fhrpgroup', _('FHRP Groups')),
                get_model_item('ipam', 'servicetemplate', _('Service Templates')),
                get_model_item('ipam', 'service', _('Services')),
            ),
        ),
    ),
)

VPN_MENU = Menu(
    label=_('VPN'),
    icon_class='mdi mdi-graph-outline',
    groups=(
        MenuGroup(
            label=_('Tunnels'),
            items=(
                get_model_item('vpn', 'tunnel', _('Tunnels')),
                get_model_item('vpn', 'tunnelgroup', _('Tunnel Groups')),
                get_model_item('vpn', 'tunneltermination', _('Tunnel Terminations')),
            ),
        ),
        MenuGroup(
            label=_('L2VPNs'),
            items=(
                get_model_item('vpn', 'l2vpn', _('L2VPNs')),
                get_model_item('vpn', 'l2vpntermination', _('Terminations')),
            ),
        ),
        MenuGroup(
            label=_('Security'),
            items=(
                get_model_item('vpn', 'ikeproposal', _('IKE Proposals')),
                get_model_item('vpn', 'ikepolicy', _('IKE Policies')),
                get_model_item('vpn', 'ipsecproposal', _('IPSec Proposals')),
                get_model_item('vpn', 'ipsecpolicy', _('IPSec Policies')),
                get_model_item('vpn', 'ipsecprofile', _('IPSec Profiles')),
            ),
        ),
    ),
)

VIRTUALIZATION_MENU = Menu(
    label=_('Virtualization'),
    icon_class='mdi mdi-monitor',
    groups=(
        MenuGroup(
            label=_('Virtual Machines'),
            items=(
                get_model_item('virtualization', 'virtualmachine', _('Virtual Machines')),
                get_model_item('virtualization', 'vminterface', _('Interfaces')),
                get_model_item('virtualization', 'virtualdisk', _('Virtual Disks')),
            ),
        ),
        MenuGroup(
            label=_('Clusters'),
            items=(
                get_model_item('virtualization', 'cluster', _('Clusters')),
                get_model_item('virtualization', 'clustertype', _('Cluster Types')),
                get_model_item('virtualization', 'clustergroup', _('Cluster Groups')),
            ),
        ),
    ),
)

CIRCUITS_MENU = Menu(
    label=_('Circuits'),
    icon_class='mdi mdi-transit-connection-variant',
    groups=(
        MenuGroup(
            label=_('Circuits'),
            items=(
                get_model_item('circuits', 'circuit', _('Circuits')),
                get_model_item('circuits', 'circuittype', _('Circuit Types')),
            ),
        ),
        MenuGroup(
            label=_('Providers'),
            items=(
                get_model_item('circuits', 'provider', _('Providers')),
                get_model_item('circuits', 'provideraccount', _('Provider Accounts')),
                get_model_item('circuits', 'providernetwork', _('Provider Networks')),
            ),
        ),
    ),
)

POWER_MENU = Menu(
    label=_('Power'),
    icon_class='mdi mdi-flash',
    groups=(
        MenuGroup(
            label=_('Power'),
            items=(
                get_model_item('dcim', 'powerfeed', _('Power Feeds')),
                get_model_item('dcim', 'powerpanel', _('Power Panels')),
            ),
        ),
    ),
)

PROVISIONING_MENU = Menu(
    label=_('Provisioning'),
    icon_class='mdi mdi-file-document-multiple-outline',
    groups=(
        MenuGroup(
            label=_('Configurations'),
            items=(
                get_model_item('extras', 'configcontext', _('Config Contexts'), actions=['add']),
                get_model_item('extras', 'configtemplate', _('Config Templates'), actions=['add']),
            ),
        ),
    ),
)

CUSTOMIZATION_MENU = Menu(
    label=_('Customization'),
    icon_class='mdi mdi-toolbox-outline',
    groups=(
        MenuGroup(
            label=_('Customization'),
            items=(
                get_model_item('extras', 'customfield', _('Custom Fields')),
                get_model_item('extras', 'customfieldchoiceset', _('Custom Field Choices')),
                get_model_item('extras', 'customlink', _('Custom Links')),
                get_model_item('extras', 'exporttemplate', _('Export Templates')),
                get_model_item('extras', 'savedfilter', _('Saved Filters')),
                get_model_item('extras', 'tag', 'Tags'),
                get_model_item('extras', 'imageattachment', _('Image Attachments'), actions=()),
            ),
        ),
        MenuGroup(
            label=_('Scripts'),
            items=(
                MenuItem(
                    link='extras:script_list',
                    link_text=_('Scripts'),
                    permissions=['extras.view_script'],
                    buttons=get_model_buttons('extras', "scriptmodule", actions=['add'])
                ),
            ),
        ),
    ),
)

OPERATIONS_MENU = Menu(
    label=_('Operations'),
    icon_class='mdi mdi-cogs',
    groups=(
        MenuGroup(
            label=_('Integrations'),
            items=(
                get_model_item('core', 'datasource', _('Data Sources')),
                get_model_item('extras', 'eventrule', _('Event Rules')),
                get_model_item('extras', 'webhook', _('Webhooks')),
            ),
        ),
        MenuGroup(
            label=_('Jobs'),
            items=(
                MenuItem(
                    link='core:job_list',
                    link_text=_('Jobs'),
                    permissions=['core.view_job'],
                ),
            ),
        ),
        MenuGroup(
            label=_('Logging'),
            items=(
                get_model_item('extras', 'journalentry', _('Journal Entries'), actions=['import']),
                get_model_item('extras', 'objectchange', _('Change Log'), actions=[]),
            ),
        ),
    ),
)

ADMIN_MENU = Menu(
    label=_('Admin'),
    icon_class='mdi mdi-account-multiple',
    groups=(
        MenuGroup(
            label=_('Authentication'),
            items=(
                MenuItem(
                    link=f'users:user_list',
                    link_text=_('Users'),
                    permissions=[f'auth.view_user'],
                    buttons=(
                        MenuItemButton(
                            link=f'users:user_add',
                            title='Add',
                            icon_class='mdi mdi-plus-thick',
                            permissions=[f'auth.add_user']
                        ),
                        MenuItemButton(
                            link=f'users:user_import',
                            title='Import',
                            icon_class='mdi mdi-upload',
                            permissions=[f'auth.add_user']
                        )
                    )
                ),
                MenuItem(
                    link=f'users:group_list',
                    link_text=_('Groups'),
                    permissions=[f'auth.view_group'],
                    buttons=(
                        MenuItemButton(
                            link=f'users:group_add',
                            title='Add',
                            icon_class='mdi mdi-plus-thick',
                            permissions=[f'auth.add_group']
                        ),
                        MenuItemButton(
                            link=f'users:group_import',
                            title='Import',
                            icon_class='mdi mdi-upload',
                            permissions=[f'auth.add_group']
                        )
                    )
                ),
                MenuItem(
                    link=f'users:token_list',
                    link_text=_('API Tokens'),
                    permissions=[f'users.view_token'],
                    buttons=get_model_buttons('users', 'token')
                ),
                MenuItem(
                    link=f'users:objectpermission_list',
                    link_text=_('Permissions'),
                    permissions=[f'users.view_objectpermission'],
                    buttons=get_model_buttons('users', 'objectpermission', actions=['add'])
                ),
            ),
        ),
        MenuGroup(
            label=_('System'),
            items=(
                MenuItem(
                    link='core:system',
                    link_text=_('System')
                ),
                MenuItem(
                    link='core:configrevision_list',
                    link_text=_('Configuration History'),
                    permissions=['core.view_configrevision']
                ),
                MenuItem(
                    link='core:background_queue_list',
                    link_text=_('Background Tasks')
                ),
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
    VPN_MENU,
    VIRTUALIZATION_MENU,
    CIRCUITS_MENU,
    POWER_MENU,
    PROVISIONING_MENU,
    CUSTOMIZATION_MENU,
    OPERATIONS_MENU,
    ADMIN_MENU,
]

#
# Add plugin menus
#

for menu in registry['plugins']['menus']:
    MENUS.append(menu)

if registry['plugins']['menu_items']:

    # Build the default plugins menu
    groups = [
        MenuGroup(label=label, items=items)
        for label, items in registry['plugins']['menu_items'].items()
    ]
    plugins_menu = Menu(
        label=_("Plugins"),
        icon_class="mdi mdi-puzzle",
        groups=groups
    )
    MENUS.append(plugins_menu)
