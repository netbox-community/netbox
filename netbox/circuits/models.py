from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from taggit.managers import TaggableManager

from dcim.constants import STATUS_CLASSES
from dcim.fields import ASNField
from extras.models import CustomFieldModel, ObjectChange
from utilities.models import ChangeLoggedModel
from utilities.utils import serialize_object
from .constants import CIRCUIT_STATUS_ACTIVE, CIRCUIT_STATUS_CHOICES, TERM_SIDE_CHOICES


@python_2_unicode_compatible
class Provider(ChangeLoggedModel, CustomFieldModel):
    """
    Each Circuit belongs to a Provider. This is usually a telecommunications company or similar organization. This model
    stores information pertinent to the user's relationship with the Provider.
    """
    name = models.CharField(
        max_length=50,
        unique=True
    )
    slug = models.SlugField(
        unique=True
    )
    asn = ASNField(
        blank=True,
        null=True,
        verbose_name='ASN'
    )
    account = models.CharField(
        max_length=30,
        blank=True,
        verbose_name='Account number'
    )
    portal_url = models.URLField(
        blank=True,
        verbose_name='Portal'
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
    custom_field_values = GenericRelation(
        to='extras.CustomFieldValue',
        content_type_field='obj_type',
        object_id_field='obj_id'
    )

    tags = TaggableManager()

    csv_headers = ['name', 'slug', 'asn', 'account', 'portal_url', 'noc_contact', 'admin_contact', 'comments']

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


@python_2_unicode_compatible
class CircuitType(ChangeLoggedModel):
    """
    Circuits can be organized by their functional role. For example, a user might wish to define CircuitTypes named
    "Long Haul," "Metro," or "Out-of-Band".
    """
    name = models.CharField(
        max_length=50,
        unique=True
    )
    slug = models.SlugField(
        unique=True
    )

    csv_headers = ['name', 'slug']

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
        )


@python_2_unicode_compatible
class Circuit(ChangeLoggedModel, CustomFieldModel):
    """
    A communications circuit connects two points. Each Circuit belongs to a Provider; Providers may have multiple
    circuits. Each circuit is also assigned a CircuitType and a Site. A Circuit may be terminated to a specific device
    interface, but this is not required. Circuit port speed and commit rate are measured in Kbps.
    """
    cid = models.CharField(
        max_length=50,
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
    status = models.PositiveSmallIntegerField(
        choices=CIRCUIT_STATUS_CHOICES,
        default=CIRCUIT_STATUS_ACTIVE
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
        max_length=100,
        blank=True
    )
    comments = models.TextField(
        blank=True
    )
    custom_field_values = GenericRelation(
        to='extras.CustomFieldValue',
        content_type_field='obj_type',
        object_id_field='obj_id'
    )

    tags = TaggableManager()

    csv_headers = [
        'cid', 'provider', 'type', 'status', 'tenant', 'install_date', 'commit_rate', 'description', 'comments',
    ]

    class Meta:
        ordering = ['provider', 'cid']
        unique_together = ['provider', 'cid']

    def __str__(self):
        return '{} {}'.format(self.provider, self.cid)

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
        return STATUS_CLASSES[self.status]

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


@python_2_unicode_compatible
class CircuitTermination(models.Model):
    circuit = models.ForeignKey(
        to='circuits.Circuit',
        on_delete=models.CASCADE,
        related_name='terminations'
    )
    term_side = models.CharField(
        max_length=1,
        choices=TERM_SIDE_CHOICES,
        verbose_name='Termination'
    )
    site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.PROTECT,
        related_name='circuit_terminations'
    )
    interface = models.OneToOneField(
        to='dcim.Interface',
        on_delete=models.PROTECT,
        related_name='circuit_termination',
        blank=True,
        null=True
    )
    port_speed = models.PositiveIntegerField(
        verbose_name='Port speed (Kbps)'
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

    class Meta:
        ordering = ['circuit', 'term_side']
        unique_together = ['circuit', 'term_side']

    def __str__(self):
        return '{} (Side {})'.format(self.circuit, self.get_term_side_display())

    def log_change(self, user, request_id, action):
        """
        Reference the parent circuit when recording the change.
        """
        ObjectChange(
            user=user,
            request_id=request_id,
            changed_object=self,
            related_object=self.circuit,
            action=action,
            object_data=serialize_object(self)
        ).save()

    def get_peer_termination(self):
        peer_side = 'Z' if self.term_side == 'A' else 'A'
        try:
            return CircuitTermination.objects.select_related('site').get(circuit=self.circuit, term_side=peer_side)
        except CircuitTermination.DoesNotExist:
            return None
