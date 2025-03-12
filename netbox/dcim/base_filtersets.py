import django_filters

from django.utils.translation import gettext as _
from netbox.filtersets import BaseFilterSet
from utilities.filters import ContentTypeFilter, TreeNodeMultipleChoiceFilter
from .models import *

__all__ = (
    'ScopedFilterSet',
)


class ScopedFilterSet(BaseFilterSet):
    """
    Provides additional filtering functionality for location, site, etc.. for Scoped models.
    """
    scope_type = ContentTypeFilter()
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='_region',
        lookup_expr='in',
        label=_('Region (ID)'),
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='_region',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Region (slug)'),
    )
    site_group_id = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='_site_group',
        lookup_expr='in',
        label=_('Site group (ID)'),
    )
    site_group = TreeNodeMultipleChoiceFilter(
        queryset=SiteGroup.objects.all(),
        field_name='_site_group',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Site group (slug)'),
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        field_name='_site',
        label=_('Site (ID)'),
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='_site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label=_('Site (slug)'),
    )
    location_id = TreeNodeMultipleChoiceFilter(
        queryset=Location.objects.all(),
        field_name='_location',
        lookup_expr='in',
        label=_('Location (ID)'),
    )
    location = TreeNodeMultipleChoiceFilter(
        queryset=Location.objects.all(),
        field_name='_location',
        lookup_expr='in',
        to_field_name='slug',
        label=_('Location (slug)'),
    )
