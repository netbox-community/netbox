from django.apps import apps
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _

from circuits.choices import *
from dcim.models import CabledObjectModel
from netbox.models import (
    ChangeLoggedModel, CustomFieldsMixin, CustomLinksMixin, OrganizationalModel, PrimaryModel, TagsMixin,
)
from netbox.models.features import WebhooksMixin

__all__ = (
    'Circuit',
    'CircuitTermination',
    'CircuitType',
)


class CircuitType(OrganizationalModel):
    """
    Circuits can be organized by their functional role. For example, a user might wish to define CircuitTypes named
    "Long Haul," "Metro," or "Out-of-Band".
    """
    def get_absolute_url(self):
        return reverse('circuits:circuittype', args=[self.pk])


class Circuit(PrimaryModel):
    """
    A communications circuit connects two points. Each Circuit belongs to a Provider; Providers may have multiple
    circuits. Each circuit is also assigned a CircuitType and a Site.  Circuit port speed and commit rate are measured
    in Kbps.
    """
    cid = models.CharField(
        max_length=100,
        verbose_name='Circuit ID'
    )
    provider = models.ForeignKey(
        to='circuits.Provider',
        on_delete=models.PROTECT,
        related_name='circuits'
    )
    type = models.ForeignKey(
        to='CircuitType',
        on_delete=models.PROTECT,
        related_name='circuits'
    )
    status = models.CharField(
        max_length=50,
        choices=CircuitStatusChoices,
        default=CircuitStatusChoices.STATUS_ACTIVE
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='circuits',
        blank=True,
        null=True
    )
    install_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Installed'
    )
    termination_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Terminates'
    )
    commit_rate = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Commit rate (Kbps)')

    # Generic relations
    contacts = GenericRelation(
        to='tenancy.ContactAssignment'
    )
    images = GenericRelation(
        to='extras.ImageAttachment'
    )

    # Cache associated CircuitTerminations
    termination_a = models.ForeignKey(
        to='circuits.CircuitTermination',
        on_delete=models.SET_NULL,
        related_name='+',
        editable=False,
        blank=True,
        null=True
    )
    termination_z = models.ForeignKey(
        to='circuits.CircuitTermination',
        on_delete=models.SET_NULL,
        related_name='+',
        editable=False,
        blank=True,
        null=True
    )

    clone_fields = (
        'provider', 'type', 'status', 'tenant', 'install_date', 'termination_date', 'commit_rate', 'description',
    )
    prerequisite_models = (
        'circuits.CircuitType',
        'circuits.Provider',
    )

    class Meta:
        ordering = ['provider', 'cid']
        constraints = (
            models.UniqueConstraint(
                fields=('provider', 'cid'),
                name='%(app_label)s_%(class)s_unique_provider_cid'
            ),
        )

    def __str__(self):
        return self.cid

    def get_absolute_url(self):
        return reverse('circuits:circuit', args=[self.pk])

    def get_status_color(self):
        return CircuitStatusChoices.colors.get(self.status)


class CircuitTermination(
    CustomFieldsMixin,
    CustomLinksMixin,
    TagsMixin,
    WebhooksMixin,
    ChangeLoggedModel,
    CabledObjectModel
):
    circuit = models.ForeignKey(
        to='circuits.Circuit',
        on_delete=models.CASCADE,
        related_name='terminations'
    )
    term_side = models.CharField(
        max_length=1,
        choices=CircuitTerminationSideChoices,
        verbose_name='Termination'
    )
    site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.PROTECT,
        related_name='circuit_terminations',
        blank=True,
        null=True
    )
    provider_network = models.ForeignKey(
        to='circuits.ProviderNetwork',
        on_delete=models.PROTECT,
        related_name='circuit_terminations',
        blank=True,
        null=True
    )
    port_speed = models.PositiveIntegerField(
        verbose_name='Port speed (Kbps)',
        blank=True,
        null=True
    )
    upstream_speed = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Upstream speed (Kbps)',
        help_text=_('Upstream speed, if different from port speed')
    )
    xconnect_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Cross-connect ID'
    )
    pp_info = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Patch panel/port(s)'
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )

    class Meta:
        ordering = ['circuit', 'term_side']
        constraints = (
            models.UniqueConstraint(
                fields=('circuit', 'term_side'),
                name='%(app_label)s_%(class)s_unique_circuit_term_side'
            ),
        )

    def __str__(self):
        return f'{self.circuit}: Termination {self.term_side}'

    def get_absolute_url(self):
        return self.circuit.get_absolute_url()

    def clean(self):
        super().clean()

        # Must define either site *or* provider network
        if self.site is None and self.provider_network is None:
            raise ValidationError("A circuit termination must attach to either a site or a provider network.")
        if self.site and self.provider_network:
            raise ValidationError("A circuit termination cannot attach to both a site and a provider network.")

    def to_objectchange(self, action):
        objectchange = super().to_objectchange(action)
        objectchange.related_object = self.circuit
        return objectchange

    @property
    def parent_object(self):
        return self.circuit

    def get_peer_termination(self):
        peer_side = 'Z' if self.term_side == 'A' else 'A'
        try:
            return CircuitTermination.objects.prefetch_related('site').get(
                circuit=self.circuit,
                term_side=peer_side
            )
        except CircuitTermination.DoesNotExist:
            return None
