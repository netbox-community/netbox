from markdown import markdown

from django.conf import settings
from django.http import Http404
from django.shortcuts import render
from django.utils.safestring import mark_safe

from circuits.models import Provider, Circuit
from dcim.models import Site, Rack, Device, ConsolePort, PowerPort, InterfaceConnection
from extras.models import UserAction
from ipam.models import Aggregate, Prefix, IPAddress, VLAN
from secrets.models import Secret


def home(request):

    stats = {

        # DCIM
        'site_count': Site.objects.count(),
        'rack_count': Rack.objects.count(),
        'device_count': Device.objects.count(),
        'interface_connections_count': InterfaceConnection.objects.count(),
        'console_connections_count': ConsolePort.objects.filter(cs_port__isnull=False).count(),
        'power_connections_count': PowerPort.objects.filter(power_outlet__isnull=False).count(),

        # IPAM
        'aggregate_count': Aggregate.objects.count(),
        'prefix_count': Prefix.objects.count(),
        'ipaddress_count': IPAddress.objects.count(),
        'vlan_count': VLAN.objects.count(),

        # Circuits
        'provider_count': Provider.objects.count(),
        'circuit_count': Circuit.objects.count(),

        # Secrets
        'secret_count': Secret.objects.count(),

    }

    return render(request, 'home.html', {
        'stats': stats,
        'recent_activity': UserAction.objects.select_related('user')[:15]
    })


def docs(request, path):
    """
    Display a page of Markdown-formatted documentation.
    """
    filename = '{}/docs/{}.md'.format(settings.BASE_DIR.rsplit('/', 1)[0], path)
    try:
        with open(filename, 'r') as docfile:
            markup = docfile.read()
    except:
        raise Http404

    content = mark_safe(markdown(markup, extensions=['mdx_gfm', 'toc']))

    return render(request, 'docs.html', {
        'content': content,
        'path': path,
    })


def trigger_500(request):
    """Hot-wired method of triggering a server error to test reporting."""

    raise Exception("Congratulations, you've triggered an exception! Go tell all your friends what an exceptional "
                    "person you are.")
