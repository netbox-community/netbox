from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from mptt.models import TreeForeignKey
from timezone_field import TimeZoneField

from dcim.choices import *
from dcim.constants import *
from django.core.exceptions import ValidationError
from dcim.fields import ASNField
from extras.utils import extras_features
from netbox.models import NestedGroupModel, PrimaryModel
from utilities.fields import NaturalOrderingField
from utilities.querysets import RestrictedQuerySet

__all__ = (
    'Location',
    'Region',
    'Site',
    'SiteGroup',
)


#
# Regions
#

@extras_features('custom_fields', 'export_templates', 'webhooks')
class Region(NestedGroupModel):
    """
    A region represents a geographic collection of sites. For example, you might create regions representing countries,
    states, and/or cities. Regions are recursively nested into a hierarchy: all sites belonging to a child region are
    also considered to be members of its parent and ancestor region(s).
    """
    parent = TreeForeignKey(
        to='self',
        on_delete=models.CASCADE,
        related_name='children',
        blank=True,
        null=True,
        db_index=True
    )
    name = models.CharField(
        max_length=100,
        unique=True
    )
    slug = models.SlugField(
        max_length=100,
        unique=True
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )

    csv_headers = ['name', 'slug', 'parent', 'description']

    def get_absolute_url(self):
        return reverse('dcim:region', args=[self.pk])

    def to_csv(self):
        return (
            self.name,
            self.slug,
            self.parent.name if self.parent else None,
            self.description,
        )

    def get_site_count(self):
        return Site.objects.filter(
            Q(region=self) |
            Q(region__in=self.get_descendants())
        ).count()


#
# Site groups
#

@extras_features('custom_fields', 'export_templates', 'webhooks')
class SiteGroup(NestedGroupModel):
    """
    A site group is an arbitrary grouping of sites. For example, you might have corporate sites and customer sites; and
    within corporate sites you might distinguish between offices and data centers. Like regions, site groups can be
    nested recursively to form a hierarchy.
    """
    parent = TreeForeignKey(
        to='self',
        on_delete=models.CASCADE,
        related_name='children',
        blank=True,
        null=True,
        db_index=True
    )
    name = models.CharField(
        max_length=100,
        unique=True
    )
    slug = models.SlugField(
        max_length=100,
        unique=True
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )

    csv_headers = ['name', 'slug', 'parent', 'description']

    def get_absolute_url(self):
        return reverse('dcim:sitegroup', args=[self.pk])

    def to_csv(self):
        return (
            self.name,
            self.slug,
            self.parent.name if self.parent else None,
            self.description,
        )

    def get_site_count(self):
        return Site.objects.filter(
            Q(group=self) |
            Q(group__in=self.get_descendants())
        ).count()


#
# Sites
#

@extras_features('custom_fields', 'custom_links', 'export_templates', 'webhooks')
class Site(PrimaryModel):
    """
    A Site represents a geographic location within a network; typically a building or campus. The optional facility
    field can be used to include an external designation, such as a data center name (e.g. Equinix SV6).
    """
    name = models.CharField(
        max_length=100,
        unique=True
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
        help_text='Local facility ID or description'
    )
    asn = ASNField(
        blank=True,
        null=True,
        verbose_name='ASN',
        help_text='32-bit autonomous system number'
    )
    time_zone = TimeZoneField(
        blank=True
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )
    physical_address = models.CharField(
        max_length=200,
        blank=True
    )
    shipping_address = models.CharField(
        max_length=200,
        blank=True
    )
    latitude = models.DecimalField(
        max_digits=8,
        decimal_places=6,
        blank=True,
        null=True,
        help_text='GPS coordinate (latitude)'
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        help_text='GPS coordinate (longitude)'
    )
    contact_name = models.CharField(
        max_length=50,
        blank=True
    )
    contact_phone = models.CharField(
        max_length=20,
        blank=True
    )
    contact_email = models.EmailField(
        blank=True,
        verbose_name='Contact E-mail'
    )
    comments = models.TextField(
        blank=True
    )
    images = GenericRelation(
        to='extras.ImageAttachment'
    )

    objects = RestrictedQuerySet.as_manager()

    csv_headers = [
        'name', 'slug', 'status', 'region', 'group', 'tenant', 'facility', 'asn', 'time_zone', 'description',
        'physical_address', 'shipping_address', 'latitude', 'longitude', 'contact_name', 'contact_phone',
        'contact_email', 'comments',
    ]
    clone_fields = [
        'status', 'region', 'group', 'tenant', 'facility', 'asn', 'time_zone', 'description', 'physical_address',
        'shipping_address', 'latitude', 'longitude', 'contact_name', 'contact_phone', 'contact_email',
    ]

    class Meta:
        ordering = ('_name',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('dcim:site', args=[self.pk])

    def to_csv(self):
        return (
            self.name,
            self.slug,
            self.get_status_display(),
            self.region.name if self.region else None,
            self.group.name if self.group else None,
            self.tenant.name if self.tenant else None,
            self.facility,
            self.asn,
            self.time_zone,
            self.description,
            self.physical_address,
            self.shipping_address,
            self.latitude,
            self.longitude,
            self.contact_name,
            self.contact_phone,
            self.contact_email,
            self.comments,
        )

    def get_status_class(self):
        return SiteStatusChoices.CSS_CLASSES.get(self.status)


#
# Locations
#

@extras_features('custom_fields', 'export_templates', 'webhooks')
class Location(NestedGroupModel):
    """
    A Location represents a subgroup of Racks and/or Devices within a Site. A Location may represent a building within a
    site, or a room within a building, for example.
    """
    name = models.CharField(
        max_length=100
    )
    slug = models.SlugField(
        max_length=100
    )
    site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.CASCADE,
        related_name='locations'
    )
    parent = TreeForeignKey(
        to='self',
        on_delete=models.CASCADE,
        related_name='children',
        blank=True,
        null=True,
        db_index=True
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )
    images = GenericRelation(
        to='extras.ImageAttachment'
    )

    csv_headers = ['site', 'parent', 'name', 'slug', 'description']
    clone_fields = ['site', 'parent', 'description']

    class Meta:
        ordering = ['site', 'name']
        unique_together = [
            ['site', 'name'],
            ['site', 'slug'],
        ]

    def get_absolute_url(self):
        return reverse('dcim:location', args=[self.pk])

    def to_csv(self):
        return (
            self.site,
            self.parent.name if self.parent else '',
            self.name,
            self.slug,
            self.description,
        )

    def clean(self):
        super().clean()

        # Parent Location (if any) must belong to the same Site
        if self.parent and self.parent.site != self.site:
            raise ValidationError(f"Parent location ({self.parent}) must belong to the same site ({self.site})")
