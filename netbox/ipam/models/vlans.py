from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse

from dcim.models import Interface
from ipam.choices import *
from ipam.constants import *
from ipam.querysets import VLANQuerySet
from netbox.models import OrganizationalModel, NetBoxModel
from virtualization.models import VMInterface


__all__ = (
    'VLAN',
    'VLANGroup',
)


class VLANGroup(OrganizationalModel):
    """
    A VLAN group is an arbitrary collection of VLANs within which VLAN IDs and names must be unique.
    """
    name = models.CharField(
        max_length=100
    )
    slug = models.SlugField(
        max_length=100
    )
    scope_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=Q(model__in=VLANGROUP_SCOPE_TYPES),
        blank=True,
        null=True
    )
    scope_id = models.PositiveBigIntegerField(
        blank=True,
        null=True
    )
    scope = GenericForeignKey(
        ct_field='scope_type',
        fk_field='scope_id'
    )
    min_vid = models.PositiveSmallIntegerField(
        verbose_name='Minimum VLAN ID',
        default=VLAN_VID_MIN,
        validators=(
            MinValueValidator(VLAN_VID_MIN),
            MaxValueValidator(VLAN_VID_MAX)
        ),
        help_text='Lowest permissible ID of a child VLAN'
    )
    max_vid = models.PositiveSmallIntegerField(
        verbose_name='Maximum VLAN ID',
        default=VLAN_VID_MAX,
        validators=(
            MinValueValidator(VLAN_VID_MIN),
            MaxValueValidator(VLAN_VID_MAX)
        ),
        help_text='Highest permissible ID of a child VLAN'
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )

    class Meta:
        ordering = ('name', 'pk')  # Name may be non-unique
        unique_together = [
            ['scope_type', 'scope_id', 'name'],
            ['scope_type', 'scope_id', 'slug'],
        ]
        verbose_name = 'VLAN group'
        verbose_name_plural = 'VLAN groups'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('ipam:vlangroup', args=[self.pk])

    def clean(self):
        super().clean()

        # Validate scope assignment
        if self.scope_type and not self.scope_id:
            raise ValidationError("Cannot set scope_type without scope_id.")
        if self.scope_id and not self.scope_type:
            raise ValidationError("Cannot set scope_id without scope_type.")

        # Validate min/max child VID limits
        if self.max_vid < self.min_vid:
            raise ValidationError({
                'max_vid': "Maximum child VID must be greater than or equal to minimum child VID"
            })

    def get_available_vids(self):
        """
        Return all available VLANs within this group.
        """
        available_vlans = {vid for vid in range(self.min_vid, self.max_vid + 1)}
        available_vlans -= set(VLAN.objects.filter(group=self).values_list('vid', flat=True))

        return sorted(available_vlans)

    def get_next_available_vid(self):
        """
        Return the first available VLAN ID (1-4094) in the group.
        """
        available_vids = self.get_available_vids()
        if available_vids:
            return available_vids[0]
        return None


class VLAN(NetBoxModel):
    """
    A VLAN is a distinct layer two forwarding domain identified by a 12-bit integer (1-4094). Each VLAN must be assigned
    to a Site, however VLAN IDs need not be unique within a Site. A VLAN may optionally be assigned to a VLANGroup,
    within which all VLAN IDs and names but be unique.

    Like Prefixes, each VLAN is assigned an operational status and optionally a user-defined Role. A VLAN can have zero
    or more Prefixes assigned to it.
    """
    site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.PROTECT,
        related_name='vlans',
        blank=True,
        null=True
    )
    group = models.ForeignKey(
        to='ipam.VLANGroup',
        on_delete=models.PROTECT,
        related_name='vlans',
        blank=True,
        null=True
    )
    vid = models.PositiveSmallIntegerField(
        verbose_name='ID',
        validators=(
            MinValueValidator(VLAN_VID_MIN),
            MaxValueValidator(VLAN_VID_MAX)
        )
    )
    name = models.CharField(
        max_length=64
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='vlans',
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=50,
        choices=VLANStatusChoices,
        default=VLANStatusChoices.STATUS_ACTIVE
    )
    role = models.ForeignKey(
        to='ipam.Role',
        on_delete=models.SET_NULL,
        related_name='vlans',
        blank=True,
        null=True
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )

    objects = VLANQuerySet.as_manager()

    clone_fields = [
        'site', 'group', 'tenant', 'status', 'role', 'description',
    ]

    class Meta:
        ordering = ('site', 'group', 'vid', 'pk')  # (site, group, vid) may be non-unique
        unique_together = [
            ['group', 'vid'],
            ['group', 'name'],
        ]
        verbose_name = 'VLAN'
        verbose_name_plural = 'VLANs'

    def __str__(self):
        return f'{self.name} ({self.vid})'

    def get_absolute_url(self):
        return reverse('ipam:vlan', args=[self.pk])

    def clean(self):
        super().clean()

        # Validate VLAN group (if assigned)
        if self.group and self.site and self.group.scope != self.site:
            raise ValidationError({
                'group': f"VLAN is assigned to group {self.group} (scope: {self.group.scope}); cannot also assign to "
                         f"site {self.site}."
            })

        # Validate group min/max VIDs
        if self.group and not self.group.min_vid <= self.vid <= self.group.max_vid:
            raise ValidationError({
                'vid': f"VID must be between {self.group.min_vid} and {self.group.max_vid} for VLANs in group "
                       f"{self.group}"
            })

    def get_status_class(self):
        return VLANStatusChoices.colors.get(self.status, 'secondary')

    def get_interfaces(self):
        # Return all device interfaces assigned to this VLAN
        return Interface.objects.filter(
            Q(untagged_vlan_id=self.pk) |
            Q(tagged_vlans=self.pk)
        ).distinct()

    def get_vminterfaces(self):
        # Return all VM interfaces assigned to this VLAN
        return VMInterface.objects.filter(
            Q(untagged_vlan_id=self.pk) |
            Q(tagged_vlans=self.pk)
        ).distinct()
