from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _

from ipam.fields import ASNField
from netbox.models import OrganizationalModel, PrimaryModel

__all__ = (
    'ASN',
    'ASNRange',
)


class ASN(PrimaryModel):
    """
    An autonomous system (AS) number is typically used to represent an independent routing domain. A site can have
    one or more ASNs assigned to it.
    """
    range = models.ForeignKey(
        to='ipam.ASNRange',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    asn = ASNField(
        unique=True,
        verbose_name='ASN',
        help_text=_('32-bit autonomous system number')
    )
    rir = models.ForeignKey(
        to='ipam.RIR',
        on_delete=models.PROTECT,
        related_name='asns',
        verbose_name='RIR'
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='asns',
        blank=True,
        null=True
    )

    prerequisite_models = (
        'ipam.RIR',
    )

    class Meta:
        ordering = ['asn']
        verbose_name = 'ASN'
        verbose_name_plural = 'ASNs'

    def __str__(self):
        return f'AS{self.asn_with_asdot}'

    def get_absolute_url(self):
        return reverse('ipam:asn', args=[self.pk])

    @property
    def asn_asdot(self):
        """
        Return ASDOT notation for AS numbers greater than 16 bits.
        """
        if self.asn > 65535:
            return f'{self.asn // 65536}.{self.asn % 65536}'
        return self.asn

    @property
    def asn_with_asdot(self):
        """
        Return both plain and ASDOT notation, where applicable.
        """
        if self.asn > 65535:
            return f'{self.asn} ({self.asn // 65536}.{self.asn % 65536})'
        else:
            return self.asn

    def clean(self):
        if self.range and self.asn not in self.range.range:
            raise ValidationError(f"ASN {self.asn} is outside of assigned range ({self.range})")


class ASNRange(OrganizationalModel):
    name = models.CharField(
        max_length=100,
        unique=True
    )
    slug = models.SlugField(
        max_length=100,
        unique=True
    )
    start = ASNField()
    end = ASNField()
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='asn_ranges',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'ASN range'
        verbose_name_plural = 'ASN ranges'

    def __str__(self):
        return f'{self.name} ({self.range_as_string()})'

    def get_absolute_url(self):
        return reverse('ipam:asnrange', args=[self.pk])

    @property
    def range(self):
        return range(self.start, self.end + 1)

    def range_as_string(self):
        return f'{self.start}-{self.end}'

    def clean(self):
        if self.end <= self.start:
            raise ValidationError(f"Starting ASN ({self.start}) must be lower than ending ASN ({self.end}).")

    def get_available_asns(self):
        """
        Return all available ASNs within this range.
        """
        range = set(self.range)
        existing_asns = set(ASN.objects.filter(range=self).values_list('asn', flat=True))
        available_asns = sorted(range - existing_asns)

        return available_asns
