from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from netbox.models import PrimaryModel
from vpn.choices import *

__all__ = (
    'IPSecProfile',
)


class IPSecProfile(PrimaryModel):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        unique=True
    )
    protocol = models.CharField(
        verbose_name=_('protocol'),
        choices=IPSecProtocolChoices
    )
    ike_version = models.PositiveSmallIntegerField(
        verbose_name=_('IKE version'),
        choices=IKEVersionChoices,
        default=IKEVersionChoices.VERSION_2
    )

    # Phase 1 parameters
    phase1_encryption = models.CharField(
        verbose_name=_('phase 1 encryption'),
        choices=EncryptionChoices
    )
    phase1_authentication = models.CharField(
        verbose_name=_('phase 1 authentication'),
        choices=AuthenticationChoices
    )
    phase1_group = models.PositiveSmallIntegerField(
        verbose_name=_('phase 1 group'),
        choices=DHGroupChoices,
        help_text=_('Diffie-Hellman group')
    )
    phase1_sa_lifetime = models.PositiveSmallIntegerField(
        verbose_name=_('phase 1 SA lifetime'),
        blank=True,
        null=True,
        help_text=_('Security association lifetime (in seconds)')
    )

    # Phase 2 parameters
    phase2_encryption = models.CharField(
        verbose_name=_('phase 2 encryption'),
        choices=EncryptionChoices
    )
    phase2_authentication = models.CharField(
        verbose_name=_('phase 2 authentication'),
        choices=AuthenticationChoices
    )
    phase2_group = models.PositiveSmallIntegerField(
        verbose_name=_('phase 2 group'),
        choices=DHGroupChoices,
        help_text=_('Diffie-Hellman group')
    )
    phase2_sa_lifetime = models.PositiveSmallIntegerField(
        verbose_name=_('phase 2 SA lifetime'),
        blank=True,
        null=True,
        help_text=_('Security association lifetime (in seconds)')
    )
    # TODO: Add PFS group?

    clone_fields = (
        'protocol', 'ike_version', 'phase1_encryption', 'phase1_authentication', 'phase1_group', 'phase1_as_lifetime',
        'phase2_encryption', 'phase2_authentication', 'phase2_group', 'phase2_as_lifetime',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = _('tunnel')
        verbose_name_plural = _('tunnels')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('vpn:ipsecprofile', args=[self.pk])
