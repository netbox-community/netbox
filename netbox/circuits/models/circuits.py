from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from circuits.choices import *
from dcim.models import CabledObjectModel
from netbox.models import ChangeLoggedModel, OrganizationalModel, PrimaryModel
from netbox.models.features import ContactsMixin, CustomFieldsMixin, CustomLinksMixin, ExportTemplatesMixin, ImageAttachmentsMixin, TagsMixin
from utilities.fields import ColorField

__all__ = (
    'Circuit',
    'CircuitGroup',
    'CircuitGroupAssignment',
    'CircuitTermination',
    'CircuitType',
)


class CircuitType(OrganizationalModel):
    """
    Circuits can be organized by their functional role. For example, a user might wish to define CircuitTypes named
    "Long Haul," "Metro," or "Out-of-Band".
    """
    color = ColorField(
        verbose_name=_('color'),
        blank=True
    )

    def get_absolute_url(self):
        return reverse('circuits:circuittype', args=[self.pk])

    class Meta:
        ordering = ('name',)
        verbose_name = _('circuit type')
        verbose_name_plural = _('circuit types')


class Circuit(ContactsMixin, ImageAttachmentsMixin, PrimaryModel):
    """
    A communications circuit connects two points. Each Circuit belongs to a Provider; Providers may have multiple
    circuits. Each circuit is also assigned a CircuitType and a Site, and may optionally be assigned to a particular
    ProviderAccount. Circuit port speed and commit rate are measured in Kbps.
    """
    cid = models.CharField(
        max_length=100,
        verbose_name=_('circuit ID'),
        help_text=_('Unique circuit ID')
    )
    provider = models.ForeignKey(
        to='circuits.Provider',
        on_delete=models.PROTECT,
        related_name='circuits'
    )
    provider_account = models.ForeignKey(
        to='circuits.ProviderAccount',
        on_delete=models.PROTECT,
        related_name='circuits',
        blank=True,
        null=True
    )
    type = models.ForeignKey(
        to='CircuitType',
        on_delete=models.PROTECT,
        related_name='circuits'
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
        related_name='circuits',
        blank=True,
        null=True
    )
    install_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('installed')
    )
    termination_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('terminates')
    )
    commit_rate = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_('commit rate (Kbps)'),
        help_text=_("Committed rate")
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
        'provider', 'provider_account', 'type', 'status', 'tenant', 'install_date', 'termination_date', 'commit_rate',
        'description',
    )
    prerequisite_models = (
        'circuits.CircuitType',
        'circuits.Provider',
    )

    class Meta:
        ordering = ['provider', 'provider_account', 'cid']
        constraints = (
            models.UniqueConstraint(
                fields=('provider', 'cid'),
                name='%(app_label)s_%(class)s_unique_provider_cid'
            ),
            models.UniqueConstraint(
                fields=('provider_account', 'cid'),
                name='%(app_label)s_%(class)s_unique_provideraccount_cid'
            ),
        )
        verbose_name = _('circuit')
        verbose_name_plural = _('circuits')

    def __str__(self):
        return self.cid

    def get_absolute_url(self):
        return reverse('circuits:circuit', args=[self.pk])

    def get_status_color(self):
        return CircuitStatusChoices.colors.get(self.status)

    def clean(self):
        super().clean()

        if self.provider_account and self.provider != self.provider_account.provider:
            raise ValidationError({'provider_account': "The assigned account must belong to the assigned provider."})


class CircuitGroup(OrganizationalModel):
    """
    An administrative grouping of Circuits.
    """
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='circuit_groups',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = _('circuit group')
        verbose_name_plural = _('circuit groups')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('circuits:circuitgroup', args=[self.pk])


class CircuitGroupAssignment(CustomFieldsMixin, ExportTemplatesMixin, TagsMixin, ChangeLoggedModel):
    """
    Assignment of a Circuit to a CircuitGroup with an optional priority.
    """
    circuit = models.ForeignKey(
        Circuit,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    group = models.ForeignKey(
        CircuitGroup,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    priority = models.CharField(
        verbose_name=_('priority'),
        max_length=50,
        choices=CircuitPriorityChoices,
        blank=True
    )
    prerequisite_models = (
        'circuits.Circuit',
        'circuits.CircuitGroup',
    )

    class Meta:
        ordering = ('circuit', 'priority', 'pk')
        constraints = (
            models.UniqueConstraint(
                fields=('circuit', 'group'),
                name='%(app_label)s_%(class)s_unique_circuit_group'
            ),
        )
        verbose_name = _('Circuit group assignment')
        verbose_name_plural = _('Circuit group assignments')

    def __str__(self):
        if self.priority:
            return f"{self.group} ({self.get_priority_display()})"
        return str(self.group)

    def get_absolute_url(self):
        return reverse('circuits:circuitgroupassignment', args=[self.pk])


class CircuitTermination(
    CustomFieldsMixin,
    CustomLinksMixin,
    TagsMixin,
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
        verbose_name=_('termination')
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
        verbose_name=_('port speed (Kbps)'),
        blank=True,
        null=True,
        help_text=_('Physical circuit speed')
    )
    upstream_speed = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_('upstream speed (Kbps)'),
        help_text=_('Upstream speed, if different from port speed')
    )
    xconnect_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('cross-connect ID'),
        help_text=_('ID of the local cross-connect')
    )
    pp_info = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('patch panel/port(s)'),
        help_text=_('Patch panel ID and port number(s)')
    )
    description = models.CharField(
        verbose_name=_('description'),
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
        verbose_name = _('circuit termination')
        verbose_name_plural = _('circuit terminations')

    def __str__(self):
        return f'{self.circuit}: Termination {self.term_side}'

    def get_absolute_url(self):
        return reverse('circuits:circuittermination', args=[self.pk])

    def clean(self):
        super().clean()

        # Must define either site *or* provider network
        if self.site is None and self.provider_network is None:
            raise ValidationError(_("A circuit termination must attach to either a site or a provider network."))
        if self.site and self.provider_network:
            raise ValidationError(_("A circuit termination cannot attach to both a site and a provider network."))

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
