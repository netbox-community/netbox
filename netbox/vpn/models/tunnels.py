from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from netbox.models import ChangeLoggedModel, PrimaryModel
from netbox.models.features import CustomFieldsMixin, CustomLinksMixin, TagsMixin
from vpn.choices import *

__all__ = (
    'Tunnel',
    'TunnelTermination',
)


class Tunnel(PrimaryModel):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        unique=True
    )
    status = models.CharField(
        verbose_name=_('status'),
        max_length=50,
        choices=TunnelStatusChoices,
        default=TunnelStatusChoices.STATUS_ACTIVE
    )
    encapsulation = models.CharField(
        verbose_name=_('encapsulation'),
        max_length=50,
        choices=TunnelEncapsulationChoices
    )
    ipsec_profile = models.ForeignKey(
        to='vpn.IPSecProfile',
        on_delete=models.PROTECT,
        related_name='tunnels',
        blank=True,
        null=True
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='tunnels',
        blank=True,
        null=True
    )
    tunnel_id = models.PositiveBigIntegerField(
        verbose_name=_('tunnel ID'),
        blank=True,
        null=True
    )

    clone_fields = (
        'status', 'encapsulation', 'ipsec_profile', 'tenant',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = _('tunnel')
        verbose_name_plural = _('tunnels')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('vpn:tunnel', args=[self.pk])

    def get_status_color(self):
        return TunnelStatusChoices.colors.get(self.status)


class TunnelTermination(CustomFieldsMixin, CustomLinksMixin, TagsMixin, ChangeLoggedModel):
    tunnel = models.ForeignKey(
        to='vpn.Tunnel',
        on_delete=models.CASCADE,
        related_name='terminations'
    )
    role = models.CharField(
        verbose_name=_('role'),
        max_length=50,
        choices=TunnelTerminationRoleChoices,
        default=TunnelTerminationRoleChoices.ROLE_PEER
    )
    interface_type = models.ForeignKey(
        to='contenttypes.ContentType',
        on_delete=models.PROTECT,
        related_name='+'
    )
    interface_id = models.PositiveBigIntegerField(
        blank=True,
        null=True
    )
    interface = GenericForeignKey(
        ct_field='interface_type',
        fk_field='interface_id'
    )
    outside_ip = models.OneToOneField(
        to='ipam.IPAddress',
        on_delete=models.PROTECT,
        related_name='tunnel_termination',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ('tunnel', 'role', 'pk')
        constraints = (
            models.UniqueConstraint(
                fields=('interface_type', 'interface_id'),
                name='%(app_label)s_%(class)s_interface',
                violation_error_message=_("An interface may be terminated to only one tunnel at a time.")
            ),
        )
        verbose_name = _('tunnel termination')
        verbose_name_plural = _('tunnel terminations')

    def __str__(self):
        return f'{self.tunnel}: Termination {self.pk}'

    def get_absolute_url(self):
        return self.tunnel.get_absolute_url()

    def get_role_color(self):
        return TunnelTerminationRoleChoices.colors.get(self.role)

    def clean(self):
        super().clean()

        # Check that the selected Interface is not already attached to a Tunnel
        if self.interface.tunnel_termination and self.interface.tunnel_termination.pk != self.pk:
            raise ValidationError({
                'interface': _("Interface {name} is already attached to a tunnel ({tunnel}).").format(
                    name=self.interface.name,
                    tunnel=self.interface.tunnel_termination.tunnel
                )
            })

    def to_objectchange(self, action):
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.tunnel
        return objectchange
