from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from netbox.models import NetBoxModel, PrimaryModel
from vpn.choices import *

__all__ = (
    'IKEPolicy',
    'IKEProposal',
    'IPSecPolicy',
    'IPSecProfile',
    'IPSecProposal',
)


#
# IKE
#

class IKEProposal(NetBoxModel):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        unique=True
    )
    description = models.CharField(
        verbose_name=_('description'),
        max_length=200,
        blank=True
    )
    authentication_method = models.CharField(
        verbose_name=('authentication method'),
        choices=AuthenticationMethodChoices
    )
    encryption_algorithm = models.CharField(
        verbose_name=_('encryption algorithm'),
        choices=EncryptionAlgorithmChoices
    )
    authentication_algorithm = models.CharField(
        verbose_name=_('authentication algorithm'),
        choices=AuthenticationAlgorithmChoices
    )
    group = models.PositiveSmallIntegerField(
        verbose_name=_('group'),
        choices=DHGroupChoices,
        help_text=_('Diffie-Hellman group ID')
    )
    sa_lifetime = models.PositiveIntegerField(
        verbose_name=_('SA lifetime'),
        blank=True,
        null=True,
        help_text=_('Security association lifetime (in seconds)')
    )

    class Meta:
        ordering = ('name',)
        verbose_name = _('IKE proposal')
        verbose_name_plural = _('IKE proposals')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('vpn:ikeproposal', args=[self.pk])


class IKEPolicy(NetBoxModel):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        unique=True
    )
    description = models.CharField(
        verbose_name=_('description'),
        max_length=200,
        blank=True
    )
    version = models.PositiveSmallIntegerField(
        verbose_name=_('version'),
        choices=IKEVersionChoices,
        default=IKEVersionChoices.VERSION_2
    )
    mode = models.CharField(
        verbose_name=_('mode'),
        choices=IKEModeChoices
    )
    proposals = models.ManyToManyField(
        to='vpn.IKEProposal',
        related_name='ike_policies',
        verbose_name=_('proposals')
    )
    preshared_key = models.TextField(
        verbose_name=_('pre-shared key'),
        blank=True
    )
    certificate = models.TextField(
        verbose_name=_('certificate'),
        blank=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = _('IKE policy')
        verbose_name_plural = _('IKE policies')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('vpn:ikeprofile', args=[self.pk])


#
# IPSec
#

class IPSecProposal(NetBoxModel):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        unique=True
    )
    description = models.CharField(
        verbose_name=_('description'),
        max_length=200,
        blank=True
    )
    encryption_algorithm = models.CharField(
        verbose_name=_('encryption'),
        choices=EncryptionAlgorithmChoices
    )
    authentication_algorithm = models.CharField(
        verbose_name=_('authentication'),
        choices=AuthenticationAlgorithmChoices
    )
    sa_lifetime_seconds = models.PositiveIntegerField(
        verbose_name=_('SA lifetime (seconds)'),
        blank=True,
        null=True,
        help_text=_('Security association lifetime (seconds)')
    )
    sa_lifetime_data = models.PositiveIntegerField(
        verbose_name=_('SA lifetime (KB)'),
        blank=True,
        null=True,
        help_text=_('Security association lifetime (in kilobytes)')
    )

    class Meta:
        ordering = ('name',)
        verbose_name = _('IPSec proposal')
        verbose_name_plural = _('IPSec proposals')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('vpn:ipsecproposal', args=[self.pk])


class IPSecPolicy(NetBoxModel):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        unique=True
    )
    description = models.CharField(
        verbose_name=_('description'),
        max_length=200,
        blank=True
    )
    proposals = models.ManyToManyField(
        to='vpn.IPSecProposal',
        related_name='ipsec_policies',
        verbose_name=_('proposals')
    )
    pfs_group = models.PositiveSmallIntegerField(
        verbose_name=_('PFS group'),
        choices=DHGroupChoices,
        blank=True,
        null=True,
        help_text=_('Diffie-Hellman group for Perfect Forward Secrecy')
    )

    class Meta:
        ordering = ('name',)
        verbose_name = _('IPSec policy')
        verbose_name_plural = _('IPSec policies')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('vpn:ipsecpolicy', args=[self.pk])


class IPSecProfile(PrimaryModel):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        unique=True
    )
    mode = models.CharField(
        verbose_name=_('mode'),
        choices=IPSecModeChoices
    )
    ike_policy = models.ForeignKey(
        to='vpn.IKEPolicy',
        on_delete=models.PROTECT,
        related_name='ipsec_profiles'
    )
    ipsec_policy = models.ForeignKey(
        to='vpn.IPSecPolicy',
        on_delete=models.PROTECT,
        related_name='ipsec_profiles'
    )

    clone_fields = (
        'mode', 'ike_policy', 'ipsec_policy',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = _('IPSec profile')
        verbose_name_plural = _('IPSec profiles')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('vpn:ipsecprofile', args=[self.pk])
