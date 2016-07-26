from django.core.urlresolvers import reverse
from django.db import models

from dcim.fields import ASNField
from dcim.models import Site, Interface
from tenancy.models import Tenant
from utilities.models import CreatedUpdatedModel


class Provider(CreatedUpdatedModel):
    """
    Each Circuit belongs to a Provider. This is usually a telecommunications company or similar organization. This model
    stores information pertinent to the user's relationship with the Provider.
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    asn = ASNField(blank=True, null=True, verbose_name='ASN')
    account = models.CharField(max_length=30, blank=True, verbose_name='Account number')
    portal_url = models.URLField(blank=True, verbose_name='Portal')
    noc_contact = models.TextField(blank=True, verbose_name='NOC contact')
    admin_contact = models.TextField(blank=True, verbose_name='Admin contact')
    comments = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('circuits:provider', args=[self.slug])

    def to_csv(self):
        return ','.join([
            self.name,
            self.slug,
            str(self.asn) if self.asn else '',
            self.account,
            self.portal_url,
        ])


class CircuitType(models.Model):
    """
    Circuits can be orgnanized by their functional role. For example, a user might wish to define CircuitTypes named
    "Long Haul," "Metro," or "Out-of-Band".
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "{}?type={}".format(reverse('circuits:circuit_list'), self.slug)


class Circuit(CreatedUpdatedModel):
    """
    A communications circuit connects two points. Each Circuit belongs to a Provider; Providers may have multiple
    circuits. Each circuit is also assigned a CircuitType and a Site. A Circuit may be terminated to a specific device
    interface, but this is not required. Circuit port speed and commit rate are measured in Kbps.
    """
    cid = models.CharField(max_length=50, verbose_name='Circuit ID')
    provider = models.ForeignKey('Provider', related_name='circuits', on_delete=models.PROTECT)
    type = models.ForeignKey('CircuitType', related_name='circuits', on_delete=models.PROTECT)
    tenant = models.ForeignKey(Tenant, related_name='circuits', blank=True, null=True, on_delete=models.PROTECT)
    site = models.ForeignKey(Site, related_name='circuits', on_delete=models.PROTECT)
    interface = models.OneToOneField(Interface, related_name='circuit', blank=True, null=True)
    install_date = models.DateField(blank=True, null=True, verbose_name='Date installed')
    port_speed = models.PositiveIntegerField(verbose_name='Port speed (Kbps)')
    commit_rate = models.PositiveIntegerField(blank=True, null=True, verbose_name='Commit rate (Kbps)')
    xconnect_id = models.CharField(max_length=50, blank=True, verbose_name='Cross-connect ID')
    pp_info = models.CharField(max_length=100, blank=True, verbose_name='Patch panel/port(s)')
    comments = models.TextField(blank=True)

    class Meta:
        ordering = ['provider', 'cid']
        unique_together = ['provider', 'cid']

    def __unicode__(self):
        return u'{} {}'.format(self.provider, self.cid)

    def get_absolute_url(self):
        return reverse('circuits:circuit', args=[self.pk])

    def to_csv(self):
        return ','.join([
            self.cid,
            self.provider.name,
            self.type.name,
            self.site.name,
            self.install_date.isoformat() if self.install_date else '',
            str(self.port_speed),
            str(self.commit_rate) if self.commit_rate else '',
            self.xconnect_id,
            self.pp_info,
        ])

    def _humanize_speed(self, speed):
        """
        Humanize speeds given in Kbps (e.g. 10000000 becomes '10 Gbps')
        """
        if speed >= 1000000000 and speed % 1000000000 == 0:
            return '{} Tbps'.format(speed / 1000000000)
        elif speed >= 1000000 and speed % 1000000 == 0:
            return '{} Gbps'.format(speed / 1000000)
        elif speed >= 1000 and speed % 1000 == 0:
            return '{} Mbps'.format(speed / 1000)
        elif speed >= 1000:
            return '{} Mbps'.format(float(speed) / 1000)
        else:
            return '{} Kbps'.format(speed)

    @property
    def port_speed_human(self):
        return self._humanize_speed(self.port_speed)

    @property
    def commit_rate_human(self):
        if not self.commit_rate:
            return ''
        return self._humanize_speed(self.commit_rate)
