from django.db import models
from django.urls import reverse
from taggit.managers import TaggableManager

from dcim.fields import ASNField
from dcim.models import CableTermination, PathEndpoint
from extras.models import ChangeLoggedModel, CustomFieldModel, ObjectChange, TaggedItem
from extras.utils import extras_features
from utilities.querysets import RestrictedQuerySet
from utilities.utils import serialize_object
from .choices import *
from .querysets import CircuitQuerySet


__all__ = (
    'Circuit',
    'CircuitTermination',
    'CircuitType',
    'Provider',
)


@extras_features('custom_fields', 'custom_links', 'export_templates', 'webhooks')
class Provider(ChangeLoggedModel, CustomFieldModel):
    """
    Each Circuit belongs to a Provider. This is usually a telecommunications company or similar organization. This model
    stores information pertinent to the user's relationship with the Provider.
    """
    name = models.CharField(
        max_length=100,
        unique=True
    )
    slug = models.SlugField(
        max_length=100,
        unique=True
    )
    asn = ASNField(
        blank=True,
        null=True,
        verbose_name='ASN',
        help_text='32-bit autonomous system number'
    )
    account = models.CharField(
        max_length=30,
        blank=True,
        verbose_name='Account number'
    )
    portal_url = models.URLField(
        blank=True,
        verbose_name='Portal URL'
    )
    noc_contact = models.TextField(
        blank=True,
        verbose_name='NOC contact'
    )
    admin_contact = models.TextField(
        blank=True,
        verbose_name='Admin contact'
    )
    comments = models.TextField(
        blank=True
    )
    tags = TaggableManager(through=TaggedItem)

    objects = RestrictedQuerySet.as_manager()

    csv_headers = [
        'name', 'slug', 'asn', 'account', 'portal_url', 'noc_contact', 'admin_contact', 'comments',
    ]
    clone_fields = [
        'asn', 'account', 'portal_url', 'noc_contact', 'admin_contact',
    ]

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('circuits:provider', args=[self.slug])

    def to_csv(self):
        return (
            self.name,
            self.slug,
            self.asn,
            self.account,
            self.portal_url,
            self.noc_contact,
            self.admin_contact,
            self.comments,
        )


class CircuitType(ChangeLoggedModel):
    """
    Circuits can be organized by their functional role. For example, a user might wish to define CircuitTypes named
    "Long Haul," "Metro," or "Out-of-Band".
    """
    name = models.CharField(
        max_length=100,
        unique=True
    )
    slug = models.SlugField(
        max_length=100,
        unique=True
    )
    description = models.CharField(
        max_length=200,
        blank=True,
    )

    objects = RestrictedQuerySet.as_manager()

    csv_headers = ['name', 'slug', 'description']

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "{}?type={}".format(reverse('circuits:circuit_list'), self.slug)

    def to_csv(self):
        return (
            self.name,
            self.slug,
            self.description,
        )


@extras_features('custom_fields', 'custom_links', 'export_templates', 'webhooks')
class Circuit(ChangeLoggedModel, CustomFieldModel):
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
        verbose_name='Date installed'
    )
    commit_rate = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Commit rate (Kbps)')
    description = models.CharField(
        max_length=200,
        blank=True
    )
    comments = models.TextField(
        blank=True
    )

    objects = CircuitQuerySet.as_manager()
    tags = TaggableManager(through=TaggedItem)

    csv_headers = [
        'cid', 'provider', 'type', 'status', 'tenant', 'install_date', 'commit_rate', 'description', 'comments',
    ]
    clone_fields = [
        'provider', 'type', 'status', 'tenant', 'install_date', 'commit_rate', 'description',
    ]

    class Meta:
        ordering = ['provider', 'cid']
        unique_together = ['provider', 'cid']

    def __str__(self):
        return self.cid

    def get_absolute_url(self):
        return reverse('circuits:circuit', args=[self.pk])

    def to_csv(self):
        return (
            self.cid,
            self.provider.name,
            self.type.name,
            self.get_status_display(),
            self.tenant.name if self.tenant else None,
            self.install_date,
            self.commit_rate,
            self.description,
            self.comments,
        )

    def get_status_class(self):
        return CircuitStatusChoices.CSS_CLASSES.get(self.status)

    def _get_termination(self, side):
        for ct in self.terminations.all():
            if ct.term_side == side:
                return ct
        return None

    @property
    def termination_a(self):
        return self._get_termination('A')

    @property
    def termination_z(self):
        return self._get_termination('Z')


class CircuitTermination(PathEndpoint, CableTermination):
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
        related_name='circuit_terminations'
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
        help_text='Upstream speed, if different from port speed'
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

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        ordering = ['circuit', 'term_side']
        unique_together = ['circuit', 'term_side']

    def __str__(self):
        return 'Side {}'.format(self.get_term_side_display())

    def to_objectchange(self, action):
        # Annotate the parent Circuit
        try:
            related_object = self.circuit
        except Circuit.DoesNotExist:
            # Parent circuit has been deleted
            related_object = None

        return ObjectChange(
            changed_object=self,
            object_repr=str(self),
            action=action,
            related_object=related_object,
            object_data=serialize_object(self)
        )

    @property
    def parent(self):
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
