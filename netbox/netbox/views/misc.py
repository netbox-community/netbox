from collections import namedtuple

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views.generic import View
from django_tables2 import RequestConfig
from packaging import version

from circuits.models import Circuit, Provider
from dcim.models import (
    Cable, ConsolePort, Device, DeviceType, Interface, PowerPanel, PowerFeed, PowerPort, Rack, Site,
)
from extras.models import ObjectChange
from extras.tables import ObjectChangeTable
from ipam.models import Aggregate, IPAddress, IPRange, Prefix, VLAN, VRF
from netbox.forms import SearchForm
from netbox.search import LookupTypes
from netbox.search.backends import search_backend
from netbox.tables import SearchTable
from tenancy.models import Contact, Tenant
from utilities.htmx import is_htmx
from utilities.paginator import EnhancedPaginator, get_paginate_count
from virtualization.models import Cluster, VirtualMachine
from wireless.models import WirelessLAN, WirelessLink

__all__ = (
    'HomeView',
    'SearchView',
)

Link = namedtuple('Link', ('label', 'viewname', 'permission', 'count'))


class HomeView(View):
    template_name = 'home.html'

    def get(self, request):
        if settings.LOGIN_REQUIRED and not request.user.is_authenticated:
            return redirect('login')

        console_connections = ConsolePort.objects.restrict(request.user, 'view')\
            .prefetch_related('_path').filter(_path__is_complete=True).count
        power_connections = PowerPort.objects.restrict(request.user, 'view')\
            .prefetch_related('_path').filter(_path__is_complete=True).count
        interface_connections = Interface.objects.restrict(request.user, 'view')\
            .prefetch_related('_path').filter(_path__is_complete=True).count

        def get_count_queryset(model):
            return model.objects.restrict(request.user, 'view').count

        def build_stats():
            org = (
                Link(_('Sites'), 'dcim:site_list', 'dcim.view_site', get_count_queryset(Site)),
                Link(_('Tenants'), 'tenancy:tenant_list', 'tenancy.view_tenant', get_count_queryset(Tenant)),
                Link(_('Contacts'), 'tenancy:contact_list', 'tenancy.view_contact', get_count_queryset(Contact)),
            )
            dcim = (
                Link(_('Racks'), 'dcim:rack_list', 'dcim.view_rack', get_count_queryset(Rack)),
                Link(_('Device Types'), 'dcim:devicetype_list', 'dcim.view_devicetype', get_count_queryset(DeviceType)),
                Link(_('Devices'), 'dcim:device_list', 'dcim.view_device', get_count_queryset(Device)),
            )
            ipam = (
                Link(_('VRFs'), 'ipam:vrf_list', 'ipam.view_vrf', get_count_queryset(VRF)),
                Link(_('Aggregates'), 'ipam:aggregate_list', 'ipam.view_aggregate', get_count_queryset(Aggregate)),
                Link(_('Prefixes'), 'ipam:prefix_list', 'ipam.view_prefix', get_count_queryset(Prefix)),
                Link(_('IP Ranges'), 'ipam:iprange_list', 'ipam.view_iprange', get_count_queryset(IPRange)),
                Link(_('IP Addresses'), 'ipam:ipaddress_list', 'ipam.view_ipaddress', get_count_queryset(IPAddress)),
                Link(_('VLANs'), 'ipam:vlan_list', 'ipam.view_vlan', get_count_queryset(VLAN)),
            )
            circuits = (
                Link(_('Providers'), 'circuits:provider_list', 'circuits.view_provider', get_count_queryset(Provider)),
                Link(_('Circuits'), 'circuits:circuit_list', 'circuits.view_circuit', get_count_queryset(Circuit))
            )
            virtualization = (
                Link(_('Clusters'), 'virtualization:cluster_list', 'virtualization.view_cluster',
                     get_count_queryset(Cluster)),
                Link(_('Virtual Machines'), 'virtualization:virtualmachine_list', 'virtualization.view_virtualmachine',
                     get_count_queryset(VirtualMachine)),
            )
            connections = (
                Link(_('Cables'), 'dcim:cable_list', 'dcim.view_cable', get_count_queryset(Cable)),
                Link(_('Interfaces'), 'dcim:interface_connections_list', 'dcim.view_interface', interface_connections),
                Link(_('Console'), 'dcim:console_connections_list', 'dcim.view_consoleport', console_connections),
                Link(_('Power'), 'dcim:power_connections_list', 'dcim.view_powerport', power_connections),
            )
            power = (
                Link(_('Power Panels'), 'dcim:powerpanel_list', 'dcim.view_powerpanel', get_count_queryset(PowerPanel)),
                Link(_('Power Feeds'), 'dcim:powerfeed_list', 'dcim.view_powerfeed', get_count_queryset(PowerFeed)),
            )
            wireless = (
                Link(_('Wireless LANs'), 'wireless:wirelesslan_list', 'wireless.view_wirelesslan',
                     get_count_queryset(WirelessLAN)),
                Link(_('Wireless Links'), 'wireless:wirelesslink_list', 'wireless.view_wirelesslink',
                     get_count_queryset(WirelessLink)),
            )
            stats = (
                (_('Organization'), org, 'domain'),
                (_('IPAM'), ipam, 'counter'),
                (_('Virtualization'), virtualization, 'monitor'),
                (_('Inventory'), dcim, 'server'),
                (_('Circuits'), circuits, 'transit-connection-variant'),
                (_('Connections'), connections, 'cable-data'),
                (_('Power'), power, 'flash'),
                (_('Wireless'), wireless, 'wifi'),
            )

            return stats

        # Compile changelog table
        changelog = ObjectChange.objects.restrict(request.user, 'view').prefetch_related(
            'user', 'changed_object_type'
        )[:10]
        changelog_table = ObjectChangeTable(changelog, user=request.user)

        # Check whether a new release is available. (Only for staff/superusers.)
        new_release = None
        if request.user.is_staff or request.user.is_superuser:
            latest_release = cache.get('latest_release')
            if latest_release:
                release_version, release_url = latest_release
                if release_version > version.parse(settings.VERSION):
                    new_release = {
                        'version': str(release_version),
                        'url': release_url,
                    }

        return render(request, self.template_name, {
            'search_form': SearchForm(),
            'stats': build_stats(),
            'changelog_table': changelog_table,
            'new_release': new_release,
        })


class SearchView(View):

    def get(self, request):
        results = []
        highlight = None

        # Initialize search form
        form = SearchForm(request.GET) if 'q' in request.GET else SearchForm()

        if form.is_valid():

            # Restrict results by object type
            object_types = []
            for obj_type in form.cleaned_data['obj_types']:
                app_label, model_name = obj_type.split('.')
                object_types.append(ContentType.objects.get_by_natural_key(app_label, model_name))

            lookup = form.cleaned_data['lookup'] or LookupTypes.PARTIAL
            results = search_backend.search(
                form.cleaned_data['q'],
                user=request.user,
                object_types=object_types,
                lookup=lookup
            )

            if form.cleaned_data['lookup'] != LookupTypes.EXACT:
                highlight = form.cleaned_data['q']

        table = SearchTable(results, highlight=highlight)

        # Paginate the table results
        RequestConfig(request, {
            'paginator_class': EnhancedPaginator,
            'per_page': get_paginate_count(request)
        }).configure(table)

        # If this is an HTMX request, return only the rendered table HTML
        if is_htmx(request):
            return render(request, 'htmx/table.html', {
                'table': table,
            })

        return render(request, 'search.html', {
            'form': form,
            'table': table,
        })
