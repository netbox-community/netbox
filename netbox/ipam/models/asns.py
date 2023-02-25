from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _

from ipam.fields import ASNField
from netbox.models import PrimaryModel

__all__ = (
    'ASN',
)


class ASN(PrimaryModel):
    """
    An autonomous system (AS) number is typically used to represent an independent routing domain. A site can have
    one or more ASNs assigned to it.
    """
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
