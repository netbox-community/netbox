from netaddr import IPNetwork, cidr_merge

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.expressions import RawSQL

from dcim.models import Interface
from extras.models import CustomFieldModel, CustomFieldValue
from tenancy.models import Tenant
from utilities.models import CreatedUpdatedModel
from utilities.sql import NullsFirstQuerySet

from .fields import IPNetworkField, IPAddressField


AF_CHOICES = (
    (4, 'IPv4'),
    (6, 'IPv6'),
)

PREFIX_STATUS_CONTAINER = 0
PREFIX_STATUS_ACTIVE = 1
PREFIX_STATUS_RESERVED = 2
PREFIX_STATUS_DEPRECATED = 3
PREFIX_STATUS_CHOICES = (
    (PREFIX_STATUS_CONTAINER, 'Container'),
    (PREFIX_STATUS_ACTIVE, 'Active'),
    (PREFIX_STATUS_RESERVED, 'Reserved'),
    (PREFIX_STATUS_DEPRECATED, 'Deprecated')
)

IPADDRESS_STATUS_ACTIVE = 1
IPADDRESS_STATUS_RESERVED = 2
IPADDRESS_STATUS_DHCP = 5
IPADDRESS_STATUS_CHOICES = (
    (IPADDRESS_STATUS_ACTIVE, 'Active'),
    (IPADDRESS_STATUS_RESERVED, 'Reserved'),
    (IPADDRESS_STATUS_DHCP, 'DHCP')
)

VLAN_STATUS_ACTIVE = 1
VLAN_STATUS_RESERVED = 2
VLAN_STATUS_DEPRECATED = 3
VLAN_STATUS_CHOICES = (
    (VLAN_STATUS_ACTIVE, 'Active'),
    (VLAN_STATUS_RESERVED, 'Reserved'),
    (VLAN_STATUS_DEPRECATED, 'Deprecated')
)

STATUS_CHOICE_CLASSES = {
    0: 'default',
    1: 'primary',
    2: 'info',
    3: 'danger',
    4: 'warning',
    5: 'success',
}


IP_PROTOCOL_TCP = 6
IP_PROTOCOL_UDP = 17
IP_PROTOCOL_CHOICES = (
    (IP_PROTOCOL_TCP, 'TCP'),
    (IP_PROTOCOL_UDP, 'UDP'),
)


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

    class Meta:
        ordering = ['name']
        verbose_name = 'VRF'
        verbose_name_plural = 'VRFs'

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('ipam:vrf', args=[self.pk])

    def to_csv(self):
        return ','.join([
            self.name,
            self.rd,
            self.tenant.name if self.tenant else '',
            'True' if self.enforce_unique else '',
            self.description,
        ])


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

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "{}?rir={}".format(reverse('ipam:aggregate_list'), self.slug)


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

    class Meta:
        ordering = ['family', 'prefix']

    def __unicode__(self):
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
        return ','.join([
            str(self.prefix),
            self.rir.name,
            self.date_added.isoformat() if self.date_added else '',
            self.description,
        ])

    def get_utilization(self):
        """
        Determine the utilization rate of the aggregate prefix and return it as a percentage.
        """
        child_prefixes = Prefix.objects.filter(prefix__net_contained_or_equal=str(self.prefix))
        # Remove overlapping prefixes from list of children
        networks = cidr_merge([c.prefix for c in child_prefixes])
        children_size = float(0)
        for p in networks:
            children_size += p.size
        return int(children_size / self.prefix.size * 100)


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

    def __unicode__(self):
        return self.name

    @property
    def count_prefixes(self):
        return self.prefixes.count()

    @property
    def count_vlans(self):
        return self.vlans.count()


class PrefixQuerySet(NullsFirstQuerySet):

    def annotate_depth(self, limit=None):
        """
        Iterate through a QuerySet of Prefixes and annotate the hierarchical level of each. While it would be preferable
        to do this using .extra() on the QuerySet to count the unique parents of each prefix, that approach introduces
        performance issues at scale.

        Because we're adding a non-field attribute to the model, annotation must be made *after* any QuerySet
        modifications.
        """
        queryset = self
        stack = []
        for p in queryset:
            try:
                prev_p = stack[-1]
            except IndexError:
                prev_p = None
            if prev_p is not None:
                while (p.prefix not in prev_p.prefix) or p.prefix == prev_p.prefix:
                    stack.pop()
                    try:
                        prev_p = stack[-1]
                    except IndexError:
                        prev_p = None
                        break
            if prev_p is not None:
                prev_p.has_children = True
            stack.append(p)
            p.depth = len(stack) - 1
        if limit is None:
            return queryset
        return filter(lambda p: p.depth <= limit, queryset)


class Prefix(CreatedUpdatedModel, CustomFieldModel):
    """
    A Prefix represents an IPv4 or IPv6 network, including mask length. Prefixes can optionally be assigned to Sites and
    VRFs. A Prefix must be assigned a status and may optionally be assigned a used-define Role. A Prefix can also be
    assigned to a VLAN where appropriate.
    """
    family = models.PositiveSmallIntegerField(choices=AF_CHOICES, editable=False)
    prefix = IPNetworkField()
    site = models.ForeignKey('dcim.Site', related_name='prefixes', on_delete=models.PROTECT, blank=True, null=True)
    vrf = models.ForeignKey('VRF', related_name='prefixes', on_delete=models.PROTECT, blank=True, null=True,
                            verbose_name='VRF')
    tenant = models.ForeignKey(Tenant, related_name='prefixes', blank=True, null=True, on_delete=models.PROTECT)
    vlan = models.ForeignKey('VLAN', related_name='prefixes', on_delete=models.PROTECT, blank=True, null=True,
                             verbose_name='VLAN')
    status = models.PositiveSmallIntegerField('Status', choices=PREFIX_STATUS_CHOICES, default=1)
    role = models.ForeignKey('Role', related_name='prefixes', on_delete=models.SET_NULL, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True)
    custom_field_values = GenericRelation(CustomFieldValue, content_type_field='obj_type', object_id_field='obj_id')

    objects = PrefixQuerySet.as_manager()

    class Meta:
        ordering = ['vrf', 'family', 'prefix']
        verbose_name_plural = 'prefixes'

    def __unicode__(self):
        return str(self.prefix)

    def get_absolute_url(self):
        return reverse('ipam:prefix', args=[self.pk])

    def clean(self):

        # Disallow host masks
        if self.prefix:
            if self.prefix.version == 4 and self.prefix.prefixlen == 32:
                raise ValidationError({
                    'prefix': "Cannot create host addresses (/32) as prefixes. Create an IPv4 address instead."
                })
            elif self.prefix.version == 6 and self.prefix.prefixlen == 128:
                raise ValidationError({
                    'prefix': "Cannot create host addresses (/128) as prefixes. Create an IPv6 address instead."
                })

    def save(self, *args, **kwargs):
        if self.prefix:
            # Clear host bits from prefix
            self.prefix = self.prefix.cidr
            # Infer address family from IPNetwork object
            self.family = self.prefix.version
        super(Prefix, self).save(*args, **kwargs)

    def to_csv(self):
        return ','.join([
            str(self.prefix),
            self.vrf.rd if self.vrf else '',
            self.tenant.name if self.tenant else '',
            self.site.name if self.site else '',
            self.get_status_display(),
            self.role.name if self.role else '',
            self.description,
        ])

    @property
    def new_subnet(self):
        if self.family == 4:
            if self.prefix.prefixlen <= 30:
                return IPNetwork('{}/{}'.format(self.prefix.network, self.prefix.prefixlen + 1))
            return None
        if self.family == 6:
            if self.prefix.prefixlen <= 126:
                return IPNetwork('{}/{}'.format(self.prefix.network, self.prefix.prefixlen + 1))
            return None

    def get_status_class(self):
        return STATUS_CHOICE_CLASSES[self.status]


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
    status = models.PositiveSmallIntegerField('Status', choices=IPADDRESS_STATUS_CHOICES, default=1)
    interface = models.ForeignKey(Interface, related_name='ip_addresses', on_delete=models.CASCADE, blank=True,
                                  null=True)
    nat_inside = models.OneToOneField('self', related_name='nat_outside', on_delete=models.SET_NULL, blank=True,
                                      null=True, verbose_name='NAT (Inside)',
                                      help_text="The IP for which this address is the \"outside\" IP")
    description = models.CharField(max_length=100, blank=True)
    custom_field_values = GenericRelation(CustomFieldValue, content_type_field='obj_type', object_id_field='obj_id')

    objects = IPAddressManager()

    class Meta:
        ordering = ['family', 'address']
        verbose_name = 'IP address'
        verbose_name_plural = 'IP addresses'

    def __unicode__(self):
        return str(self.address)

    def get_absolute_url(self):
        return reverse('ipam:ipaddress', args=[self.pk])

    def clean(self):

        # Enforce unique IP space if applicable
        if self.vrf and self.vrf.enforce_unique:
            duplicate_ips = IPAddress.objects.filter(vrf=self.vrf, address__net_host=str(self.address.ip))\
                .exclude(pk=self.pk)
            if duplicate_ips:
                raise ValidationError({
                    'address': "Duplicate IP address found in VRF {}: {}".format(self.vrf, duplicate_ips.first())
                })
        elif not self.vrf and settings.ENFORCE_GLOBAL_UNIQUE:
            duplicate_ips = IPAddress.objects.filter(vrf=None, address__net_host=str(self.address.ip))\
                .exclude(pk=self.pk)
            if duplicate_ips:
                raise ValidationError({
                    'address': "Duplicate IP address found in global table: {}".format(duplicate_ips.first())
                })

    def save(self, *args, **kwargs):
        if self.address:
            # Infer address family from IPAddress object
            self.family = self.address.version
        super(IPAddress, self).save(*args, **kwargs)

    def to_csv(self):

        # Determine if this IP is primary for a Device
        is_primary = False
        if self.family == 4 and getattr(self, 'primary_ip4_for', False):
            is_primary = True
        elif self.family == 6 and getattr(self, 'primary_ip6_for', False):
            is_primary = True

        return ','.join([
            str(self.address),
            self.vrf.rd if self.vrf else '',
            self.tenant.name if self.tenant else '',
            self.get_status_display(),
            self.device.identifier if self.device else '',
            self.interface.name if self.interface else '',
            'True' if is_primary else '',
            self.description,
        ])

    @property
    def device(self):
        if self.interface:
            return self.interface.device
        return None

    def get_status_class(self):
        return STATUS_CHOICE_CLASSES[self.status]


class VLANGroup(models.Model):
    """
    A VLAN group is an arbitrary collection of VLANs within which VLAN IDs and names must be unique.
    """
    name = models.CharField(max_length=50)
    slug = models.SlugField()
    site = models.ForeignKey('dcim.Site', related_name='vlan_groups')

    class Meta:
        ordering = ['site', 'name']
        unique_together = [
            ['site', 'name'],
            ['site', 'slug'],
        ]
        verbose_name = 'VLAN group'
        verbose_name_plural = 'VLAN groups'

    def __unicode__(self):
        return u'{} - {}'.format(self.site.name, self.name)

    def get_absolute_url(self):
        return "{}?group_id={}".format(reverse('ipam:vlan_list'), self.pk)


class VLAN(CreatedUpdatedModel, CustomFieldModel):
    """
    A VLAN is a distinct layer two forwarding domain identified by a 12-bit integer (1-4094). Each VLAN must be assigned
    to a Site, however VLAN IDs need not be unique within a Site. A VLAN may optionally be assigned to a VLANGroup,
    within which all VLAN IDs and names but be unique.

    Like Prefixes, each VLAN is assigned an operational status and optionally a user-defined Role. A VLAN can have zero
    or more Prefixes assigned to it.
    """
    site = models.ForeignKey('dcim.Site', related_name='vlans', on_delete=models.PROTECT)
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

    class Meta:
        ordering = ['site', 'group', 'vid']
        unique_together = [
            ['group', 'vid'],
            ['group', 'name'],
        ]
        verbose_name = 'VLAN'
        verbose_name_plural = 'VLANs'

    def __unicode__(self):
        return self.display_name

    def get_absolute_url(self):
        return reverse('ipam:vlan', args=[self.pk])

    def clean(self):

        # Validate VLAN group
        if self.group and self.group.site != self.site:
            raise ValidationError({
                'group': "VLAN group must belong to the assigned site ({}).".format(self.site)
            })

    def to_csv(self):
        return ','.join([
            self.site.name,
            self.group.name if self.group else '',
            str(self.vid),
            self.name,
            self.tenant.name if self.tenant else '',
            self.get_status_display(),
            self.role.name if self.role else '',
            self.description,
        ])

    @property
    def display_name(self):
        return u'{} ({})'.format(self.vid, self.name)

    def get_status_class(self):
        return STATUS_CHOICE_CLASSES[self.status]


class Service(CreatedUpdatedModel):
    """
    A Service represents a layer-four service (e.g. HTTP or SSH) running on a Device. A Service may optionally be tied
    to one or more specific IPAddresses belonging to the Device.
    """
    device = models.ForeignKey('dcim.Device', related_name='services', on_delete=models.CASCADE, verbose_name='device')
    name = models.CharField(max_length=30)
    protocol = models.PositiveSmallIntegerField(choices=IP_PROTOCOL_CHOICES)
    port = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(65535)],
                                       verbose_name='Port number')
    ipaddresses = models.ManyToManyField('ipam.IPAddress', related_name='services', blank=True,
                                         verbose_name='IP addresses')
    description = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['device', 'protocol', 'port']
        unique_together = ['device', 'protocol', 'port']

    def __unicode__(self):
        return u'{} ({}/{})'.format(self.name, self.port, self.get_protocol_display())

    def get_parent_url(self):
        return self.device.get_absolute_url()
