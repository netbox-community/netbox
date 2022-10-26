import platform
import sys
from collections import namedtuple

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseServerError
from django.shortcuts import redirect, render
from django.template import loader
from django.template.exceptions import TemplateDoesNotExist
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.csrf import requires_csrf_token
from django.views.defaults import ERROR_500_TEMPLATE_NAME, page_not_found
from django.views.generic import View
from packaging import version
from sentry_sdk import capture_message

from circuits.models import Circuit, Provider
from dcim.models import (
    Cable, ConsolePort, Device, DeviceType, Interface, PowerPanel, PowerFeed, PowerPort, Rack, Site,
)
from extras.models import ObjectChange
from extras.tables import ObjectChangeTable
from ipam.models import Aggregate, IPAddress, IPRange, Prefix, VLAN, VRF
from netbox.constants import SEARCH_MAX_RESULTS
from netbox.forms import SearchForm
from netbox.search import SEARCH_TYPES
from tenancy.models import Contact, Tenant
from virtualization.models import Cluster, VirtualMachine
from wireless.models import WirelessLAN, WirelessLink


Link = namedtuple('Link', ('label', 'viewname', 'permission', 'count'))


class HomeView(View):
    template_name = 'home.html'

    def get(self, request):
        if settings.LOGIN_REQUIRED and not request.user.is_authenticated:
            return redirect('login')

        console_connections = ConsolePort.objects.restrict(request.user, 'view').prefetch_related('_path').filter(
            _path__is_complete=True
        ).count
        power_connections = PowerPort.objects.restrict(request.user, 'view').prefetch_related('_path').filter(
            _path__is_complete=True
        ).count
        interface_connections = Interface.objects.restrict(request.user, 'view').prefetch_related('_path').filter(
            _path__is_complete=True
        ).count

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
        form = SearchForm(request.GET)
        results = []

        if form.is_valid():

            # If an object type has been specified, redirect to the dedicated view for it
            if form.cleaned_data['obj_type']:
                object_type = form.cleaned_data['obj_type']
                url = reverse(SEARCH_TYPES[object_type]['url'])
                return redirect(f"{url}?q={form.cleaned_data['q']}")

            for obj_type in SEARCH_TYPES.keys():

                queryset = SEARCH_TYPES[obj_type]['queryset'].restrict(request.user, 'view')
                filterset = SEARCH_TYPES[obj_type]['filterset']
                table = SEARCH_TYPES[obj_type]['table']
                url = SEARCH_TYPES[obj_type]['url']

                # Construct the results table for this object type
                filtered_queryset = filterset({'q': form.cleaned_data['q']}, queryset=queryset).qs
                table = table(filtered_queryset, orderable=False)
                table.paginate(per_page=SEARCH_MAX_RESULTS)

                if table.page:
                    results.append({
                        'name': queryset.model._meta.verbose_name_plural,
                        'table': table,
                        'url': f"{reverse(url)}?q={form.cleaned_data.get('q')}"
                    })

        return render(request, 'search.html', {
            'form': form,
            'results': results,
        })


class StaticMediaFailureView(View):
    """
    Display a user-friendly error message with troubleshooting tips when a static media file fails to load.
    """
    def get(self, request):
        return render(request, 'media_failure.html', {
            'filename': request.GET.get('filename')
        })


def handler_404(request, exception):
    """
    Wrap Django's default 404 handler to enable Sentry reporting.
    """
    capture_message("Page not found", level="error")

    return page_not_found(request, exception)


@requires_csrf_token
def server_error(request, template_name=ERROR_500_TEMPLATE_NAME):
    """
    Custom 500 handler to provide additional context when rendering 500.html.
    """
    try:
        template = loader.get_template(template_name)
    except TemplateDoesNotExist:
        return HttpResponseServerError('<h1>Server Error (500)</h1>', content_type='text/html')
    type_, error, traceback = sys.exc_info()

    return HttpResponseServerError(template.render({
        'error': error,
        'exception': str(type_),
        'netbox_version': settings.VERSION,
        'python_version': platform.python_version(),
    }))
