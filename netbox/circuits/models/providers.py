from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from netbox.models import PrimaryModel
from netbox.models.features import ContactsMixin

__all__ = (
    'ProviderNetwork',
    'Provider',
    'ProviderAccount',
)


class Provider(ContactsMixin, PrimaryModel):
    """
    Each Circuit belongs to a Provider. This is usually a telecommunications company or similar organization. This model
    stores information pertinent to the user's relationship with the Provider.
    """
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        unique=True,
        help_text=_('Full name of the provider')
    )
    slug = models.SlugField(
        verbose_name=_('slug'),
        max_length=100,
        unique=True
    )
    asns = models.ManyToManyField(
        to='ipam.ASN',
        related_name='providers',
        blank=True
    )

    clone_fields = ()

    class Meta:
        ordering = ['name']
        verbose_name = _('provider')
        verbose_name_plural = _('providers')

    def __str__(self):
        return self.name


class ProviderAccount(ContactsMixin, PrimaryModel):
    """
    This is a discrete account within a provider.  Each Circuit belongs to a Provider Account.
    """
    provider = models.ForeignKey(
        to='circuits.Provider',
        on_delete=models.PROTECT,
        related_name='accounts'
    )
    account = models.CharField(
        max_length=100,
        verbose_name=_('account ID')
    )
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        blank=True
    )

    clone_fields = ('provider', )

    class Meta:
        ordering = ('provider', 'account')
        constraints = (
            models.UniqueConstraint(
                fields=('provider', 'account'),
                name='%(app_label)s_%(class)s_unique_provider_account'
            ),
            models.UniqueConstraint(
                fields=('provider', 'name'),
                name='%(app_label)s_%(class)s_unique_provider_name',
                condition=~Q(name="")
            ),
        )
        verbose_name = _('provider account')
        verbose_name_plural = _('provider accounts')

    def __str__(self):
        if self.name:
            return f'{self.account} ({self.name})'
        return f'{self.account}'


class ProviderNetwork(PrimaryModel):
    """
    This represents a provider network which exists outside of NetBox, the details of which are unknown or
    unimportant to the user.
    """
    name = models.CharField(
        verbose_name=_('name'),
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
        verbose_name=_('service ID')
    )

    class Meta:
        ordering = ('provider', 'name')
        constraints = (
            models.UniqueConstraint(
                fields=('provider', 'name'),
                name='%(app_label)s_%(class)s_unique_provider_name'
            ),
        )
        verbose_name = _('provider network')
        verbose_name_plural = _('provider networks')

    def __str__(self):
        return self.name
