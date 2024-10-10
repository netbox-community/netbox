from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ipam.fields import ASNField
from ipam.querysets import ASNRangeQuerySet
from netbox.models import OrganizationalModel, PrimaryModel

__all__ = (
    'ASN',
    'ASNRange',
)


class ASNRange(OrganizationalModel):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        unique=True
    )
    slug = models.SlugField(
        verbose_name=_('slug'),
        max_length=100,
        unique=True
    )
    rir = models.ForeignKey(
        to='ipam.RIR',
        on_delete=models.PROTECT,
        related_name='asn_ranges',
        verbose_name=_('RIR')
    )
    start = ASNField(
        verbose_name=_('start'),
    )
    end = ASNField(
        verbose_name=_('end'),
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='asn_ranges',
        blank=True,
        null=True
    )

    objects = ASNRangeQuerySet.as_manager()

    class Meta:
        ordering = ('name',)
        verbose_name = _('ASN range')
        verbose_name_plural = _('ASN ranges')

    def __str__(self):
        return f'{self.name} ({self.range_as_string()})'

    @property
    def range(self):
        return range(self.start, self.end + 1)

    def range_as_string(self):
        return f'{self.start}-{self.end}'

    def clean(self):
        super().clean()

        if self.end <= self.start:
            raise ValidationError(
                _("Starting ASN ({start}) must be lower than ending ASN ({end}).").format(
                    start=self.start, end=self.end
                )
            )

    def get_child_asns(self):
        return ASN.objects.filter(
            asn__gte=self.start,
            asn__lte=self.end
        )

    def get_available_asns(self):
        """
        Return all available ASNs within this range.
        """
        range = set(self.range)
        existing_asns = set(self.get_child_asns().values_list('asn', flat=True))
        available_asns = sorted(range - existing_asns)

        return available_asns


class ASN(PrimaryModel):
    """
    An autonomous system (AS) number is typically used to represent an independent routing domain. A site can have
    one or more ASNs assigned to it.
    """
    rir = models.ForeignKey(
        to='ipam.RIR',
        on_delete=models.PROTECT,
        related_name='asns',
        verbose_name=_('RIR'),
        help_text=_("Regional Internet Registry responsible for this AS number space")
    )
    asn = ASNField(
        unique=True,
        verbose_name=_('ASN'),
        help_text=_('16- or 32-bit autonomous system number')
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
        verbose_name = _('ASN')
        verbose_name_plural = _('ASNs')

    def __str__(self):
        return f'AS{self.asn_with_asdot}'

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

    @property
    def prefixed_name(self):
        return f'AS{self.asn_with_asdot}'
