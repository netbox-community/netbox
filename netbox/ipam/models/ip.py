import netaddr
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F
from django.db.models.functions import Cast
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from core.models import ObjectType
from ipam.choices import *
from ipam.constants import *
from ipam.fields import IPNetworkField, IPAddressField
from ipam.lookups import Host
from ipam.managers import IPAddressManager
from ipam.querysets import PrefixQuerySet
from ipam.validators import DNSValidator
from netbox.config import get_config
from netbox.models import OrganizationalModel, PrimaryModel

__all__ = (
    'Aggregate',
    'IPAddress',
    'IPRange',
    'Prefix',
    'RIR',
    'Role',
)


class GetAvailablePrefixesMixin:

    def get_available_prefixes(self):
        """
        Return all available prefixes within this Aggregate or Prefix as an IPSet.
        """
        params = {
            'prefix__net_contained': str(self.prefix)
        }
        if hasattr(self, 'vrf'):
            params['vrf'] = self.vrf

        child_prefixes = Prefix.objects.filter(**params).values_list('prefix', flat=True)
        return netaddr.IPSet(self.prefix) - netaddr.IPSet(child_prefixes)

    def get_first_available_prefix(self):
        """
        Return the first available child prefix within the prefix (or None).
        """
        available_prefixes = self.get_available_prefixes()
        if not available_prefixes:
            return None
        return available_prefixes.iter_cidrs()[0]


class RIR(OrganizationalModel):
    """
    A Regional Internet Registry (RIR) is responsible for the allocation of a large portion of the global IP address
    space. This can be an organization like ARIN or RIPE, or a governing standard such as RFC 1918.
    """
    is_private = models.BooleanField(
        default=False,
        verbose_name=_('private'),
        help_text=_('IP space managed by this RIR is considered private')
    )

    class Meta:
        ordering = ('name',)
        verbose_name = _('RIR')
        verbose_name_plural = _('RIRs')

    def get_absolute_url(self):
        return reverse('ipam:rir', args=[self.pk])


class Aggregate(GetAvailablePrefixesMixin, PrimaryModel):
    """
    An aggregate exists at the root level of the IP address space hierarchy in NetBox. Aggregates are used to organize
    the hierarchy and track the overall utilization of available address space. Each Aggregate is assigned to a RIR.
    """
    prefix = IPNetworkField(
        help_text=_("IPv4 or IPv6 network")
    )
    rir = models.ForeignKey(
        to='ipam.RIR',
        on_delete=models.PROTECT,
        related_name='aggregates',
        verbose_name=_('RIR'),
        help_text=_("Regional Internet Registry responsible for this IP space")
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='aggregates',
        blank=True,
        null=True
    )
    date_added = models.DateField(
        verbose_name=_('date added'),
        blank=True,
        null=True
    )

    clone_fields = (
        'rir', 'tenant', 'date_added', 'description',
    )
    prerequisite_models = (
        'ipam.RIR',
    )

    class Meta:
        ordering = ('prefix', 'pk')  # prefix may be non-unique
        verbose_name = _('aggregate')
        verbose_name_plural = _('aggregates')

    def __str__(self):
        return str(self.prefix)

    def get_absolute_url(self):
        return reverse('ipam:aggregate', args=[self.pk])

    def clean(self):
        super().clean()

        if self.prefix:

            # /0 masks are not acceptable
            if self.prefix.prefixlen == 0:
                raise ValidationError({
                    'prefix': _("Cannot create aggregate with /0 mask.")
                })

            # Ensure that the aggregate being added is not covered by an existing aggregate
            covering_aggregates = Aggregate.objects.filter(
                prefix__net_contains_or_equals=str(self.prefix)
            )
            if self.pk:
                covering_aggregates = covering_aggregates.exclude(pk=self.pk)
            if covering_aggregates:
                raise ValidationError({
                    'prefix': _(
                        "Aggregates cannot overlap. {prefix} is already covered by an existing aggregate ({aggregate})."
                    ).format(
                        prefix=self.prefix,
                        aggregate=covering_aggregates[0]
                    )
                })

            # Ensure that the aggregate being added does not cover an existing aggregate
            covered_aggregates = Aggregate.objects.filter(prefix__net_contained=str(self.prefix))
            if self.pk:
                covered_aggregates = covered_aggregates.exclude(pk=self.pk)
            if covered_aggregates:
                raise ValidationError({
                    'prefix': _(
                        "Prefixes cannot overlap aggregates. {prefix} covers an existing aggregate ({aggregate})."
                    ).format(
                        prefix=self.prefix,
                        aggregate=covered_aggregates[0]
                    )
                })

    @property
    def family(self):
        if self.prefix:
            return self.prefix.version
        return None

    def get_child_prefixes(self):
        """
        Return all Prefixes within this Aggregate
        """
        return Prefix.objects.filter(prefix__net_contained=str(self.prefix))

    def get_utilization(self):
        """
        Determine the prefix utilization of the aggregate and return it as a percentage.
        """
        queryset = Prefix.objects.filter(prefix__net_contained_or_equal=str(self.prefix))
        child_prefixes = netaddr.IPSet([p.prefix for p in queryset])
        utilization = float(child_prefixes.size) / self.prefix.size * 100

        return min(utilization, 100)


class Role(OrganizationalModel):
    """
    A Role represents the functional role of a Prefix or VLAN; for example, "Customer," "Infrastructure," or
    "Management."
    """
    weight = models.PositiveSmallIntegerField(
        verbose_name=_('weight'),
        default=1000
    )

    class Meta:
        ordering = ('weight', 'name')
        verbose_name = _('role')
        verbose_name_plural = _('roles')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('ipam:role', args=[self.pk])


class Prefix(GetAvailablePrefixesMixin, PrimaryModel):
    """
    A Prefix represents an IPv4 or IPv6 network, including mask length. Prefixes can optionally be assigned to Sites and
    VRFs. A Prefix must be assigned a status and may optionally be assigned a used-define Role. A Prefix can also be
    assigned to a VLAN where appropriate.
    """
    prefix = IPNetworkField(
        verbose_name=_('prefix'),
        help_text=_('IPv4 or IPv6 network with mask')
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
        verbose_name=_('VRF')
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
        null=True
    )
    status = models.CharField(
        max_length=50,
        choices=PrefixStatusChoices,
        default=PrefixStatusChoices.STATUS_ACTIVE,
        verbose_name=_('status'),
        help_text=_('Operational status of this prefix')
    )
    role = models.ForeignKey(
        to='ipam.Role',
        on_delete=models.SET_NULL,
        related_name='prefixes',
        blank=True,
        null=True,
        help_text=_('The primary function of this prefix')
    )
    is_pool = models.BooleanField(
        verbose_name=_('is a pool'),
        default=False,
        help_text=_('All IP addresses within this prefix are considered usable')
    )
    mark_utilized = models.BooleanField(
        verbose_name=_('mark utilized'),
        default=False,
        help_text=_("Treat as fully utilized")
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

    clone_fields = (
        'site', 'vrf', 'tenant', 'vlan', 'status', 'role', 'is_pool', 'mark_utilized', 'description',
    )

    class Meta:
        ordering = (F('vrf').asc(nulls_first=True), 'prefix', 'pk')  # (vrf, prefix) may be non-unique
        verbose_name = _('prefix')
        verbose_name_plural = _('prefixes')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Cache the original prefix and VRF so we can check if they have changed on post_save
        self._prefix = self.__dict__.get('prefix')
        self._vrf_id = self.__dict__.get('vrf_id')

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
                    'prefix': _("Cannot create prefix with /0 mask.")
                })

            # Enforce unique IP space (if applicable)
            if (self.vrf is None and get_config().ENFORCE_GLOBAL_UNIQUE) or (self.vrf and self.vrf.enforce_unique):
                duplicate_prefixes = self.get_duplicates()
                if duplicate_prefixes:
                    table = _("VRF {vrf}").format(vrf=self.vrf) if self.vrf else _("global table")
                    raise ValidationError({
                        'prefix': _("Duplicate prefix found in {table}: {prefix}").format(
                            table=table,
                            prefix=duplicate_prefixes.first(),
                        )
                    })

    def save(self, *args, **kwargs):

        if isinstance(self.prefix, netaddr.IPNetwork):

            # Clear host bits from prefix
            self.prefix = self.prefix.cidr

        super().save(*args, **kwargs)

    @property
    def family(self):
        return self.prefix.version if self.prefix else None

    @property
    def mask_length(self):
        return self.prefix.prefixlen if self.prefix else None

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

    def get_status_color(self):
        return PrefixStatusChoices.colors.get(self.status)

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

    def get_child_ranges(self):
        """
        Return all IPRanges within this Prefix and VRF.
        """
        return IPRange.objects.filter(
            vrf=self.vrf,
            start_address__net_host_contained=str(self.prefix),
            end_address__net_host_contained=str(self.prefix)
        )

    def get_child_ips(self):
        """
        Return all IPAddresses within this Prefix and VRF. If this Prefix is a container in the global table, return
        child IPAddresses belonging to any VRF.
        """
        if self.vrf is None and self.status == PrefixStatusChoices.STATUS_CONTAINER:
            return IPAddress.objects.filter(address__net_host_contained=str(self.prefix))
        else:
            return IPAddress.objects.filter(address__net_host_contained=str(self.prefix), vrf=self.vrf)

    def get_available_ips(self):
        """
        Return all available IPs within this prefix as an IPSet.
        """
        if self.mark_utilized:
            return netaddr.IPSet()

        prefix = netaddr.IPSet(self.prefix)
        child_ips = netaddr.IPSet([ip.address.ip for ip in self.get_child_ips()])
        child_ranges = []
        for iprange in self.get_child_ranges():
            child_ranges.append(iprange.range)
        available_ips = prefix - child_ips - netaddr.IPSet(child_ranges)

        # IPv6 /127's, pool, or IPv4 /31-/32 sets are fully usable
        if (self.family == 6 and self.prefix.prefixlen >= 127) or self.is_pool or (self.family == 4 and self.prefix.prefixlen >= 31):
            return available_ips

        if self.family == 4:
            # For "normal" IPv4 prefixes, omit first and last addresses
            available_ips -= netaddr.IPSet([
                netaddr.IPAddress(self.prefix.first),
                netaddr.IPAddress(self.prefix.last),
            ])
        else:
            # For IPv6 prefixes, omit the Subnet-Router anycast address
            # per RFC 4291
            available_ips -= netaddr.IPSet([netaddr.IPAddress(self.prefix.first)])
        return available_ips

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
            utilization = float(child_prefixes.size) / self.prefix.size * 100
        else:
            # Compile an IPSet to avoid counting duplicate IPs
            child_ips = netaddr.IPSet(
                [_.range for _ in self.get_child_ranges()] + [_.address.ip for _ in self.get_child_ips()]
            )

            prefix_size = self.prefix.size
            if self.prefix.version == 4 and self.prefix.prefixlen < 31 and not self.is_pool:
                prefix_size -= 2
            utilization = float(child_ips.size) / prefix_size * 100

        return min(utilization, 100)


class IPRange(PrimaryModel):
    """
    A range of IP addresses, defined by start and end addresses.
    """
    start_address = IPAddressField(
        verbose_name=_('start address'),
        help_text=_('IPv4 or IPv6 address (with mask)')
    )
    end_address = IPAddressField(
        verbose_name=_('end address'),
        help_text=_('IPv4 or IPv6 address (with mask)')
    )
    size = models.PositiveIntegerField(
        verbose_name=_('size'),
        editable=False
    )
    vrf = models.ForeignKey(
        to='ipam.VRF',
        on_delete=models.PROTECT,
        related_name='ip_ranges',
        blank=True,
        null=True,
        verbose_name=_('VRF')
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='ip_ranges',
        blank=True,
        null=True
    )
    status = models.CharField(
        verbose_name=_('status'),
        max_length=50,
        choices=IPRangeStatusChoices,
        default=IPRangeStatusChoices.STATUS_ACTIVE,
        help_text=_('Operational status of this range')
    )
    role = models.ForeignKey(
        to='ipam.Role',
        on_delete=models.SET_NULL,
        related_name='ip_ranges',
        blank=True,
        null=True,
        help_text=_('The primary function of this range')
    )
    mark_utilized = models.BooleanField(
        verbose_name=_('mark utilized'),
        default=False,
        help_text=_("Treat as fully utilized")
    )

    clone_fields = (
        'vrf', 'tenant', 'status', 'role', 'description',
    )

    class Meta:
        ordering = (F('vrf').asc(nulls_first=True), 'start_address', 'pk')  # (vrf, start_address) may be non-unique
        verbose_name = _('IP range')
        verbose_name_plural = _('IP ranges')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('ipam:iprange', args=[self.pk])

    def clean(self):
        super().clean()

        if self.start_address and self.end_address:

            # Check that start & end IP versions match
            if self.start_address.version != self.end_address.version:
                raise ValidationError({
                    'end_address': _("Starting and ending IP address versions must match")
                })

            # Check that the start & end IP prefix lengths match
            if self.start_address.prefixlen != self.end_address.prefixlen:
                raise ValidationError({
                    'end_address': _("Starting and ending IP address masks must match")
                })

            # Check that the ending address is greater than the starting address
            if not self.end_address > self.start_address:
                raise ValidationError({
                    'end_address': _(
                        "Ending address must be lower than the starting address ({start_address})"
                    ).format(start_address=self.start_address)
                })

            # Check for overlapping ranges
            overlapping_range = IPRange.objects.exclude(pk=self.pk).filter(vrf=self.vrf).filter(
                Q(start_address__gte=self.start_address, start_address__lte=self.end_address) |  # Starts inside
                Q(end_address__gte=self.start_address, end_address__lte=self.end_address) |  # Ends inside
                Q(start_address__lte=self.start_address, end_address__gte=self.end_address)  # Starts & ends outside
            ).first()
            if overlapping_range:
                raise ValidationError(
                    _("Defined addresses overlap with range {overlapping_range} in VRF {vrf}").format(
                        overlapping_range=overlapping_range,
                        vrf=self.vrf
                    ))

            # Validate maximum size
            MAX_SIZE = 2 ** 32 - 1
            if int(self.end_address.ip - self.start_address.ip) + 1 > MAX_SIZE:
                raise ValidationError(
                    _("Defined range exceeds maximum supported size ({max_size})").format(max_size=MAX_SIZE)
                )

    def save(self, *args, **kwargs):

        # Record the range's size (number of IP addresses)
        self.size = int(self.end_address.ip - self.start_address.ip) + 1

        super().save(*args, **kwargs)

    @property
    def family(self):
        return self.start_address.version if self.start_address else None

    @property
    def range(self):
        return netaddr.IPRange(self.start_address.ip, self.end_address.ip)

    @property
    def mask_length(self):
        return self.start_address.prefixlen if self.start_address else None

    @cached_property
    def name(self):
        """
        Return an efficient string representation of the IP range.
        """
        separator = ':' if self.family == 6 else '.'
        start_chunks = str(self.start_address.ip).split(separator)
        end_chunks = str(self.end_address.ip).split(separator)

        base_chunks = []
        for a, b in zip(start_chunks, end_chunks):
            if a == b:
                base_chunks.append(a)

        base_str = separator.join(base_chunks)
        start_str = separator.join(start_chunks[len(base_chunks):])
        end_str = separator.join(end_chunks[len(base_chunks):])

        return f'{base_str}{separator}{start_str}-{end_str}/{self.start_address.prefixlen}'

    def _set_prefix_length(self, value):
        """
        Expose the IPRange object's prefixlen attribute on the parent model so that it can be manipulated directly,
        e.g. for bulk editing.
        """
        self.start_address.prefixlen = value
        self.end_address.prefixlen = value
    prefix_length = property(fset=_set_prefix_length)

    def get_status_color(self):
        return IPRangeStatusChoices.colors.get(self.status)

    def get_child_ips(self):
        """
        Return all IPAddresses within this IPRange and VRF.
        """
        return IPAddress.objects.filter(
            address__gte=self.start_address,
            address__lte=self.end_address,
            vrf=self.vrf
        )

    def get_available_ips(self):
        """
        Return all available IPs within this range as an IPSet.
        """
        range = netaddr.IPRange(self.start_address.ip, self.end_address.ip)
        child_ips = netaddr.IPSet([ip.address.ip for ip in self.get_child_ips()])

        return netaddr.IPSet(range) - child_ips

    @cached_property
    def first_available_ip(self):
        """
        Return the first available IP within the range (or None).
        """
        available_ips = self.get_available_ips()
        if not available_ips:
            return None

        return '{}/{}'.format(next(available_ips.__iter__()), self.start_address.prefixlen)

    @cached_property
    def utilization(self):
        """
        Determine the utilization of the range and return it as a percentage.
        """
        if self.mark_utilized:
            return 100

        # Compile an IPSet to avoid counting duplicate IPs
        child_count = netaddr.IPSet([
            ip.address.ip for ip in self.get_child_ips()
        ]).size

        return min(float(child_count) / self.size * 100, 100)


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
        verbose_name=_('address'),
        help_text=_('IPv4 or IPv6 address (with mask)')
    )
    vrf = models.ForeignKey(
        to='ipam.VRF',
        on_delete=models.PROTECT,
        related_name='ip_addresses',
        blank=True,
        null=True,
        verbose_name=_('VRF')
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='ip_addresses',
        blank=True,
        null=True
    )
    status = models.CharField(
        verbose_name=_('status'),
        max_length=50,
        choices=IPAddressStatusChoices,
        default=IPAddressStatusChoices.STATUS_ACTIVE,
        help_text=_('The operational status of this IP')
    )
    role = models.CharField(
        verbose_name=_('role'),
        max_length=50,
        choices=IPAddressRoleChoices,
        blank=True,
        help_text=_('The functional role of this IP')
    )
    assigned_object_type = models.ForeignKey(
        to='contenttypes.ContentType',
        limit_choices_to=IPADDRESS_ASSIGNMENT_MODELS,
        on_delete=models.PROTECT,
        related_name='+',
        blank=True,
        null=True
    )
    assigned_object_id = models.PositiveBigIntegerField(
        blank=True,
        null=True
    )
    assigned_object = GenericForeignKey(
        ct_field='assigned_object_type',
        fk_field='assigned_object_id'
    )
    nat_inside = models.ForeignKey(
        to='self',
        on_delete=models.SET_NULL,
        related_name='nat_outside',
        blank=True,
        null=True,
        verbose_name=_('NAT (inside)'),
        help_text=_('The IP for which this address is the "outside" IP')
    )
    dns_name = models.CharField(
        max_length=255,
        blank=True,
        validators=[DNSValidator],
        verbose_name=_('DNS name'),
        help_text=_('Hostname or FQDN (not case-sensitive)')
    )

    objects = IPAddressManager()

    clone_fields = (
        'vrf', 'tenant', 'status', 'role', 'dns_name', 'description',
    )

    class Meta:
        ordering = ('address', 'pk')  # address may be non-unique
        indexes = (
            models.Index(Cast(Host('address'), output_field=IPAddressField()), name='ipam_ipaddress_host'),
            models.Index(fields=('assigned_object_type', 'assigned_object_id')),
        )
        verbose_name = _('IP address')
        verbose_name_plural = _('IP addresses')

    def __str__(self):
        return str(self.address)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Denote the original assigned object (if any) for validation in clean()
        self._original_assigned_object_id = self.__dict__.get('assigned_object_id')
        self._original_assigned_object_type_id = self.__dict__.get('assigned_object_type_id')

    def get_absolute_url(self):
        return reverse('ipam:ipaddress', args=[self.pk])

    def get_duplicates(self):
        return IPAddress.objects.filter(
            vrf=self.vrf,
            address__net_host=str(self.address.ip)
        ).exclude(pk=self.pk)

    def get_next_available_ip(self):
        """
        Return the next available IP address within this IP's network (if any)
        """
        if self.address and self.address.broadcast:
            start_ip = self.address.ip + 1
            end_ip = self.address.broadcast - 1
            if start_ip <= end_ip:
                available_ips = netaddr.IPSet(netaddr.IPRange(start_ip, end_ip))
                available_ips -= netaddr.IPSet([
                    address.ip for address in IPAddress.objects.filter(
                        vrf=self.vrf,
                        address__gt=self.address,
                        address__net_contained_or_equal=self.address.cidr
                    ).values_list('address', flat=True)
                ])
                if available_ips:
                    return next(iter(available_ips))

    def get_related_ips(self):
        """
        Return all IPAddresses belonging to the same VRF.
        """
        return IPAddress.objects.exclude(address=str(self.address)).filter(
            vrf=self.vrf, address__net_contained_or_equal=str(self.address)
        )

    def clean(self):
        super().clean()

        if self.address:

            # /0 masks are not acceptable
            if self.address.prefixlen == 0:
                raise ValidationError({
                    'address': _("Cannot create IP address with /0 mask.")
                })

            # Do not allow assigning a network ID or broadcast address to an interface.
            if self.assigned_object:
                if self.address.ip == self.address.network:
                    msg = _("{ip} is a network ID, which may not be assigned to an interface.").format(
                        ip=self.address.ip
                    )
                    if self.address.version == 4 and self.address.prefixlen not in (31, 32):
                        raise ValidationError(msg)
                    if self.address.version == 6 and self.address.prefixlen not in (127, 128):
                        raise ValidationError(msg)
                if (
                        self.address.version == 4 and self.address.ip == self.address.broadcast and
                        self.address.prefixlen not in (31, 32)
                ):
                    msg = _("{ip} is a broadcast address, which may not be assigned to an interface.").format(
                        ip=self.address.ip
                    )
                    raise ValidationError(msg)

            # Enforce unique IP space (if applicable)
            if (self.vrf is None and get_config().ENFORCE_GLOBAL_UNIQUE) or (self.vrf and self.vrf.enforce_unique):
                duplicate_ips = self.get_duplicates()
                if duplicate_ips and (
                        self.role not in IPADDRESS_ROLES_NONUNIQUE or
                        any(dip.role not in IPADDRESS_ROLES_NONUNIQUE for dip in duplicate_ips)
                ):
                    table = _("VRF {vrf}").format(vrf=self.vrf) if self.vrf else _("global table")
                    raise ValidationError({
                        'address': _("Duplicate IP address found in {table}: {ipaddress}").format(
                            table=table,
                            ipaddress=duplicate_ips.first(),
                        )
                    })

        if self._original_assigned_object_id and self._original_assigned_object_type_id:
            parent = getattr(self.assigned_object, 'parent_object', None)
            ct = ObjectType.objects.get_for_id(self._original_assigned_object_type_id)
            original_assigned_object = ct.get_object_for_this_type(pk=self._original_assigned_object_id)
            original_parent = getattr(original_assigned_object, 'parent_object', None)

            # can't use is_primary_ip as self.assigned_object might be changed
            is_primary = False
            if self.family == 4 and hasattr(original_parent, 'primary_ip4') and original_parent.primary_ip4_id == self.pk:
                is_primary = True
            if self.family == 6 and hasattr(original_parent, 'primary_ip6') and original_parent.primary_ip6_id == self.pk:
                is_primary = True

            if is_primary and (parent != original_parent):
                raise ValidationError(
                    _("Cannot reassign IP address while it is designated as the primary IP for the parent object")
                )

        # Validate IP status selection
        if self.status == IPAddressStatusChoices.STATUS_SLAAC and self.family != 6:
            raise ValidationError({
                'status': _("Only IPv6 addresses can be assigned SLAAC status")
            })

    def save(self, *args, **kwargs):

        # Force dns_name to lowercase
        self.dns_name = self.dns_name.lower()

        super().save(*args, **kwargs)

    def clone(self):
        attrs = super().clone()

        # Populate the address field with the next available IP (if any)
        if next_available_ip := self.get_next_available_ip():
            attrs['address'] = f'{next_available_ip}/{self.address.prefixlen}'

        return attrs

    def to_objectchange(self, action):
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.assigned_object
        return objectchange

    @property
    def family(self):
        if self.address:
            return self.address.version
        return None

    @property
    def is_oob_ip(self):
        if self.assigned_object:
            parent = getattr(self.assigned_object, 'parent_object', None)
            if hasattr(parent, 'oob_ip') and parent.oob_ip_id == self.pk:
                return True
        return False

    @property
    def is_primary_ip(self):
        if self.assigned_object:
            parent = getattr(self.assigned_object, 'parent_object', None)
            if self.family == 4 and hasattr(parent, 'primary_ip4') and parent.primary_ip4_id == self.pk:
                return True
            if self.family == 6 and hasattr(parent, 'primary_ip6') and parent.primary_ip6_id == self.pk:
                return True
        return False

    def _set_mask_length(self, value):
        """
        Expose the IPNetwork object's prefixlen attribute on the parent model so that it can be manipulated directly,
        e.g. for bulk editing.
        """
        if self.address is not None:
            self.address.prefixlen = value
    mask_length = property(fset=_set_mask_length)

    def get_status_color(self):
        return IPAddressStatusChoices.colors.get(self.status)

    def get_role_color(self):
        return IPAddressRoleChoices.colors.get(self.role)
