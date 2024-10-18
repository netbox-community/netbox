from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ipam.constants import SERVICE_PORT_MIN, SERVICE_PORT_MAX
from ipam.fields import IPNetworkField
from netbox.models import PrimaryModel, CustomFieldsMixin, CustomLinksMixin, TagsMixin, \
    ChangeLoggedModel
from vpn.choices import *

__all__ = (
    'IKEPolicy',
    'IKEProposal',
    'IPSecPolicy',
    'IPSecProfile',
    'IPSecProposal',
    'WireguardConfig',
)


WIREGUARD_DEFAULT_PORT = 51820


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


class WireguardConfig(CustomFieldsMixin, CustomLinksMixin, TagsMixin, ChangeLoggedModel):
    tunnel_interface_type = models.ForeignKey(
        to='contenttypes.ContentType',
        on_delete=models.PROTECT,
        related_name='+'
    )
    tunnel_interface_id = models.PositiveBigIntegerField(
        blank=True,
        null=True
    )
    tunnel_interface = GenericForeignKey(
        ct_field='tunnel_interface_type',
        fk_field='tunnel_interface_id'
    )
    private_key = models.TextField(
        verbose_name=_('private key'),
        blank=True,
    )
    public_key = models.TextField(
        verbose_name=_('public key'),
        blank=True
    )
    listen_port = models.PositiveIntegerField(
        verbose_name=_('listen port'),
        default=WIREGUARD_DEFAULT_PORT,
        validators=[
            MinValueValidator(SERVICE_PORT_MIN),
            MaxValueValidator(SERVICE_PORT_MAX)
        ]
    )
    allowed_ips = ArrayField(
        base_field=IPNetworkField(),
        blank=True,
        null=True,
        verbose_name=_('allowed ips'),
        help_text=_(
            "Represents the permissible IPv4/IPv6 networks for use by other peers in their "
            "'allowed_ips' configuration while creating a tunnel with this peer. "
            "Ex: '10.1.1.0/24, 192.168.10.16/32, 2001:DB8:1::/64'"
        ),
    )
    fwmark = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('fwmark'),
        help_text=_('Optional. Set a 32-bit integer firewall mark (fwmark) for outgoing packets'),
    )
    persistent_keepalive_interval = models.PositiveIntegerField(
        default=0,
        verbose_name=_('persistent keepalive interval'),
        help_text=_('Persistant keepalive interval in seconds, 0 disables this feature'),
    )

    class Meta:
        ordering = ('pk',)
        indexes = (
            models.Index(fields=('tunnel_interface_type', 'tunnel_interface_id')),
        )
        constraints = (
            models.UniqueConstraint(
                fields=('tunnel_interface_type', 'tunnel_interface_id'),
                name='%(app_label)s_%(class)s_tunnel_interface',
                violation_error_message=_("An tunnel_interface may only have one wireguard configration.")
            ),
        )
        verbose_name = _('wireguard config')
        verbose_name_plural = _('wireguard configs')

    def __str__(self):
        return f'{self.tunnel_interface.name}: Wireguard config'

    def get_absolute_url(self):
        return reverse('vpn:wireguardconfig', args=[self.pk])

    def clean(self):
        super().clean()

        # Check that the selected termination object is not already
        if getattr(self.tunnel_interface, 'wireguard_config', None) and self.tunnel_interface.wireguard_config.pk != self.pk:
            raise ValidationError({
                'tunnel_interface': _("{name} already has a Wireguard config").format(
                    name=self.tunnel_interface.name,
                )
            })

    def to_objectchange(self, action):
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.tunnel_interface
        return objectchange
