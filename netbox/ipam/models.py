from __future__ import unicode_literals

import netaddr
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.expressions import RawSQL
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible

from dcim.models import Interface
from extras.models import CustomFieldModel, CustomFieldValue
from tenancy.models import Tenant
from utilities.models import CreatedUpdatedModel
from utilities.utils import csv_format
from .constants import *
from .fields import IPNetworkField, IPAddressField
from .querysets import PrefixQuerySet


@python_2_unicode_compatible
class VRF(CreatedUpdatedModel, CustomFieldModel):
    """
    A virtual routing and forwarding (VRF) table represents a discrete layer three forwarding domain (e.g. a routing
    table). Prefixes and IPAddresses can optionally be assigned to VRFs. (Prefixes and IPAddresses not assigned to a VRF
    are said to exist in the "global" table.)
    """
    name = models.CharField(max_length=50)
    rd = models.CharField(max_length=21, unique=True, verbose_name='Route distinguisher')
    tenant = models.ForeignKey(Tenant, related_name='vrfs', blank=True, null=True, on_delete=models.PROTECT)
    enforce_unique = models.BooleanField(default=True, verbose_name='Enforce unique space',
                                         help_text="Prevent duplicate prefixes/IP addresses within this VRF")
    description = models.CharField(max_length=100, blank=True)
    custom_field_values = GenericRelation(CustomFieldValue, content_type_field='obj_type', object_id_field='obj_id')

    csv_headers = ['name', 'rd', 'tenant', 'enforce_unique', 'description']

    class Meta:
        ordering = ['name']
        verbose_name = 'VRF'
        verbose_name_plural = 'VRFs'

    def __str__(self):
        return self.display_name or super(VRF, self).__str__()

    def get_absolute_url(self):
        return reverse('ipam:vrf', args=[self.pk])

    def to_csv(self):
        return csv_format([
            self.name,
            self.rd,
            self.tenant.name if self.tenant else None,
            self.enforce_unique,
            self.description,
        ])

    @property
    def display_name(self):
        if self.name and self.rd:
            return "{} ({})".format(self.name, self.rd)
        return None


@python_2_unicode_compatible
class RIR(models.Model):
    """
    A Regional Internet Registry (RIR) is responsible for the allocation of a large portion of the global IP address
    space. This can be an organization like ARIN or RIPE, or a governing standard such as RFC 1918.
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    is_private = models.BooleanField(default=False, verbose_name='Private',
                                     help_text='IP space managed by this RIR is considered private')

    class Meta:
        ordering = ['name']
        verbose_name = 'RIR'
        verbose_name_plural = 'RIRs'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "{}?rir={}".format(reverse('ipam:aggregate_list'), self.slug)


@python_2_unicode_compatible
class Aggregate(CreatedUpdatedModel, CustomFieldModel):
    """
    An aggregate exists at the root level of the IP address space hierarchy in NetBox. Aggregates are used to organize
    the hierarchy and track the overall utilization of available address space. Each Aggregate is assigned to a RIR.
    """
    family = models.PositiveSmallIntegerField(choices=AF_CHOICES)
    prefix = IPNetworkField()
    rir = models.ForeignKey('RIR', related_name='aggregates', on_delete=models.PROTECT, verbose_name='RIR')
    date_added = models.DateField(blank=True, null=True)
    description = models.CharField(max_length=100, blank=True)
    custom_field_values = GenericRelation(CustomFieldValue, content_type_field='obj_type', object_id_field='obj_id')

    csv_headers = ['prefix', 'rir', 'date_added', 'description']

    class Meta:
        ordering = ['family', 'prefix']

    def __str__(self):
        return str(self.prefix)

    def get_absolute_url(self):
        return reverse('ipam:aggregate', args=[self.pk])

    def clean(self):

        if self.prefix:

            # Clear host bits from prefix
            self.prefix = self.prefix.cidr

            # Ensure that the aggregate being added is not covered by an existing aggregate
            covering_aggregates = Aggregate.objects.filter(prefix__net_contains_or_equals=str(self.prefix))
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

    def save(self, *args, **kwargs):
        if self.prefix:
            # Infer address family from IPNetwork object
            self.family = self.prefix.version
        super(Aggregate, self).save(*args, **kwargs)

    def to_csv(self):
        return csv_format([
            self.prefix,
            self.rir.name,
            self.date_added.isoformat() if self.date_added else None,
            self.description,
        ])

    def get_utilization(self):
        """
        Determine the prefix utilization of the aggregate and return it as a percentage.
        """
        queryset = Prefix.objects.filter(prefix__net_contained_or_equal=str(self.prefix))
        child_prefixes = netaddr.IPSet([p.prefix for p in queryset])
        return int(float(child_prefixes.size) / self.prefix.size * 100)


@python_2_unicode_compatible
class Role(models.Model):
    """
    A Role represents the functional role of a Prefix or VLAN; for example, "Customer," "Infrastructure," or
    "Management."
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    weight = models.PositiveSmallIntegerField(default=1000)

    class Meta:
        ordering = ['weight', 'name']

    def __str__(self):
        return self.name

    @property
    def count_prefixes(self):
        return self.prefixes.count()

    @property
    def count_vlans(self):
        return self.vlans.count()


@python_2_unicode_compatible
class Prefix(CreatedUpdatedModel, CustomFieldModel):
    """
    A Prefix represents an IPv4 or IPv6 network, including mask length. Prefixes can optionally be assigned to Sites and
    VRFs. A Prefix must be assigned a status and may optionally be assigned a used-define Role. A Prefix can also be
    assigned to a VLAN where appropriate.
    """
    family = models.PositiveSmallIntegerField(choices=AF_CHOICES, editable=False)
    prefix = IPNetworkField(help_text="IPv4 or IPv6 network with mask")
    site = models.ForeignKey('dcim.Site', related_name='prefixes', on_delete=models.PROTECT, blank=True, null=True)
    vrf = models.ForeignKey('VRF', related_name='prefixes', on_delete=models.PROTECT, blank=True, null=True,
                            verbose_name='VRF')
    tenant = models.ForeignKey(Tenant, related_name='prefixes', blank=True, null=True, on_delete=models.PROTECT)
    vlan = models.ForeignKey('VLAN', related_name='prefixes', on_delete=models.PROTECT, blank=True, null=True,
                             verbose_name='VLAN')
    status = models.PositiveSmallIntegerField('Status', choices=PREFIX_STATUS_CHOICES, default=PREFIX_STATUS_ACTIVE,
                                              help_text="Operational status of this prefix")
    role = models.ForeignKey('Role', related_name='prefixes', on_delete=models.SET_NULL, blank=True, null=True,
                             help_text="The primary function of this prefix")
    is_pool = models.BooleanField(verbose_name='Is a pool', default=False,
                                  help_text="All IP addresses within this prefix are considered usable")
    description = models.CharField(max_length=100, blank=True)
    custom_field_values = GenericRelation(CustomFieldValue, content_type_field='obj_type', object_id_field='obj_id')

    objects = PrefixQuerySet.as_manager()

    csv_headers = [
        'prefix', 'vrf', 'tenant', 'site', 'vlan_group', 'vlan_vid', 'status', 'role', 'is_pool', 'description',
    ]

    class Meta:
        ordering = ['vrf', 'family', 'prefix']
        verbose_name_plural = 'prefixes'

    def __str__(self):
        return str(self.prefix)

    def get_absolute_url(self):
        return reverse('ipam:prefix', args=[self.pk])

    def clean(self):

        if self.prefix:

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
        if self.prefix:
            # Clear host bits from prefix
            self.prefix = self.prefix.cidr
            # Infer address family from IPNetwork object
            self.family = self.prefix.version
        super(Prefix, self).save(*args, **kwargs)

    def to_csv(self):
        return csv_format([
            self.prefix,
            self.vrf.rd if self.vrf else None,
            self.tenant.name if self.tenant else None,
            self.site.name if self.site else None,
            self.vlan.group.name if self.vlan and self.vlan.group else None,
            self.vlan.vid if self.vlan else None,
            self.get_status_display(),
            self.role.name if self.role else None,
            self.is_pool,
            self.description,
        ])

    def get_status_class(self):
        return STATUS_CHOICE_CLASSES[self.status]

    def get_duplicates(self):
        return Prefix.objects.filter(vrf=self.vrf, prefix=str(self.prefix)).exclude(pk=self.pk)

    def get_child_ips(self):
        """
        Return all IPAddresses within this Prefix.
        """
        return IPAddress.objects.filter(address__net_host_contained=str(self.prefix), vrf=self.vrf)

    def get_available_ips(self):
        """
        Return all available IPs within this prefix as an IPSet.
        """
        prefix = netaddr.IPSet(self.prefix)
        child_ips = netaddr.IPSet([ip.address.ip for ip in self.get_child_ips()])
        available_ips = prefix - child_ips

        # Remove unusable IPs from non-pool prefixes
        if not self.is_pool:
            available_ips -= netaddr.IPSet([
                netaddr.IPAddress(self.prefix.first),
                netaddr.IPAddress(self.prefix.last),
            ])

        return available_ips

    def get_first_available_ip(self):
        """
        Return the first available IP within the prefix (or None).
        """
        available_ips = self.get_available_ips()
        if available_ips:
            return '{}/{}'.format(next(available_ips.__iter__()), self.prefix.prefixlen)
        else:
            return None

    def get_utilization(self):
        """
        Determine the utilization of the prefix and return it as a percentage. For Prefixes with a status of
        "container", calculate utilization based on child prefixes. For all others, count child IP addresses.
        """
        if self.status == PREFIX_STATUS_CONTAINER:
            queryset = Prefix.objects.filter(prefix__net_contained=str(self.prefix), vrf=self.vrf)
            child_prefixes = netaddr.IPSet([p.prefix for p in queryset])
            return int(float(child_prefixes.size) / self.prefix.size * 100)
        else:
            child_count = self.get_child_ips().count()
            prefix_size = self.prefix.size
            if self.family == 4 and self.prefix.prefixlen < 31 and not self.is_pool:
                prefix_size -= 2
            return int(float(child_count) / prefix_size * 100)

    @property
    def new_subnet(self):
        if self.family == 4:
            if self.prefix.prefixlen <= 30:
                return netaddr.IPNetwork('{}/{}'.format(self.prefix.network, self.prefix.prefixlen + 1))
            return None
        if self.family == 6:
            if self.prefix.prefixlen <= 126:
                return netaddr.IPNetwork('{}/{}'.format(self.prefix.network, self.prefix.prefixlen + 1))
            return None


class IPAddressManager(models.Manager):

    def get_queryset(self):
        """
        By default, PostgreSQL will order INETs with shorter (larger) prefix lengths ahead of those with longer
        (smaller) masks. This makes no sense when ordering IPs, which should be ordered solely by family and host
        address. We can use HOST() to extract just the host portion of the address (ignoring its mask), but we must
        then re-cast this value to INET() so that records will be ordered properly. We are essentially re-casting each
        IP address as a /32 or /128.
        """
        qs = super(IPAddressManager, self).get_queryset()
        return qs.annotate(host=RawSQL('INET(HOST(ipam_ipaddress.address))', [])).order_by('family', 'host')


@python_2_unicode_compatible
class IPAddress(CreatedUpdatedModel, CustomFieldModel):
    """
    An IPAddress represents an individual IPv4 or IPv6 address and its mask. The mask length should match what is
    configured in the real world. (Typically, only loopback interfaces are configured with /32 or /128 masks.) Like
    Prefixes, IPAddresses can optionally be assigned to a VRF. An IPAddress can optionally be assigned to an Interface.
    Interfaces can have zero or more IPAddresses assigned to them.

    An IPAddress can also optionally point to a NAT inside IP, designating itself as a NAT outside IP. This is useful,
    for example, when mapping public addresses to private addresses. When an Interface has been assigned an IPAddress
    which has a NAT outside IP, that Interface's Device can use either the inside or outside IP as its primary IP.
    """
    family = models.PositiveSmallIntegerField(choices=AF_CHOICES, editable=False)
    address = IPAddressField(help_text="IPv4 or IPv6 address (with mask)")
    vrf = models.ForeignKey('VRF', related_name='ip_addresses', on_delete=models.PROTECT, blank=True, null=True,
                            verbose_name='VRF')
    tenant = models.ForeignKey(Tenant, related_name='ip_addresses', blank=True, null=True, on_delete=models.PROTECT)
    status = models.PositiveSmallIntegerField(
        'Status', choices=IPADDRESS_STATUS_CHOICES, default=IPADDRESS_STATUS_ACTIVE,
        help_text='The operational status of this IP'
    )
    role = models.PositiveSmallIntegerField(
        'Role', choices=IPADDRESS_ROLE_CHOICES, blank=True, null=True, help_text='The functional role of this IP'
    )
    interface = models.ForeignKey(Interface, related_name='ip_addresses', on_delete=models.CASCADE, blank=True,
                                  null=True)
    nat_inside = models.OneToOneField('self', related_name='nat_outside', on_delete=models.SET_NULL, blank=True,
                                      null=True, verbose_name='NAT (Inside)',
                                      help_text="The IP for which this address is the \"outside\" IP")
    description = models.CharField(max_length=100, blank=True)
    custom_field_values = GenericRelation(CustomFieldValue, content_type_field='obj_type', object_id_field='obj_id')

    objects = IPAddressManager()

    csv_headers = [
        'address', 'vrf', 'tenant', 'status', 'role', 'device', 'virtual_machine', 'interface_name', 'is_primary',
        'description',
    ]

    class Meta:
        ordering = ['family', 'address']
        verbose_name = 'IP address'
        verbose_name_plural = 'IP addresses'

    def __str__(self):
        return str(self.address)

    def get_absolute_url(self):
        return reverse('ipam:ipaddress', args=[self.pk])

    def get_duplicates(self):
        return IPAddress.objects.filter(vrf=self.vrf, address__net_host=str(self.address.ip)).exclude(pk=self.pk)

    def clean(self):

        if self.address:

            # Enforce unique IP space (if applicable)
            if (self.vrf is None and settings.ENFORCE_GLOBAL_UNIQUE) or (self.vrf and self.vrf.enforce_unique):
                duplicate_ips = self.get_duplicates()
                if duplicate_ips:
                    raise ValidationError({
                        'address': "Duplicate IP address found in {}: {}".format(
                            "VRF {}".format(self.vrf) if self.vrf else "global table",
                            duplicate_ips.first(),
                        )
                    })

    def save(self, *args, **kwargs):
        if self.address:
            # Infer address family from IPAddress object
            self.family = self.address.version
        super(IPAddress, self).save(*args, **kwargs)

    def to_csv(self):

        # Determine if this IP is primary for a Device
        if self.family == 4 and getattr(self, 'primary_ip4_for', False):
            is_primary = True
        elif self.family == 6 and getattr(self, 'primary_ip6_for', False):
            is_primary = True
        else:
            is_primary = False

        return csv_format([
            self.address,
            self.vrf.rd if self.vrf else None,
            self.tenant.name if self.tenant else None,
            self.get_status_display(),
            self.get_role_display(),
            self.device.identifier if self.device else None,
            self.virtual_machine.name if self.virtual_machine else None,
            self.interface.name if self.interface else None,
            is_primary,
            self.description,
        ])

    @property
    def device(self):
        if self.interface:
            return self.interface.device
        return None

    @property
    def virtual_machine(self):
        if self.interface:
            return self.interface.virtual_machine
        return None

    def get_status_class(self):
        return STATUS_CHOICE_CLASSES[self.status]

    def get_role_class(self):
        return ROLE_CHOICE_CLASSES[self.role]


@python_2_unicode_compatible
class VLANGroup(models.Model):
    """
    A VLAN group is an arbitrary collection of VLANs within which VLAN IDs and names must be unique.
    """
    name = models.CharField(max_length=50)
    slug = models.SlugField()
    site = models.ForeignKey('dcim.Site', related_name='vlan_groups', on_delete=models.PROTECT, blank=True, null=True)

    class Meta:
        ordering = ['site', 'name']
        unique_together = [
            ['site', 'name'],
            ['site', 'slug'],
        ]
        verbose_name = 'VLAN group'
        verbose_name_plural = 'VLAN groups'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "{}?group_id={}".format(reverse('ipam:vlan_list'), self.pk)

    def get_next_available_vid(self):
        """
        Return the first available VLAN ID (1-4094) in the group.
        """
        vids = [vlan['vid'] for vlan in self.vlans.order_by('vid').values('vid')]
        for i in range(1, 4095):
            if i not in vids:
                return i
        return None


@python_2_unicode_compatible
class VLAN(CreatedUpdatedModel, CustomFieldModel):
    """
    A VLAN is a distinct layer two forwarding domain identified by a 12-bit integer (1-4094). Each VLAN must be assigned
    to a Site, however VLAN IDs need not be unique within a Site. A VLAN may optionally be assigned to a VLANGroup,
    within which all VLAN IDs and names but be unique.

    Like Prefixes, each VLAN is assigned an operational status and optionally a user-defined Role. A VLAN can have zero
    or more Prefixes assigned to it.
    """
    site = models.ForeignKey('dcim.Site', related_name='vlans', on_delete=models.PROTECT, blank=True, null=True)
    group = models.ForeignKey('VLANGroup', related_name='vlans', blank=True, null=True, on_delete=models.PROTECT)
    vid = models.PositiveSmallIntegerField(verbose_name='ID', validators=[
        MinValueValidator(1),
        MaxValueValidator(4094)
    ])
    name = models.CharField(max_length=64)
    tenant = models.ForeignKey(Tenant, related_name='vlans', blank=True, null=True, on_delete=models.PROTECT)
    status = models.PositiveSmallIntegerField('Status', choices=VLAN_STATUS_CHOICES, default=1)
    role = models.ForeignKey('Role', related_name='vlans', on_delete=models.SET_NULL, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True)
    custom_field_values = GenericRelation(CustomFieldValue, content_type_field='obj_type', object_id_field='obj_id')

    csv_headers = ['site', 'group_name', 'vid', 'name', 'tenant', 'status', 'role', 'description']

    class Meta:
        ordering = ['site', 'group', 'vid']
        unique_together = [
            ['group', 'vid'],
            ['group', 'name'],
        ]
        verbose_name = 'VLAN'
        verbose_name_plural = 'VLANs'

    def __str__(self):
        return self.display_name or super(VLAN, self).__str__()

    def get_absolute_url(self):
        return reverse('ipam:vlan', args=[self.pk])

    def clean(self):

        # Validate VLAN group
        if self.group and self.group.site != self.site:
            raise ValidationError({
                'group': "VLAN group must belong to the assigned site ({}).".format(self.site)
            })

    def to_csv(self):
        return csv_format([
            self.site.name if self.site else None,
            self.group.name if self.group else None,
            self.vid,
            self.name,
            self.tenant.name if self.tenant else None,
            self.get_status_display(),
            self.role.name if self.role else None,
            self.description,
        ])

    @property
    def display_name(self):
        if self.vid and self.name:
            return "{} ({})".format(self.vid, self.name)
        return None

    def get_status_class(self):
        return STATUS_CHOICE_CLASSES[self.status]


@python_2_unicode_compatible
class Service(CreatedUpdatedModel):
    """
    A Service represents a layer-four service (e.g. HTTP or SSH) running on a Device or VirtualMachine. A Service may
    optionally be tied to one or more specific IPAddresses belonging to its parent.
    """
    device = models.ForeignKey(
        to='dcim.Device',
        on_delete=models.CASCADE,
        related_name='services',
        verbose_name='device',
        null=True,
        blank=True
    )
    virtual_machine = models.ForeignKey(
        to='virtualization.VirtualMachine',
        on_delete=models.CASCADE,
        related_name='services',
        null=True,
        blank=True
    )
    name = models.CharField(
        max_length=30
    )
    protocol = models.PositiveSmallIntegerField(
        choices=IP_PROTOCOL_CHOICES
    )
    port = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(65535)],
        verbose_name='Port number'
    )
    ipaddresses = models.ManyToManyField(
        to='ipam.IPAddress',
        related_name='services',
        blank=True,
        verbose_name='IP addresses'
    )
    description = models.CharField(
        max_length=100,
        blank=True
    )

    class Meta:
        ordering = ['protocol', 'port']

    def __str__(self):
        return '{} ({}/{})'.format(self.name, self.port, self.get_protocol_display())

    @property
    def parent(self):
        return self.device or self.virtual_machine

    def clean(self):

        # A Service must belong to a Device *or* to a VirtualMachine
        if self.device and self.virtual_machine:
            raise ValidationError("A service cannot be associated with both a device and a virtual machine.")
        if not self.device and not self.virtual_machine:
            raise ValidationError("A service must be associated with either a device or a virtual machine.")
