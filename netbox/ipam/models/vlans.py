from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField, IntegerRangeField
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.backends.postgresql.psycopg_any import NumericRange
from django.utils.translation import gettext_lazy as _

from dcim.models import Interface, Site, SiteGroup
from ipam.choices import *
from ipam.constants import *
from ipam.querysets import VLANGroupQuerySet, VLANQuerySet
from netbox.models import NetBoxModel, OrganizationalModel, PrimaryModel
from utilities.data import check_ranges_overlap, ranges_to_string, ranges_to_string_list
from virtualization.models import VMInterface

__all__ = (
    'VLAN',
    'VLANGroup',
    'VLANTranslationPolicy',
    'VLANTranslationRule',
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
        max_length=100,
        db_collation="natural_sort"
    )
    slug = models.SlugField(
        verbose_name=_('slug'),
        max_length=100
    )
    scope_type = models.ForeignKey(
        to='contenttypes.ContentType',
        on_delete=models.CASCADE,
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
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='vlan_groups',
        blank=True,
        null=True
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

    def clean(self):
        super().clean()
        from netbox.validators import validator_registry
        validator_registry.validate(self)

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
    def vid_ranges_items(self):
        """
        Property that converts VID ranges to a list of string representations.
        """
        return ranges_to_string_list(self.vid_ranges)

    @property
    def vid_ranges_list(self):
        """
        Property that converts VID ranges into a string representation.
        """
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
    qinq_svlan = models.ForeignKey(
        to='self',
        on_delete=models.PROTECT,
        related_name='qinq_cvlans',
        blank=True,
        null=True
    )
    qinq_role = models.CharField(
        verbose_name=_('Q-in-Q role'),
        max_length=50,
        choices=VLANQinQRoleChoices,
        blank=True,
        null=True,
        help_text=_("Customer/service VLAN designation (for Q-in-Q/IEEE 802.1ad)")
    )
    l2vpn_terminations = GenericRelation(
        to='vpn.L2VPNTermination',
        content_type_field='assigned_object_type',
        object_id_field='assigned_object_id',
        related_query_name='vlan'
    )

    objects = VLANQuerySet.as_manager()

    clone_fields = [
        'site', 'group', 'tenant', 'status', 'role', 'description', 'qinq_role', 'qinq_svlan',
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
            models.UniqueConstraint(
                fields=('qinq_svlan', 'vid'),
                name='%(app_label)s_%(class)s_unique_qinq_svlan_vid'
            ),
            models.UniqueConstraint(
                fields=('qinq_svlan', 'name'),
                name='%(app_label)s_%(class)s_unique_qinq_svlan_name'
            ),
        )
        verbose_name = _('VLAN')
        verbose_name_plural = _('VLANs')

    def __str__(self):
        return f'{self.name} ({self.vid})'

    def clean(self):
        super().clean()
        from netbox.validators import validator_registry
        validator_registry.validate(self)

    def get_status_color(self):
        return VLANStatusChoices.colors.get(self.status)

    def get_qinq_role_color(self):
        return VLANQinQRoleChoices.colors.get(self.qinq_role)

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


class VLANTranslationPolicy(PrimaryModel):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        unique=True,
    )

    class Meta:
        verbose_name = _('VLAN translation policy')
        verbose_name_plural = _('VLAN translation policies')
        ordering = ('name',)

    def __str__(self):
        return self.name


class VLANTranslationRule(NetBoxModel):
    policy = models.ForeignKey(
        to=VLANTranslationPolicy,
        related_name='rules',
        on_delete=models.CASCADE,
    )
    description = models.CharField(
        verbose_name=_('description'),
        max_length=200,
        blank=True
    )
    local_vid = models.PositiveSmallIntegerField(
        verbose_name=_('Local VLAN ID'),
        validators=(
            MinValueValidator(VLAN_VID_MIN),
            MaxValueValidator(VLAN_VID_MAX)
        ),
        help_text=_("Numeric VLAN ID (1-4094)")
    )
    remote_vid = models.PositiveSmallIntegerField(
        verbose_name=_('Remote VLAN ID'),
        validators=(
            MinValueValidator(VLAN_VID_MIN),
            MaxValueValidator(VLAN_VID_MAX)
        ),
        help_text=_("Numeric VLAN ID (1-4094)")
    )
    prerequisite_models = (
        'ipam.VLANTranslationPolicy',
    )

    clone_fields = ['policy']

    class Meta:
        verbose_name = _('VLAN translation rule')
        ordering = ('policy', 'local_vid',)
        constraints = (
            models.UniqueConstraint(
                fields=('policy', 'local_vid'),
                name='%(app_label)s_%(class)s_unique_policy_local_vid'
            ),
            models.UniqueConstraint(
                fields=('policy', 'remote_vid'),
                name='%(app_label)s_%(class)s_unique_policy_remote_vid'
            ),
        )

    def __str__(self):
        return f'{self.local_vid} -> {self.remote_vid} ({self.policy})'

    def to_objectchange(self, action):
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.policy
        return objectchange
