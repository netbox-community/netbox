import netaddr
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F
from django.urls import reverse

from dcim.models import Device
from extras.utils import extras_features
from netbox.models import OrganizationalModel, PrimaryModel
from ipam.choices import *
from ipam.constants import *
from ipam.fields import IPNetworkField, IPAddressField
from ipam.managers import IPAddressManager
from ipam.querysets import PrefixQuerySet
from ipam.validators import DNSValidator
from utilities.querysets import RestrictedQuerySet
from virtualization.models import VirtualMachine


__all__ = (
    'Aggregate',
    'IPAddress',
    'Prefix',
    'RIR',
    'Role',
)


@extras_features('custom_fields', 'custom_links', 'export_templates', 'webhooks')
class RIR(OrganizationalModel):
    """
    A Regional Internet Registry (RIR) is responsible for the allocation of a large portion of the global IP address
    space. This can be an organization like ARIN or RIPE, or a governing standard such as RFC 1918.
    """
    name = models.CharField(
        max_length=100,
        unique=True
    )
    slug = models.SlugField(
        max_length=100,
        unique=True
    )
    is_private = models.BooleanField(
        default=False,
        verbose_name='Private',
        help_text='IP space managed by this RIR is considered private'
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )

    objects = RestrictedQuerySet.as_manager()

    csv_headers = ['name', 'slug', 'is_private', 'description']

    class Meta:
        ordering = ['name']
        verbose_name = 'RIR'
        verbose_name_plural = 'RIRs'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('ipam:rir', args=[self.pk])


@extras_features('custom_fields', 'custom_links', 'export_templates', 'tags', 'webhooks')
class Aggregate(PrimaryModel):
    """
    An aggregate exists at the root level of the IP address space hierarchy in NetBox. Aggregates are used to organize
    the hierarchy and track the overall utilization of available address space. Each Aggregate is assigned to a RIR.
    """
    prefix = IPNetworkField()
    rir = models.ForeignKey(
        to='ipam.RIR',
        on_delete=models.PROTECT,
        related_name='aggregates',
        verbose_name='RIR'
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='aggregates',
        blank=True,
        null=True
    )
    date_added = models.DateField(
        blank=True,
        null=True
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )

    objects = RestrictedQuerySet.as_manager()

    csv_headers = ['prefix', 'rir', 'tenant', 'date_added', 'description']
    clone_fields = [
        'rir', 'tenant', 'date_added', 'description',
    ]

    class Meta:
        ordering = ('prefix', 'pk')  # prefix may be non-unique

    def __str__(self):
        return str(self.prefix)

    def get_absolute_url(self):
        return reverse('ipam:aggregate', args=[self.pk])

    def clean(self):
        super().clean()

        if self.prefix:

            # Clear host bits from prefix
            self.prefix = self.prefix.cidr

            # /0 masks are not acceptable
            if self.prefix.prefixlen == 0:
                raise ValidationError({
                    'prefix': "Cannot create aggregate with /0 mask."
                })

            # Ensure that the aggregate being added is not covered by an existing aggregate
            covering_aggregates = Aggregate.objects.filter(
                prefix__net_contains_or_equals=str(self.prefix)
            )
            if self.pk:
                covering_aggregates = covering_aggregates.exclude(pk=self.pk)
            if covering_aggregates:
                raise ValidationError({
                    'prefix': "Aggregates cannot overlap. {} is already covered by an existing aggregate ({}).".format(
                        self.prefix, covering_aggregates[0]
                    )
                })

            # Ensure that the aggregate being added does not cover an existing aggregate
            covered_aggregates = Aggregate.objects.filter(prefix__net_contained=str(self.prefix))
            if self.pk:
                covered_aggregates = covered_aggregates.exclude(pk=self.pk)
            if covered_aggregates:
                raise ValidationError({
                    'prefix': "Aggregates cannot overlap. {} covers an existing aggregate ({}).".format(
                        self.prefix, covered_aggregates[0]
                    )
                })

    @property
    def family(self):
        if self.prefix:
            return self.prefix.version
        return None

    def get_utilization(self):
        """
        Determine the prefix utilization of the aggregate and return it as a percentage.
        """
        queryset = Prefix.objects.filter(prefix__net_contained_or_equal=str(self.prefix))
        child_prefixes = netaddr.IPSet([p.prefix for p in queryset])
        return int(float(child_prefixes.size) / self.prefix.size * 100)


@extras_features('custom_fields', 'custom_links', 'export_templates', 'webhooks')
class Role(OrganizationalModel):
    """
    A Role represents the functional role of a Prefix or VLAN; for example, "Customer," "Infrastructure," or
    "Management."
    """
    name = models.CharField(
        max_length=100,
        unique=True
    )
    slug = models.SlugField(
        max_length=100,
        unique=True
    )
    weight = models.PositiveSmallIntegerField(
        default=1000
    )
    description = models.CharField(
        max_length=200,
        blank=True,
    )

    objects = RestrictedQuerySet.as_manager()

    csv_headers = ['name', 'slug', 'weight', 'description']

    class Meta:
        ordering = ['weight', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('ipam:role', args=[self.pk])


@extras_features('custom_fields', 'custom_links', 'export_templates', 'tags', 'webhooks')
class Prefix(PrimaryModel):
    """
    A Prefix represents an IPv4 or IPv6 network, including mask length. Prefixes can optionally be assigned to Sites and
    VRFs. A Prefix must be assigned a status and may optionally be assigned a used-define Role. A Prefix can also be
    assigned to a VLAN where appropriate.
    """
    prefix = IPNetworkField(
        help_text='IPv4 or IPv6 network with mask'
    )
    site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.PROTECT,
        related_name='prefixes',
        blank=True,
        null=True
    )
    vrf = models.ForeignKey(
        to='ipam.VRF',
        on_delete=models.PROTECT,
        related_name='prefixes',
        blank=True,
        null=True,
        verbose_name='VRF'
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='prefixes',
        blank=True,
        null=True
    )
    vlan = models.ForeignKey(
        to='ipam.VLAN',
        on_delete=models.PROTECT,
        related_name='prefixes',
        blank=True,
        null=True,
        verbose_name='VLAN'
    )
    status = models.CharField(
        max_length=50,
        choices=PrefixStatusChoices,
        default=PrefixStatusChoices.STATUS_ACTIVE,
        verbose_name='Status',
        help_text='Operational status of this prefix'
    )
    role = models.ForeignKey(
        to='ipam.Role',
        on_delete=models.SET_NULL,
        related_name='prefixes',
        blank=True,
        null=True,
        help_text='The primary function of this prefix'
    )
    is_pool = models.BooleanField(
        verbose_name='Is a pool',
        default=False,
        help_text='All IP addresses within this prefix are considered usable'
    )
    mark_utilized = models.BooleanField(
        default=False,
        help_text="Treat as 100% utilized"
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )

    # Cached depth & child counts
    _depth = models.PositiveSmallIntegerField(
        default=0,
        editable=False
    )
    _children = models.PositiveBigIntegerField(
        default=0,
        editable=False
    )

    objects = PrefixQuerySet.as_manager()

    csv_headers = [
        'prefix', 'vrf', 'tenant', 'site', 'vlan_group', 'vlan', 'status', 'role', 'is_pool', 'mark_utilized',
        'description',
    ]
    clone_fields = [
        'site', 'vrf', 'tenant', 'vlan', 'status', 'role', 'is_pool', 'mark_utilized', 'description',
    ]

    class Meta:
        ordering = (F('vrf').asc(nulls_first=True), 'prefix', 'pk')  # (vrf, prefix) may be non-unique
        verbose_name_plural = 'prefixes'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Cache the original prefix and VRF so we can check if they have changed on post_save
        self._prefix = self.prefix
        self._vrf = self.vrf

    def __str__(self):
        return str(self.prefix)

    def get_absolute_url(self):
        return reverse('ipam:prefix', args=[self.pk])

    def clean(self):
        super().clean()

        if self.prefix:

            # /0 masks are not acceptable
            if self.prefix.prefixlen == 0:
                raise ValidationError({
                    'prefix': "Cannot create prefix with /0 mask."
                })

            # Disallow host masks
            if self.prefix.version == 4 and self.prefix.prefixlen == 32:
                raise ValidationError({
                    'prefix': "Cannot create host addresses (/32) as prefixes. Create an IPv4 address instead."
                })
            elif self.prefix.version == 6 and self.prefix.prefixlen == 128:
                raise ValidationError({
                    'prefix': "Cannot create host addresses (/128) as prefixes. Create an IPv6 address instead."
                })

            # Enforce unique IP space (if applicable)
            if (self.vrf is None and settings.ENFORCE_GLOBAL_UNIQUE) or (self.vrf and self.vrf.enforce_unique):
                duplicate_prefixes = self.get_duplicates()
                if duplicate_prefixes:
                    raise ValidationError({
                        'prefix': "Duplicate prefix found in {}: {}".format(
                            "VRF {}".format(self.vrf) if self.vrf else "global table",
                            duplicate_prefixes.first(),
                        )
                    })

    def save(self, *args, **kwargs):

        if isinstance(self.prefix, netaddr.IPNetwork):

            # Clear host bits from prefix
            self.prefix = self.prefix.cidr

        super().save(*args, **kwargs)

    @property
    def family(self):
        if self.prefix:
            return self.prefix.version
        return None

    @property
    def depth(self):
        return self._depth

    @property
    def children(self):
        return self._children

    def _set_prefix_length(self, value):
        """
        Expose the IPNetwork object's prefixlen attribute on the parent model so that it can be manipulated directly,
        e.g. for bulk editing.
        """
        if self.prefix is not None:
            self.prefix.prefixlen = value
    prefix_length = property(fset=_set_prefix_length)

    def get_status_class(self):
        return PrefixStatusChoices.CSS_CLASSES.get(self.status)

    def get_parents(self, include_self=False):
        """
        Return all containing Prefixes in the hierarchy.
        """
        lookup = 'net_contains_or_equals' if include_self else 'net_contains'
        return Prefix.objects.filter(**{
            'vrf': self.vrf,
            f'prefix__{lookup}': self.prefix
        })

    def get_children(self, include_self=False):
        """
        Return all covered Prefixes in the hierarchy.
        """
        lookup = 'net_contained_or_equal' if include_self else 'net_contained'
        return Prefix.objects.filter(**{
            'vrf': self.vrf,
            f'prefix__{lookup}': self.prefix
        })

    def get_duplicates(self):
        return Prefix.objects.filter(vrf=self.vrf, prefix=str(self.prefix)).exclude(pk=self.pk)

    def get_child_prefixes(self):
        """
        Return all Prefixes within this Prefix and VRF. If this Prefix is a container in the global table, return child
        Prefixes belonging to any VRF.
        """
        if self.vrf is None and self.status == PrefixStatusChoices.STATUS_CONTAINER:
            return Prefix.objects.filter(prefix__net_contained=str(self.prefix))
        else:
            return Prefix.objects.filter(prefix__net_contained=str(self.prefix), vrf=self.vrf)

    def get_child_ips(self):
        """
        Return all IPAddresses within this Prefix and VRF. If this Prefix is a container in the global table, return
        child IPAddresses belonging to any VRF.
        """
        if self.vrf is None and self.status == PrefixStatusChoices.STATUS_CONTAINER:
            return IPAddress.objects.filter(address__net_host_contained=str(self.prefix))
        else:
            return IPAddress.objects.filter(address__net_host_contained=str(self.prefix), vrf=self.vrf)

    def get_available_prefixes(self):
        """
        Return all available Prefixes within this prefix as an IPSet.
        """
        prefix = netaddr.IPSet(self.prefix)
        child_prefixes = netaddr.IPSet([child.prefix for child in self.get_child_prefixes()])
        available_prefixes = prefix - child_prefixes

        return available_prefixes

    def get_available_ips(self):
        """
        Return all available IPs within this prefix as an IPSet.
        """
        if self.mark_utilized:
            return list()

        prefix = netaddr.IPSet(self.prefix)
        child_ips = netaddr.IPSet([ip.address.ip for ip in self.get_child_ips()])
        available_ips = prefix - child_ips

        # IPv6, pool, or IPv4 /31 sets are fully usable
        if self.family == 6 or self.is_pool or self.prefix.prefixlen == 31:
            return available_ips

        # For "normal" IPv4 prefixes, omit first and last addresses
        available_ips -= netaddr.IPSet([
            netaddr.IPAddress(self.prefix.first),
            netaddr.IPAddress(self.prefix.last),
        ])

        return available_ips

    def get_first_available_prefix(self):
        """
        Return the first available child prefix within the prefix (or None).
        """
        available_prefixes = self.get_available_prefixes()
        if not available_prefixes:
            return None
        return available_prefixes.iter_cidrs()[0]

    def get_first_available_ip(self):
        """
        Return the first available IP within the prefix (or None).
        """
        available_ips = self.get_available_ips()
        if not available_ips:
            return None
        return '{}/{}'.format(next(available_ips.__iter__()), self.prefix.prefixlen)

    def get_utilization(self):
        """
        Determine the utilization of the prefix and return it as a percentage. For Prefixes with a status of
        "container", calculate utilization based on child prefixes. For all others, count child IP addresses.
        """
        if self.mark_utilized:
            return 100

        if self.status == PrefixStatusChoices.STATUS_CONTAINER:
            queryset = Prefix.objects.filter(
                prefix__net_contained=str(self.prefix),
                vrf=self.vrf
            )
            child_prefixes = netaddr.IPSet([p.prefix for p in queryset])
            return int(float(child_prefixes.size) / self.prefix.size * 100)
        else:
            # Compile an IPSet to avoid counting duplicate IPs
            child_count = netaddr.IPSet([ip.address.ip for ip in self.get_child_ips()]).size
            prefix_size = self.prefix.size
            if self.prefix.version == 4 and self.prefix.prefixlen < 31 and not self.is_pool:
                prefix_size -= 2
            return int(float(child_count) / prefix_size * 100)


@extras_features('custom_fields', 'custom_links', 'export_templates', 'tags', 'webhooks')
class IPAddress(PrimaryModel):
    """
    An IPAddress represents an individual IPv4 or IPv6 address and its mask. The mask length should match what is
    configured in the real world. (Typically, only loopback interfaces are configured with /32 or /128 masks.) Like
    Prefixes, IPAddresses can optionally be assigned to a VRF. An IPAddress can optionally be assigned to an Interface.
    Interfaces can have zero or more IPAddresses assigned to them.

    An IPAddress can also optionally point to a NAT inside IP, designating itself as a NAT outside IP. This is useful,
    for example, when mapping public addresses to private addresses. When an Interface has been assigned an IPAddress
    which has a NAT outside IP, that Interface's Device can use either the inside or outside IP as its primary IP.
    """
    address = IPAddressField(
        help_text='IPv4 or IPv6 address (with mask)'
    )
    vrf = models.ForeignKey(
        to='ipam.VRF',
        on_delete=models.PROTECT,
        related_name='ip_addresses',
        blank=True,
        null=True,
        verbose_name='VRF'
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='ip_addresses',
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=50,
        choices=IPAddressStatusChoices,
        default=IPAddressStatusChoices.STATUS_ACTIVE,
        help_text='The operational status of this IP'
    )
    role = models.CharField(
        max_length=50,
        choices=IPAddressRoleChoices,
        blank=True,
        help_text='The functional role of this IP'
    )
    assigned_object_type = models.ForeignKey(
        to=ContentType,
        limit_choices_to=IPADDRESS_ASSIGNMENT_MODELS,
        on_delete=models.PROTECT,
        related_name='+',
        blank=True,
        null=True
    )
    assigned_object_id = models.PositiveIntegerField(
        blank=True,
        null=True
    )
    assigned_object = GenericForeignKey(
        ct_field='assigned_object_type',
        fk_field='assigned_object_id'
    )
    nat_inside = models.OneToOneField(
        to='self',
        on_delete=models.SET_NULL,
        related_name='nat_outside',
        blank=True,
        null=True,
        verbose_name='NAT (Inside)',
        help_text='The IP for which this address is the "outside" IP'
    )
    dns_name = models.CharField(
        max_length=255,
        blank=True,
        validators=[DNSValidator],
        verbose_name='DNS Name',
        help_text='Hostname or FQDN (not case-sensitive)'
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )

    objects = IPAddressManager()

    csv_headers = [
        'address', 'vrf', 'tenant', 'status', 'role', 'assigned_object_type', 'assigned_object_id', 'is_primary',
        'dns_name', 'description',
    ]
    clone_fields = [
        'vrf', 'tenant', 'status', 'role', 'description',
    ]

    class Meta:
        ordering = ('address', 'pk')  # address may be non-unique
        verbose_name = 'IP address'
        verbose_name_plural = 'IP addresses'

    def __str__(self):
        return str(self.address)

    def get_absolute_url(self):
        return reverse('ipam:ipaddress', args=[self.pk])

    def get_duplicates(self):
        return IPAddress.objects.filter(
            vrf=self.vrf,
            address__net_host=str(self.address.ip)
        ).exclude(pk=self.pk)

    def clean(self):
        super().clean()

        if self.address:

            # /0 masks are not acceptable
            if self.address.prefixlen == 0:
                raise ValidationError({
                    'address': "Cannot create IP address with /0 mask."
                })

            # Enforce unique IP space (if applicable)
            if (self.vrf is None and settings.ENFORCE_GLOBAL_UNIQUE) or (self.vrf and self.vrf.enforce_unique):
                duplicate_ips = self.get_duplicates()
                if duplicate_ips and (
                        self.role not in IPADDRESS_ROLES_NONUNIQUE or
                        any(dip.role not in IPADDRESS_ROLES_NONUNIQUE for dip in duplicate_ips)
                ):
                    raise ValidationError({
                        'address': "Duplicate IP address found in {}: {}".format(
                            "VRF {}".format(self.vrf) if self.vrf else "global table",
                            duplicate_ips.first(),
                        )
                    })

        # Check for primary IP assignment that doesn't match the assigned device/VM
        if self.pk:
            device = Device.objects.filter(Q(primary_ip4=self) | Q(primary_ip6=self)).first()
            if device:
                if getattr(self.assigned_object, 'device', None) != device:
                    raise ValidationError({
                        'interface': f"IP address is primary for device {device} but not assigned to it!"
                    })
            vm = VirtualMachine.objects.filter(Q(primary_ip4=self) | Q(primary_ip6=self)).first()
            if vm:
                if getattr(self.assigned_object, 'virtual_machine', None) != vm:
                    raise ValidationError({
                        'vminterface': f"IP address is primary for virtual machine {vm} but not assigned to it!"
                    })

        # Validate IP status selection
        if self.status == IPAddressStatusChoices.STATUS_SLAAC and self.family != 6:
            raise ValidationError({
                'status': "Only IPv6 addresses can be assigned SLAAC status"
            })

    def save(self, *args, **kwargs):

        # Force dns_name to lowercase
        self.dns_name = self.dns_name.lower()

        super().save(*args, **kwargs)

    def to_objectchange(self, action):
        # Annotate the assigned object, if any
        return super().to_objectchange(action, related_object=self.assigned_object)

    @property
    def family(self):
        if self.address:
            return self.address.version
        return None

    def _set_mask_length(self, value):
        """
        Expose the IPNetwork object's prefixlen attribute on the parent model so that it can be manipulated directly,
        e.g. for bulk editing.
        """
        if self.address is not None:
            self.address.prefixlen = value
    mask_length = property(fset=_set_mask_length)

    def get_status_class(self):
        return IPAddressStatusChoices.CSS_CLASSES.get(self.status)

    def get_role_class(self):
        return IPAddressRoleChoices.CSS_CLASSES.get(self.role)
