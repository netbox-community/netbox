from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _
from timezone_field import TimeZoneField

from dcim.choices import *
from dcim.constants import *
from netbox.models import NestedGroupModel, PrimaryModel
from utilities.fields import NaturalOrderingField

__all__ = (
    'Location',
    'Region',
    'Site',
    'SiteGroup',
)


#
# Regions
#

class Region(NestedGroupModel):
    """
    A region represents a geographic collection of sites. For example, you might create regions representing countries,
    states, and/or cities. Regions are recursively nested into a hierarchy: all sites belonging to a child region are
    also considered to be members of its parent and ancestor region(s).
    """
    # Generic relations
    vlan_groups = GenericRelation(
        to='ipam.VLANGroup',
        content_type_field='scope_type',
        object_id_field='scope_id',
        related_query_name='region'
    )
    contacts = GenericRelation(
        to='tenancy.ContactAssignment'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('parent', 'name'),
                name='%(app_label)s_%(class)s_parent_name'
            ),
            models.UniqueConstraint(
                fields=('name',),
                name='%(app_label)s_%(class)s_name',
                condition=Q(parent__isnull=True),
                violation_error_message="A top-level region with this name already exists."
            ),
            models.UniqueConstraint(
                fields=('parent', 'slug'),
                name='%(app_label)s_%(class)s_parent_slug'
            ),
            models.UniqueConstraint(
                fields=('slug',),
                name='%(app_label)s_%(class)s_slug',
                condition=Q(parent__isnull=True),
                violation_error_message="A top-level region with this slug already exists."
            ),
        )

    def get_absolute_url(self):
        return reverse('dcim:region', args=[self.pk])

    def get_site_count(self):
        return Site.objects.filter(
            Q(region=self) |
            Q(region__in=self.get_descendants())
        ).count()


#
# Site groups
#

class SiteGroup(NestedGroupModel):
    """
    A site group is an arbitrary grouping of sites. For example, you might have corporate sites and customer sites; and
    within corporate sites you might distinguish between offices and data centers. Like regions, site groups can be
    nested recursively to form a hierarchy.
    """
    # Generic relations
    vlan_groups = GenericRelation(
        to='ipam.VLANGroup',
        content_type_field='scope_type',
        object_id_field='scope_id',
        related_query_name='site_group'
    )
    contacts = GenericRelation(
        to='tenancy.ContactAssignment'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('parent', 'name'),
                name='%(app_label)s_%(class)s_parent_name'
            ),
            models.UniqueConstraint(
                fields=('name',),
                name='%(app_label)s_%(class)s_name',
                condition=Q(parent__isnull=True),
                violation_error_message="A top-level site group with this name already exists."
            ),
            models.UniqueConstraint(
                fields=('parent', 'slug'),
                name='%(app_label)s_%(class)s_parent_slug'
            ),
            models.UniqueConstraint(
                fields=('slug',),
                name='%(app_label)s_%(class)s_slug',
                condition=Q(parent__isnull=True),
                violation_error_message="A top-level site group with this slug already exists."
            ),
        )

    def get_absolute_url(self):
        return reverse('dcim:sitegroup', args=[self.pk])

    def get_site_count(self):
        return Site.objects.filter(
            Q(group=self) |
            Q(group__in=self.get_descendants())
        ).count()


#
# Sites
#

class Site(PrimaryModel):
    """
    A Site represents a geographic location within a network; typically a building or campus. The optional facility
    field can be used to include an external designation, such as a data center name (e.g. Equinix SV6).
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text=_("Full name of the site")
    )
    _name = NaturalOrderingField(
        target_field='name',
        max_length=100,
        blank=True
    )
    slug = models.SlugField(
        max_length=100,
        unique=True
    )
    status = models.CharField(
        max_length=50,
        choices=SiteStatusChoices,
        default=SiteStatusChoices.STATUS_ACTIVE
    )
    region = models.ForeignKey(
        to='dcim.Region',
        on_delete=models.SET_NULL,
        related_name='sites',
        blank=True,
        null=True
    )
    group = models.ForeignKey(
        to='dcim.SiteGroup',
        on_delete=models.SET_NULL,
        related_name='sites',
        blank=True,
        null=True
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='sites',
        blank=True,
        null=True
    )
    facility = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Local facility ID or description")
    )
    asns = models.ManyToManyField(
        to='ipam.ASN',
        related_name='sites',
        blank=True
    )
    time_zone = TimeZoneField(
        blank=True
    )
    physical_address = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Physical location of the building")
    )
    shipping_address = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("If different from the physical address")
    )
    latitude = models.DecimalField(
        max_digits=8,
        decimal_places=6,
        blank=True,
        null=True,
        help_text=_("GPS coordinate in decimal format (xx.yyyyyy)")
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        help_text=_("GPS coordinate in decimal format (xx.yyyyyy)")
    )

    # Generic relations
    vlan_groups = GenericRelation(
        to='ipam.VLANGroup',
        content_type_field='scope_type',
        object_id_field='scope_id',
        related_query_name='site'
    )
    contacts = GenericRelation(
        to='tenancy.ContactAssignment'
    )
    images = GenericRelation(
        to='extras.ImageAttachment'
    )

    clone_fields = (
        'status', 'region', 'group', 'tenant', 'facility', 'time_zone', 'physical_address', 'shipping_address',
        'latitude', 'longitude', 'description',
    )

    class Meta:
        ordering = ('_name',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('dcim:site', args=[self.pk])

    def get_status_color(self):
        return SiteStatusChoices.colors.get(self.status)


#
# Locations
#

class Location(NestedGroupModel):
    """
    A Location represents a subgroup of Racks and/or Devices within a Site. A Location may represent a building within a
    site, or a room within a building, for example.
    """
    site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.CASCADE,
        related_name='locations'
    )
    status = models.CharField(
        max_length=50,
        choices=LocationStatusChoices,
        default=LocationStatusChoices.STATUS_ACTIVE
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='locations',
        blank=True,
        null=True
    )

    # Generic relations
    vlan_groups = GenericRelation(
        to='ipam.VLANGroup',
        content_type_field='scope_type',
        object_id_field='scope_id',
        related_query_name='location'
    )
    contacts = GenericRelation(
        to='tenancy.ContactAssignment'
    )
    images = GenericRelation(
        to='extras.ImageAttachment'
    )

    clone_fields = ('site', 'parent', 'status', 'tenant', 'description')
    prerequisite_models = (
        'dcim.Site',
    )

    class Meta:
        ordering = ['site', 'name']
        constraints = (
            models.UniqueConstraint(
                fields=('site', 'parent', 'name'),
                name='%(app_label)s_%(class)s_parent_name'
            ),
            models.UniqueConstraint(
                fields=('site', 'name'),
                name='%(app_label)s_%(class)s_name',
                condition=Q(parent__isnull=True),
                violation_error_message="A location with this name already exists within the specified site."
            ),
            models.UniqueConstraint(
                fields=('site', 'parent', 'slug'),
                name='%(app_label)s_%(class)s_parent_slug'
            ),
            models.UniqueConstraint(
                fields=('site', 'slug'),
                name='%(app_label)s_%(class)s_slug',
                condition=Q(parent__isnull=True),
                violation_error_message="A location with this slug already exists within the specified site."
            ),
        )

    def get_absolute_url(self):
        return reverse('dcim:location', args=[self.pk])

    def get_status_color(self):
        return LocationStatusChoices.colors.get(self.status)

    def clean(self):
        super().clean()

        # Parent Location (if any) must belong to the same Site
        if self.parent and self.parent.site != self.site:
            raise ValidationError(f"Parent location ({self.parent}) must belong to the same site ({self.site})")
