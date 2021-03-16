import platform
import sys

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import F
from django.http import HttpResponseServerError
from django.shortcuts import render
from django.template import loader
from django.template.exceptions import TemplateDoesNotExist
from django.urls import reverse
from django.views.decorators.csrf import requires_csrf_token
from django.views.defaults import ERROR_500_TEMPLATE_NAME
from django.views.generic import View
from packaging import version

from circuits.models import Circuit, Provider
from dcim.models import (
    Cable, ConsolePort, Device, DeviceType, Interface, PowerPanel, PowerFeed, PowerPort, Rack, Site,
)
from extras.choices import JobResultStatusChoices
from extras.models import ObjectChange, JobResult
from ipam.models import Aggregate, IPAddress, Prefix, VLAN, VRF
from netbox.constants import SEARCH_MAX_RESULTS, SEARCH_TYPES
from netbox.forms import SearchForm
from netbox.releases import get_latest_release
from secrets.models import Secret
from tenancy.models import Tenant
from virtualization.models import Cluster, VirtualMachine


class HomeView(View):
    template_name = 'home.html'

    def get(self, request):

        connected_consoleports = ConsolePort.objects.restrict(request.user, 'view').prefetch_related('_path').filter(
            _path__destination_id__isnull=False
        )
        connected_powerports = PowerPort.objects.restrict(request.user, 'view').prefetch_related('_path').filter(
            _path__destination_id__isnull=False
        )
        connected_interfaces = Interface.objects.restrict(request.user, 'view').prefetch_related('_path').filter(
            _path__destination_id__isnull=False,
            pk__lt=F('_path__destination_id')
        )

        # Report Results
        report_content_type = ContentType.objects.get(app_label='extras', model='report')
        report_results = JobResult.objects.filter(
            obj_type=report_content_type,
            status__in=JobResultStatusChoices.TERMINAL_STATE_CHOICES
        ).defer('data')[:10]

        stats = {

            # Organization
            'site_count': Site.objects.restrict(request.user, 'view').count(),
            'tenant_count': Tenant.objects.restrict(request.user, 'view').count(),

            # DCIM
            'rack_count': Rack.objects.restrict(request.user, 'view').count(),
            'devicetype_count': DeviceType.objects.restrict(request.user, 'view').count(),
            'device_count': Device.objects.restrict(request.user, 'view').count(),
            'interface_connections_count': connected_interfaces.count(),
            'cable_count': Cable.objects.restrict(request.user, 'view').count(),
            'console_connections_count': connected_consoleports.count(),
            'power_connections_count': connected_powerports.count(),
            'powerpanel_count': PowerPanel.objects.restrict(request.user, 'view').count(),
            'powerfeed_count': PowerFeed.objects.restrict(request.user, 'view').count(),

            # IPAM
            'vrf_count': VRF.objects.restrict(request.user, 'view').count(),
            'aggregate_count': Aggregate.objects.restrict(request.user, 'view').count(),
            'prefix_count': Prefix.objects.restrict(request.user, 'view').count(),
            'ipaddress_count': IPAddress.objects.restrict(request.user, 'view').count(),
            'vlan_count': VLAN.objects.restrict(request.user, 'view').count(),

            # Circuits
            'provider_count': Provider.objects.restrict(request.user, 'view').count(),
            'circuit_count': Circuit.objects.restrict(request.user, 'view').count(),

            # Secrets
            'secret_count': Secret.objects.restrict(request.user, 'view').count(),

            # Virtualization
            'cluster_count': Cluster.objects.restrict(request.user, 'view').count(),
            'virtualmachine_count': VirtualMachine.objects.restrict(request.user, 'view').count(),

        }

        changelog = ObjectChange.objects.restrict(request.user, 'view').prefetch_related('user', 'changed_object_type')

        # Check whether a new release is available. (Only for staff/superusers.)
        new_release = None
        if request.user.is_staff or request.user.is_superuser:
            latest_release, release_url = get_latest_release()
            if isinstance(latest_release, version.Version):
                current_version = version.parse(settings.VERSION)
                if latest_release > current_version:
                    new_release = {
                        'version': str(latest_release),
                        'url': release_url,
                    }

        return render(request, self.template_name, {
            'search_form': SearchForm(),
            'stats': stats,
            'report_results': report_results,
            'changelog': changelog[:15],
            'new_release': new_release,
        })


class SearchView(View):

    def get(self, request):

        # No query
        if 'q' not in request.GET:
            return render(request, 'search.html', {
                'form': SearchForm(),
            })

        form = SearchForm(request.GET)
        results = []

        if form.is_valid():

            if form.cleaned_data['obj_type']:
                # Searching for a single type of object
                obj_types = [form.cleaned_data['obj_type']]
            else:
                # Searching all object types
                obj_types = SEARCH_TYPES.keys()

            for obj_type in obj_types:

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
