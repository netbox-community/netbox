from netaddr import IPNetwork, cidr_merge

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.expressions import RawSQL

from dcim.models import Interface
from tenancy.models import Tenant
from utilities.models import CreatedUpdatedModel
import dns.models

from .fields import IPNetworkField, IPAddressField

import time
import ipaddress
import netaddr


AF_CHOICES = (
    (4, 'IPv4'),
    (6, 'IPv6'),
)

PREFIX_STATUS_CHOICES = (
    (0, 'Container'),
    (1, 'Active'),
    (2, 'Reserved'),
    (3, 'Deprecated')
)

VLAN_STATUS_CHOICES = (
    (1, 'Active'),
    (2, 'Reserved'),
    (3, 'Deprecated')
)

STATUS_CHOICE_CLASSES = {
    0: 'default',
    1: 'primary',
    2: 'info',
    3: 'danger',
}


class VRF(CreatedUpdatedModel):
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

    class Meta:
        ordering = ['name']
        verbose_name = 'RIR'
        verbose_name_plural = 'RIRs'

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "{}?rir={}".format(reverse('ipam:aggregate_list'), self.slug)


class Aggregate(CreatedUpdatedModel):
    """
    An aggregate exists at the root level of the IP address space hierarchy in NetBox. Aggregates are used to organize
    the hierarchy and track the overall utilization of available address space. Each Aggregate is assigned to a RIR.
    """
    family = models.PositiveSmallIntegerField(choices=AF_CHOICES)
    prefix = IPNetworkField()
    rir = models.ForeignKey('RIR', related_name='aggregates', on_delete=models.PROTECT, verbose_name='RIR')
    date_added = models.DateField(blank=True, null=True)
    description = models.CharField(max_length=100, blank=True)

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
                raise ValidationError("{} is already covered by an existing aggregate ({})"
                                      .format(self.prefix, covering_aggregates[0]))

            # Ensure that the aggregate being added does not cover an existing aggregate
            covered_aggregates = Aggregate.objects.filter(prefix__net_contained=str(self.prefix))
            if self.pk:
                covered_aggregates = covered_aggregates.exclude(pk=self.pk)
            if covered_aggregates:
                raise ValidationError("{} is overlaps with an existing aggregate ({})"
                                      .format(self.prefix, covered_aggregates[0]))

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


class PrefixQuerySet(models.QuerySet):

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


class Prefix(CreatedUpdatedModel):
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

    objects = PrefixQuerySet.as_manager()

    # Reverse DNS
    ttl = models.PositiveIntegerField(blank=True, null=True)
    soa_name = models.CharField(max_length=100, blank=True)
    soa_contact = models.CharField(max_length=100, blank=True)

    soa_serial = models.CharField(max_length=10, blank=True)
    bind_changed = models.BooleanField(default=True)

    soa_refresh = models.PositiveIntegerField(blank=True, null=True)
    soa_retry = models.PositiveIntegerField(blank=True, null=True)
    soa_expire = models.PositiveIntegerField(blank=True, null=True)
    soa_minimum = models.PositiveIntegerField(blank=True, null=True)

    extra_conf = models.CharField(max_length=500, blank=True)
    description = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['family', 'prefix']
        verbose_name_plural = 'prefixes'

    def __unicode__(self):
        return str(self.prefix)

    def get_absolute_url(self):
        return reverse('ipam:prefix', args=[self.pk])

    def clean(self):
        # Disallow host masks
        if self.prefix:
            if self.prefix.version == 4 and self.prefix.prefixlen == 32:
                raise ValidationError("Cannot create host addresses (/32) as prefixes. These should be IPv4 addresses "
                                      "instead.")
            elif self.prefix.version == 6 and self.prefix.prefixlen == 128:
                raise ValidationError("Cannot create host addresses (/128) as prefixes. These should be IPv6 addresses "
                                      "instead.")

    def save(self, *args, **kwargs):
        self.bind_changed = True
        if self.prefix:
            # Clear host bits from prefix
            self.prefix = self.prefix.cidr
            # Infer address family from IPNetwork object
            self.family = self.prefix.version
        super(Prefix, self).save(*args, **kwargs)

    def set_bind_changed(self, value):
        self.bind_changed = value
        super(Prefix, self).save()

    def update_serial(self):
        """
        Each time a record or the zone is modified, the serial is incremented.
        """
        current_date = time.strftime('%Y%m%d', time.localtime())
        if not self.soa_serial:
            self.soa_serial = current_date + '01'
        else:
            serial_date = self.soa_serial[:8]
            serial_num = self.soa_serial[8:]

            if serial_date != current_date:
                self.soa_serial = current_date + '01'
            else:
                serial_num = int(serial_num)
                serial_num += 1
                if serial_num < 10:
                    self.soa_serial = current_date + '0' + str(serial_num)
                else:
                    self.soa_serial = current_date + str(serial_num)
        self.set_bind_changed(False)

    def to_csv(self):
        return ','.join([
            str(self.prefix),
            self.vrf.rd if self.vrf else '',
            self.site.name if self.site else '',
            self.get_status_display(),
            self.role.name if self.role else '',
            self.description,
            str(self.ttl) if self.ttl else '',
            self.soa_name if self.soa_name else '',
            self.soa_contact if self.soa_contact else '',
            self.soa_serial if self.soa_serial else '',
            str(self.soa_refresh) if self.soa_refresh else '',
            str(self.soa_retry) if self.soa_retry else '',
            str(self.soa_expire) if self.soa_expire else '',
            str(self.soa_minimum) if self.soa_minimum else '',
            '"{}"'.format(self.extra_conf) if self.extra_conf else '',
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

    def to_bind(self, ipaddresses):
        if self.bind_changed:
            self.update_serial()

        zones = {}

        def header(zone_id):
            return '\n'.join([
                '; ' + zone_id,
                '; gen from prefix ' + str(self.prefix) + ' (' + (self.description if self.description else '') + ') by netbox ( ' + time.strftime('%A %B %d %Y %H:%M:%S', time.localtime()) + ' ) ',
                '',
                '$TTL ' + str(self.ttl),
                self.soa_name.ljust(30) + '    IN    ' + 'SOA                   ' + self.soa_contact + ' (',
                '    ' + self.soa_serial.ljust(30) + ' ; serial',
                '    ' + str(self.soa_refresh).ljust(30) + ' ; refresh',
                '    ' + str(self.soa_retry).ljust(30) + ' ; retry',
                '    ' + str(self.soa_expire).ljust(30) + ' ; expire',
                '    ' + str(self.soa_minimum).ljust(29) + ') ; minimum',
                '',
                '',
                '',
                '$ORIGIN        ' + zone_id,
                '',
                '',
            ])

        if self.prefix.version == 4:
            pbytes = str(self.prefix).split('/')[0].split('.')
            pslash = int(str(self.prefix).split('/')[1])

            if pslash > 16:
                pbytes[3] = '0'
                zslash = 24
                largerPrefix = Prefix.objects.filter(family=4, prefix__net_contains_or_equals=pbytes[0] + '.' + pbytes[1] + '.0.0/16')
                if largerPrefix:
                    pbytes[2] = '0'
                    zslash = 16
            else:
                pbytes[2] = '0'
                zslash = 16

            if pslash > zslash:
                pslash = zslash

            p = IPNetwork(unicode('.'.join(pbytes) + '/' + str(pslash)))

            ipaddresses = IPAddress.objects.filter(family=4)
            for ip in ipaddresses:
                if ip.ptr:
                    ibytes = str(ip.address).split('/')[0].split('.')
                    islash = str(ip.address).split('/')[1]
                    i = netaddr.IPAddress(unicode('.'.join(ibytes)))

                    if i in p:
                        if zslash == 24:
                            zone_id = ibytes[2] + '.' + ibytes[1] + '.' + ibytes[0] + '.in-addr.arpa.'
                            if zone_id not in zones:
                                zones[zone_id] = header(zone_id)
                            zones[zone_id] += ibytes[3].ljust(3) + '        IN PTR        ' + ip.ptr.ljust(40) + '    ; ' + ip.description.ljust(20) + ' ; gen by netbox ( ' + time.strftime('%A %B %d %Y %H:%M:%S', time.localtime()) + ' ) \n'
                        else:
                            zone_id = ibytes[1] + '.' + ibytes[0] + '.in-addr.arpa.'
                            if zone_id not in zones:
                                zones[zone_id] = header(zone_id)
                            zones[zone_id] += (ibytes[3] + '.' + ibytes[2]).ljust(7) + '        IN PTR        ' + ip.ptr.ljust(40) + '    ; ' + ip.description.ljust(20) + ' ; gen by netbox ( ' + time.strftime('%A %B %d %Y %H:%M:%S', time.localtime()) + ' ) \n'

        else:
            pfull = str(ipaddress.IPv6Address(unicode(str(self.prefix).split('/')[0])).exploded)
            pnibbles = pfull.split(':')
            pdigits = pfull.replace(':', '')
            pslash = int(str(self.prefix).split('/')[1])

            zslash = pslash if pslash % 16 == 0 else pslash / 16 + 16
            pnibbles = pnibbles[:zslash / 16] + ['0000'] * (8 - zslash / 16)

            largerPrefix = Prefix.objects.filter(family=6, prefix__net_contains_or_equals=':'.join(pnibbles) + '/' + str(zslash))
            if largerPrefix:
                minSlash = 128
                for pp in largerPrefix:
                    ppslash = int(str(pp.prefix).split('/')[1])
                    if ppslash < minSlash:
                        minSlash = ppslash
                zslash = minSlash
                pnibbles = pnibbles[:zslash / 16] + ['0000'] * (8 - zslash / 16)

            for ip in ipaddresses:
                if ip.ptr:
                    ifull = str(ipaddress.IPv6Address(unicode(str(ip.address).split('/')[0])).exploded)
                    inibbles = ifull.split(':')
                    idigits = ifull.replace(':', '')[::-1]
                    islash = int(str(ip.address).split('/')[1])

                    pdigitszone = pdigits[:zslash / 4][::-1]
                    zone_id = '.'.join(pdigitszone) + '.ip6.arpa.'
                    if zone_id not in zones:
                        zones[zone_id] = header(zone_id)

                    zones[zone_id] += ('.'.join(idigits[:32 - zslash / 4])).ljust(30) + '        IN PTR        ' + ip.ptr.ljust(40) + '    ; ' + ip.description.ljust(20) + ' ; gen by netbox ( ' + time.strftime('%A %B %d %Y %H:%M:%S', time.localtime()) + ' ) \n'

        for z in zones:
            z += '\n\n; end '

        ret = []
        for zid, zc in zones.items():
            ret.append({
                'num': len(ret),
                'id': zid,
                'content': zc,
            })

        return ret


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


class IPAddress(CreatedUpdatedModel):
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
    address = IPAddressField()
    vrf = models.ForeignKey('VRF', related_name='ip_addresses', on_delete=models.PROTECT, blank=True, null=True,
                            verbose_name='VRF')
    tenant = models.ForeignKey(Tenant, related_name='ip_addresses', blank=True, null=True, on_delete=models.PROTECT)
    ptr = models.CharField(max_length=100, blank=True, verbose_name='PTR')
    interface = models.ForeignKey(Interface, related_name='ip_addresses', on_delete=models.CASCADE, blank=True,
                                  null=True)
    nat_inside = models.OneToOneField('self', related_name='nat_outside', on_delete=models.SET_NULL, blank=True,
                                      null=True, verbose_name='NAT IP (inside)')
    description = models.CharField(max_length=100, blank=True)

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
                raise ValidationError("Duplicate IP address found in VRF {}: {}".format(self.vrf,
                                                                                        duplicate_ips.first()))
        elif not self.vrf and settings.ENFORCE_GLOBAL_UNIQUE:
            duplicate_ips = IPAddress.objects.filter(vrf=None, address__net_host=str(self.address.ip))\
                .exclude(pk=self.pk)
            if duplicate_ips:
                raise ValidationError("Duplicate IP address found in global table: {}".format(duplicate_ips.first()))

    def save(self, *args, **kwargs):
        if self.address:
            # Infer address family from IPAddress object
            self.family = self.address.version
        super(IPAddress, self).save(*args, **kwargs)
        self.update_dns()
        dns_records = dns.models.Record.objects.filter(address=self)
        for r in dns_records:
            r.save()

    def update_dns(self):
        """Auto-create a corresponding A/AAAA DNS record (if possible) whenever the PTR field is modified"""
        if self.ptr:
            which_zone = None
            zones = dns.models.Zone.objects.all()
            for zone in zones:
                if self.ptr.endswith(zone.name) or self.ptr.endswith(zone.name + '.'):
                    which_zone = zone
                    break

            if which_zone:
                zone_name = which_zone.name
                record_name = self.ptr[:-len(zone_name)] if not self.ptr.endswith('.') else self.ptr[:-len(zone_name) - 1]
                if record_name.endswith('.'):
                    record_name = record_name[:-1]
                record_type = 'A' if self.family == 4 else 'AAAA'

                dns.models.Record.objects.get_or_create(
                    name=record_name,
                    record_type=record_type,
                    zone=which_zone,
                    address=self
                )

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
            self.ptr if self.ptr else '',
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


class VLAN(CreatedUpdatedModel):
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
            raise ValidationError("VLAN group must belong to the assigned site ({}).".format(self.site))

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
