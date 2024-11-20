from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.postgres.fields import ArrayField, IntegerRangeField
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.backends.postgresql.psycopg_any import NumericRange
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from dcim.models import Interface
from ipam.choices import *
from ipam.constants import *
from ipam.querysets import VLANQuerySet, VLANGroupQuerySet
from netbox.models import OrganizationalModel, PrimaryModel
from utilities.data import check_ranges_overlap, ranges_to_string
from virtualization.models import VMInterface

__all__ = (
    'VLAN',
    'VLANGroup',
)


def default_vid_ranges():
    return [
        NumericRange(VLAN_VID_MIN, VLAN_VID_MAX, bounds='[]')
    ]


class VLANGroup(OrganizationalModel):
    """
    A VLAN group is an arbitrary collection of VLANs within which VLAN IDs and names must be unique. Each group must
     define one or more ranges of valid VLAN IDs, and may be assigned a specific scope.
    """
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100
    )
    slug = models.SlugField(
        verbose_name=_('slug'),
        max_length=100
    )
    scope_type = models.ForeignKey(
        to='contenttypes.ContentType',
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
    vid_ranges = ArrayField(
        IntegerRangeField(),
        verbose_name=_('VLAN ID ranges'),
        default=default_vid_ranges
    )
    _total_vlan_ids = models.PositiveBigIntegerField(
        default=VLAN_VID_MAX - VLAN_VID_MIN + 1
    )

    objects = VLANGroupQuerySet.as_manager()

    class Meta:
        ordering = ('name', 'pk')  # Name may be non-unique
        indexes = (
            models.Index(fields=('scope_type', 'scope_id')),
        )
        constraints = (
            models.UniqueConstraint(
                fields=('scope_type', 'scope_id', 'name'),
                name='%(app_label)s_%(class)s_unique_scope_name'
            ),
            models.UniqueConstraint(
                fields=('scope_type', 'scope_id', 'slug'),
                name='%(app_label)s_%(class)s_unique_scope_slug'
            ),
        )
        verbose_name = _('VLAN group')
        verbose_name_plural = _('VLAN groups')

    def get_absolute_url(self):
        return reverse('ipam:vlangroup', args=[self.pk])

    def clean(self):
        super().clean()

        # Validate scope assignment
        if self.scope_type and not self.scope_id:
            raise ValidationError(_("Cannot set scope_type without scope_id."))
        if self.scope_id and not self.scope_type:
            raise ValidationError(_("Cannot set scope_id without scope_type."))

        # Validate VID ranges
        for vid_range in self.vid_ranges:
            lower_vid = vid_range.lower if vid_range.lower_inc else vid_range.lower + 1
            upper_vid = vid_range.upper if vid_range.upper_inc else vid_range.upper - 1
            if lower_vid < VLAN_VID_MIN:
                raise ValidationError({
                    'vid_ranges': _("Starting VLAN ID in range ({value}) cannot be less than {minimum}").format(
                        value=lower_vid, minimum=VLAN_VID_MIN
                    )
                })
            if upper_vid > VLAN_VID_MAX:
                raise ValidationError({
                    'vid_ranges': _("Ending VLAN ID in range ({value}) cannot exceed {maximum}").format(
                        value=upper_vid, maximum=VLAN_VID_MAX
                    )
                })
            if lower_vid > upper_vid:
                raise ValidationError({
                    'vid_ranges': _(
                        "Ending VLAN ID in range must be greater than or equal to the starting VLAN ID ({range})"
                    ).format(range=f'{lower_vid}-{upper_vid}')
                })

        # Check for overlapping VID ranges
        if self.vid_ranges and check_ranges_overlap(self.vid_ranges):
            raise ValidationError({'vid_ranges': _("Ranges cannot overlap.")})

    def save(self, *args, **kwargs):
        self._total_vlan_ids = 0
        for vid_range in self.vid_ranges:
            self._total_vlan_ids += vid_range.upper - vid_range.lower + 1

        super().save(*args, **kwargs)

    def get_available_vids(self):
        """
        Return all available VLANs within this group.
        """
        available_vlans = set()
        for vlan_range in self.vid_ranges:
            available_vlans = available_vlans.union({
                vid for vid in range(vlan_range.lower, vlan_range.upper)
            })
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

    def get_child_vlans(self):
        """
        Return all VLANs within this group.
        """
        return VLAN.objects.filter(group=self).order_by('vid')

    @property
    def vid_ranges_list(self):
        return ranges_to_string(self.vid_ranges)


class VLAN(PrimaryModel):
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
        null=True,
        help_text=_("The specific site to which this VLAN is assigned (if any)")
    )
    group = models.ForeignKey(
        to='ipam.VLANGroup',
        on_delete=models.PROTECT,
        related_name='vlans',
        blank=True,
        null=True,
        help_text=_("VLAN group (optional)")
    )
    vid = models.PositiveSmallIntegerField(
        verbose_name=_('VLAN ID'),
        validators=(
            MinValueValidator(VLAN_VID_MIN),
            MaxValueValidator(VLAN_VID_MAX)
        ),
        help_text=_("Numeric VLAN ID (1-4094)")
    )
    name = models.CharField(
        verbose_name=_('name'),
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
        verbose_name=_('status'),
        max_length=50,
        choices=VLANStatusChoices,
        default=VLANStatusChoices.STATUS_ACTIVE,
        help_text=_("Operational status of this VLAN")
    )
    role = models.ForeignKey(
        to='ipam.Role',
        on_delete=models.SET_NULL,
        related_name='vlans',
        blank=True,
        null=True,
        help_text=_("The primary function of this VLAN")
    )
    l2vpn_terminations = GenericRelation(
        to='vpn.L2VPNTermination',
        content_type_field='assigned_object_type',
        object_id_field='assigned_object_id',
        related_query_name='vlan'
    )

    objects = VLANQuerySet.as_manager()

    clone_fields = [
        'site', 'group', 'tenant', 'status', 'role', 'description',
    ]

    class Meta:
        ordering = ('site', 'group', 'vid', 'pk')  # (site, group, vid) may be non-unique
        constraints = (
            models.UniqueConstraint(
                fields=('group', 'vid'),
                name='%(app_label)s_%(class)s_unique_group_vid'
            ),
            models.UniqueConstraint(
                fields=('group', 'name'),
                name='%(app_label)s_%(class)s_unique_group_name'
            ),
        )
        verbose_name = _('VLAN')
        verbose_name_plural = _('VLANs')

    def __str__(self):
        return f'{self.name} ({self.vid})'

    def get_absolute_url(self):
        return reverse('ipam:vlan', args=[self.pk])

    def clean(self):
        super().clean()

        # Validate VLAN group (if assigned)
        if self.group and self.site and self.group.scope != self.site:
            raise ValidationError(
                _(
                    "VLAN is assigned to group {group} (scope: {scope}); cannot also assign to site {site}."
                ).format(group=self.group, scope=self.group.scope, site=self.site)
            )

        # Check that the VLAN ID is permitted in the assigned group (if any)
        if self.group:
            if not any([self.vid in r for r in self.group.vid_ranges]):
                raise ValidationError({
                    'vid': _(
                        "VID must be in ranges {ranges} for VLANs in group {group}"
                    ).format(ranges=ranges_to_string(self.group.vid_ranges), group=self.group)
                })

    def get_status_color(self):
        return VLANStatusChoices.colors.get(self.status)

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

    @property
    def l2vpn_termination(self):
        return self.l2vpn_terminations.first()
