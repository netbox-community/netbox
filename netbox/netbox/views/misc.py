import re
from collections import namedtuple

from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.generic import View
from django_tables2 import RequestConfig
from packaging import version

from extras.constants import DEFAULT_DASHBOARD
from extras.dashboard.utils import get_dashboard, get_default_dashboard
from netbox.forms import SearchForm
from netbox.search import LookupTypes
from netbox.search.backends import search_backend
from netbox.tables import SearchTable
from utilities.htmx import htmx_partial
from utilities.paginator import EnhancedPaginator, get_paginate_count

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

        # Construct the user's custom dashboard layout
        try:
            dashboard = get_dashboard(request.user).get_layout()
        except Exception:
            messages.error(request, _(
                "There was an error loading the dashboard configuration. A default dashboard is in use."
            ))
            dashboard = get_default_dashboard(config=DEFAULT_DASHBOARD).get_layout()

        # Check whether a new release is available. (Only for staff/superusers.)
        new_release = None
        if request.user.is_staff or request.user.is_superuser:
            latest_release = cache.get('latest_release')
            if latest_release:
                release_version, release_url = latest_release
                if release_version > version.parse(settings.RELEASE.version):
                    new_release = {
                        'version': str(release_version),
                        'url': release_url,
                    }

        return render(request, self.template_name, {
            'dashboard': dashboard,
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

            # If performing a regex search, pass the highlight value as a compiled pattern
            if form.cleaned_data['lookup'] == LookupTypes.REGEX:
                try:
                    highlight = re.compile(f"({form.cleaned_data['q']})", flags=re.IGNORECASE)
                except re.error:
                    pass
            elif form.cleaned_data['lookup'] != LookupTypes.EXACT:
                highlight = form.cleaned_data['q']

        table = SearchTable(results, highlight=highlight)

        # Paginate the table results
        RequestConfig(request, {
            'paginator_class': EnhancedPaginator,
            'per_page': get_paginate_count(request)
        }).configure(table)

        # If this is an HTMX request, return only the rendered table HTML
        if htmx_partial(request):
            return render(request, 'htmx/table.html', {
                'table': table,
            })

        return render(request, 'search.html', {
            'form': form,
            'table': table,
        })
