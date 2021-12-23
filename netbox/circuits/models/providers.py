from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse

from dcim.fields import ASNField
from extras.utils import extras_features
from netbox.models import PrimaryModel

__all__ = (
    'ProviderNetwork',
    'Provider',
)


@extras_features('custom_fields', 'custom_links', 'export_templates', 'tags', 'webhooks')
class Provider(PrimaryModel):
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

    # Generic relations
    contacts = GenericRelation(
        to='tenancy.ContactAssignment'
    )

    clone_fields = [
        'asn', 'account', 'portal_url', 'noc_contact', 'admin_contact',
    ]

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('circuits:provider', args=[self.pk])


@extras_features('custom_fields', 'custom_links', 'export_templates', 'tags', 'webhooks')
class ProviderNetwork(PrimaryModel):
    """
    This represents a provider network which exists outside of NetBox, the details of which are unknown or
    unimportant to the user.
    """
    name = models.CharField(
        max_length=100
    )
    provider = models.ForeignKey(
        to='circuits.Provider',
        on_delete=models.PROTECT,
        related_name='networks'
    )
    service_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Service ID'
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )
    comments = models.TextField(
        blank=True
    )

    class Meta:
        ordering = ('provider', 'name')
        constraints = (
            models.UniqueConstraint(
                fields=('provider', 'name'),
                name='circuits_providernetwork_provider_name'
            ),
        )
        unique_together = ('provider', 'name')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('circuits:providernetwork', args=[self.pk])
