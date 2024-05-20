from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from netbox.models import PrimaryModel
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

class IKEProposal(PrimaryModel):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        unique=True
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
        choices=AuthenticationAlgorithmChoices,
        blank=True
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

    clone_fields = (
        'authentication_method', 'encryption_algorithm', 'authentication_algorithm', 'group', 'sa_lifetime',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = _('IKE proposal')
        verbose_name_plural = _('IKE proposals')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('vpn:ikeproposal', args=[self.pk])


class IKEPolicy(PrimaryModel):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        unique=True
    )
    version = models.PositiveSmallIntegerField(
        verbose_name=_('version'),
        choices=IKEVersionChoices,
        default=IKEVersionChoices.VERSION_2
    )
    mode = models.CharField(
        verbose_name=_('mode'),
        choices=IKEModeChoices,
        blank=True
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

    clone_fields = (
        'version', 'mode', 'proposals',
    )
    prerequisite_models = (
        'vpn.IKEProposal',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = _('IKE policy')
        verbose_name_plural = _('IKE policies')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('vpn:ikepolicy', args=[self.pk])

    def clean(self):
        super().clean()

        # Mode is required
        if self.version == IKEVersionChoices.VERSION_1 and not self.mode:
            raise ValidationError(_("Mode is required for selected IKE version"))

        # Mode cannot be used
        if self.version == IKEVersionChoices.VERSION_2 and self.mode:
            raise ValidationError(_("Mode cannot be used for selected IKE version"))


#
# IPSec
#

class IPSecProposal(PrimaryModel):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        unique=True
    )
    encryption_algorithm = models.CharField(
        verbose_name=_('encryption'),
        choices=EncryptionAlgorithmChoices,
        blank=True
    )
    authentication_algorithm = models.CharField(
        verbose_name=_('authentication'),
        choices=AuthenticationAlgorithmChoices,
        blank=True
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

    clone_fields = (
        'encryption_algorithm', 'authentication_algorithm', 'sa_lifetime_seconds', 'sa_lifetime_data',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = _('IPSec proposal')
        verbose_name_plural = _('IPSec proposals')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('vpn:ipsecproposal', args=[self.pk])

    def clean(self):
        super().clean()

        # Encryption and/or authentication algorithm must be defined
        if not self.encryption_algorithm and not self.authentication_algorithm:
            raise ValidationError(_("Encryption and/or authentication algorithm must be defined"))


class IPSecPolicy(PrimaryModel):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        unique=True
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

    clone_fields = (
        'proposals', 'pfs_group',
    )
    prerequisite_models = (
        'vpn.IPSecProposal',
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
    prerequisite_models = (
        'vpn.IKEPolicy',
        'vpn.IPSecPolicy',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = _('IPSec profile')
        verbose_name_plural = _('IPSec profiles')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('vpn:ipsecprofile', args=[self.pk])
