from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey
from taggit.managers import TaggableManager
from timezone_field import TimeZoneField

from dcim.choices import *
from dcim.constants import *
from django.core.exceptions import ValidationError
from dcim.fields import ASNField
from extras.models import ChangeLoggedModel, CustomFieldModel, ObjectChange, TaggedItem
from extras.utils import extras_features
from utilities.fields import NaturalOrderingField
from utilities.querysets import RestrictedQuerySet
from utilities.mptt import TreeManager
from utilities.utils import serialize_object

__all__ = (
    'Region',
    'Site',
)


#
# Regions
#

@extras_features('export_templates', 'webhooks')
class Region(MPTTModel, ChangeLoggedModel):
    """
    Sites can be grouped within geographic Regions.
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

    objects = TreeManager()

    csv_headers = ['name', 'slug', 'parent', 'description']

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "{}?region={}".format(reverse('dcim:site_list'), self.slug)

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

    def to_objectchange(self, action):
        # Remove MPTT-internal fields
        return ObjectChange(
            changed_object=self,
            object_repr=str(self),
            action=action,
            object_data=serialize_object(self, exclude=['level', 'lft', 'rght', 'tree_id'])
        )

    def clean(self):
        super().clean()

        # An MPTT model cannot be its own parent
        if self.pk and self.parent_id == self.pk:
            raise ValidationError({
                "parent": "Cannot assign self as parent."
            })


#
# Sites
#

@extras_features('custom_fields', 'custom_links', 'export_templates', 'webhooks')
class Site(ChangeLoggedModel, CustomFieldModel):
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
    tags = TaggableManager(through=TaggedItem)

    objects = RestrictedQuerySet.as_manager()

    csv_headers = [
        'name', 'slug', 'status', 'region', 'tenant', 'facility', 'asn', 'time_zone', 'description', 'physical_address',
        'shipping_address', 'latitude', 'longitude', 'contact_name', 'contact_phone', 'contact_email', 'comments',
    ]
    clone_fields = [
        'status', 'region', 'tenant', 'facility', 'asn', 'time_zone', 'description', 'physical_address',
        'shipping_address', 'latitude', 'longitude', 'contact_name', 'contact_phone', 'contact_email',
    ]

    class Meta:
        ordering = ('_name',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('dcim:site', args=[self.slug])

    def to_csv(self):
        return (
            self.name,
            self.slug,
            self.get_status_display(),
            self.region.name if self.region else None,
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
