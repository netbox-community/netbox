from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from netbox.models import ChangeLoggedModel, OrganizationalModel, PrimaryModel
from netbox.models.features import CustomFieldsMixin, CustomLinksMixin, TagsMixin
from vpn.choices import *

__all__ = (
    'Tunnel',
    'TunnelGroup',
    'TunnelTermination',
)


class TunnelGroup(OrganizationalModel):
    """
    An administrative grouping of Tunnels. This can be used to correlate peer-to-peer tunnels which form a mesh,
    for example.
    """
    class Meta:
        ordering = ('name',)
        verbose_name = _('tunnel group')
        verbose_name_plural = _('tunnel groups')

    def get_absolute_url(self):
        return reverse('vpn:tunnelgroup', args=[self.pk])


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
    group = models.ForeignKey(
        to='vpn.TunnelGroup',
        on_delete=models.PROTECT,
        related_name='tunnels',
        blank=True,
        null=True
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
        constraints = (
            models.UniqueConstraint(
                fields=('group', 'name'),
                name='%(app_label)s_%(class)s_group_name'
            ),
            models.UniqueConstraint(
                fields=('name',),
                name='%(app_label)s_%(class)s_name',
                condition=Q(group__isnull=True)
            ),
        )
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
    termination_type = models.ForeignKey(
        to='contenttypes.ContentType',
        on_delete=models.PROTECT,
        related_name='+'
    )
    termination_id = models.PositiveBigIntegerField(
        blank=True,
        null=True
    )
    termination = GenericForeignKey(
        ct_field='termination_type',
        fk_field='termination_id'
    )
    outside_ip = models.ForeignKey(
        to='ipam.IPAddress',
        on_delete=models.PROTECT,
        related_name='tunnel_terminations',
        blank=True,
        null=True
    )

    prerequisite_models = (
        'vpn.Tunnel',
    )

    class Meta:
        ordering = ('tunnel', 'role', 'pk')
        indexes = (
            models.Index(fields=('termination_type', 'termination_id')),
        )
        constraints = (
            models.UniqueConstraint(
                fields=('termination_type', 'termination_id'),
                name='%(app_label)s_%(class)s_termination',
                violation_error_message=_("An object may be terminated to only one tunnel at a time.")
            ),
        )
        verbose_name = _('tunnel termination')
        verbose_name_plural = _('tunnel terminations')

    def __str__(self):
        return f'{self.tunnel}: Termination {self.pk}'

    def get_absolute_url(self):
        return reverse('vpn:tunneltermination', args=[self.pk])

    def get_role_color(self):
        return TunnelTerminationRoleChoices.colors.get(self.role)

    def clean(self):
        super().clean()

        # Check that the selected termination object is not already attached to a Tunnel
        if getattr(self.termination, 'tunnel_termination', None) and self.termination.tunnel_termination.pk != self.pk:
            raise ValidationError({
                'termination': _("{name} is already attached to a tunnel ({tunnel}).").format(
                    name=self.termination.name,
                    tunnel=self.termination.tunnel_termination.tunnel
                )
            })

    def to_objectchange(self, action):
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.tunnel
        return objectchange
