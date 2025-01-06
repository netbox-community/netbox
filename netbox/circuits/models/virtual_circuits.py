from functools import cached_property

from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from circuits.choices import *
from netbox.models import ChangeLoggedModel, PrimaryModel
from netbox.models.features import CustomFieldsMixin, CustomLinksMixin, TagsMixin
from .base import BaseCircuitType

__all__ = (
    'VirtualCircuit',
    'VirtualCircuitTermination',
    'VirtualCircuitType',
)


class VirtualCircuitType(BaseCircuitType):
    """
    Like physical circuits, virtual circuits can be organized by their functional role. For example, a user might wish
    to categorize virtual circuits by their technological nature or by product name.
    """
    class Meta:
        ordering = ('name',)
        verbose_name = _('virtual circuit type')
        verbose_name_plural = _('virtual circuit types')


class VirtualCircuit(PrimaryModel):
    """
    A virtual connection between two or more endpoints, delivered across one or more physical circuits.
    """
    cid = models.CharField(
        max_length=100,
        verbose_name=_('circuit ID'),
        help_text=_('Unique circuit ID')
    )
    provider_network = models.ForeignKey(
        to='circuits.ProviderNetwork',
        on_delete=models.PROTECT,
        related_name='virtual_circuits'
    )
    provider_account = models.ForeignKey(
        to='circuits.ProviderAccount',
        on_delete=models.PROTECT,
        related_name='virtual_circuits',
        blank=True,
        null=True
    )
    type = models.ForeignKey(
        to='circuits.VirtualCircuitType',
        on_delete=models.PROTECT,
        related_name='virtual_circuits'
    )
    status = models.CharField(
        verbose_name=_('status'),
        max_length=50,
        choices=CircuitStatusChoices,
        default=CircuitStatusChoices.STATUS_ACTIVE
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='virtual_circuits',
        blank=True,
        null=True
    )

    group_assignments = GenericRelation(
        to='circuits.CircuitGroupAssignment',
        content_type_field='member_type',
        object_id_field='member_id',
        related_query_name='virtual_circuit'
    )

    clone_fields = (
        'provider_network', 'provider_account', 'status', 'tenant', 'description',
    )
    prerequisite_models = (
        'circuits.ProviderNetwork',
        'circuits.VirtualCircuitType',
    )

    class Meta:
        ordering = ['provider_network', 'provider_account', 'cid']
        constraints = (
            models.UniqueConstraint(
                fields=('provider_network', 'cid'),
                name='%(app_label)s_%(class)s_unique_provider_network_cid'
            ),
            models.UniqueConstraint(
                fields=('provider_account', 'cid'),
                name='%(app_label)s_%(class)s_unique_provideraccount_cid'
            ),
        )
        verbose_name = _('virtual circuit')
        verbose_name_plural = _('virtual circuits')

    def __str__(self):
        return self.cid

    def get_status_color(self):
        return CircuitStatusChoices.colors.get(self.status)

    def clean(self):
        super().clean()

        if self.provider_account and self.provider_network.provider != self.provider_account.provider:
            raise ValidationError({
                'provider_account': "The assigned account must belong to the provider of the assigned network."
            })

    @property
    def provider(self):
        return self.provider_network.provider


class VirtualCircuitTermination(
    CustomFieldsMixin,
    CustomLinksMixin,
    TagsMixin,
    ChangeLoggedModel
):
    virtual_circuit = models.ForeignKey(
        to='circuits.VirtualCircuit',
        on_delete=models.CASCADE,
        related_name='terminations'
    )
    role = models.CharField(
        verbose_name=_('role'),
        max_length=50,
        choices=VirtualCircuitTerminationRoleChoices,
        default=VirtualCircuitTerminationRoleChoices.ROLE_PEER
    )
    interface = models.OneToOneField(
        to='dcim.Interface',
        on_delete=models.CASCADE,
        related_name='virtual_circuit_termination'
    )
    description = models.CharField(
        verbose_name=_('description'),
        max_length=200,
        blank=True
    )

    class Meta:
        ordering = ['virtual_circuit', 'role', 'pk']
        verbose_name = _('virtual circuit termination')
        verbose_name_plural = _('virtual circuit terminations')

    def __str__(self):
        return f'{self.virtual_circuit}: {self.get_role_display()} termination'

    def get_absolute_url(self):
        return reverse('circuits:virtualcircuittermination', args=[self.pk])

    def get_role_color(self):
        return VirtualCircuitTerminationRoleChoices.colors.get(self.role)

    def to_objectchange(self, action):
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.virtual_circuit
        return objectchange

    @property
    def parent_object(self):
        return self.virtual_circuit

    @cached_property
    def peer_terminations(self):
        if self.role == VirtualCircuitTerminationRoleChoices.ROLE_PEER:
            return self.virtual_circuit.terminations.exclude(pk=self.pk).filter(
                role=VirtualCircuitTerminationRoleChoices.ROLE_PEER
            )
        if self.role == VirtualCircuitTerminationRoleChoices.ROLE_HUB:
            return self.virtual_circuit.terminations.filter(
                role=VirtualCircuitTerminationRoleChoices.ROLE_SPOKE
            )
        if self.role == VirtualCircuitTerminationRoleChoices.ROLE_SPOKE:
            return self.virtual_circuit.terminations.filter(
                role=VirtualCircuitTerminationRoleChoices.ROLE_HUB
            )

    def clean(self):
        super().clean()

        if self.interface and not self.interface.is_virtual:
            raise ValidationError("Virtual circuits may be terminated only to virtual interfaces.")
