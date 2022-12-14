from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse

from netbox.models import ChangeLoggedModel, PrimaryModel
from netbox.models.features import WebhooksMixin
from ipam.choices import *
from ipam.constants import *

__all__ = (
    'FHRPGroup',
    'FHRPGroupAssignment',
)


class FHRPGroup(PrimaryModel):
    """
    A grouping of next hope resolution protocol (FHRP) peers. (For instance, VRRP or HSRP.)
    """
    group_id = models.PositiveSmallIntegerField(
        verbose_name='Group ID'
    )
    name = models.CharField(
        max_length=100,
        blank=True
    )
    protocol = models.CharField(
        max_length=50,
        choices=FHRPGroupProtocolChoices
    )
    auth_type = models.CharField(
        max_length=50,
        choices=FHRPGroupAuthTypeChoices,
        blank=True,
        verbose_name='Authentication type'
    )
    auth_key = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Authentication key'
    )
    ip_addresses = GenericRelation(
        to='ipam.IPAddress',
        content_type_field='assigned_object_type',
        object_id_field='assigned_object_id',
        related_query_name='fhrpgroup'
    )

    clone_fields = ('protocol', 'auth_type', 'auth_key', 'description')

    class Meta:
        ordering = ['protocol', 'group_id', 'pk']
        verbose_name = 'FHRP group'

    def __str__(self):
        name = ''
        if self.name:
            name = f'{self.name} '

        name += f'{self.get_protocol_display()}: {self.group_id}'

        # Append the first assigned IP addresses (if any) to serve as an additional identifier
        if self.pk:
            ip_address = self.ip_addresses.first()
            if ip_address:
                return f"{name} ({ip_address})"

        return name

    def get_absolute_url(self):
        return reverse('ipam:fhrpgroup', args=[self.pk])


class FHRPGroupAssignment(WebhooksMixin, ChangeLoggedModel):
    interface_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE
    )
    interface_id = models.PositiveBigIntegerField()
    interface = GenericForeignKey(
        ct_field='interface_type',
        fk_field='interface_id'
    )
    group = models.ForeignKey(
        to='ipam.FHRPGroup',
        on_delete=models.CASCADE
    )
    priority = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(FHRPGROUPASSIGNMENT_PRIORITY_MIN),
            MaxValueValidator(FHRPGROUPASSIGNMENT_PRIORITY_MAX)
        )
    )

    clone_fields = ('interface_type', 'interface_id')

    class Meta:
        ordering = ('-priority', 'pk')
        constraints = (
            models.UniqueConstraint(
                fields=('interface_type', 'interface_id', 'group'),
                name='%(app_label)s_%(class)s_unique_interface_group'
            ),
        )
        verbose_name = 'FHRP group assignment'

    def __str__(self):
        return f'{self.interface}: {self.group} ({self.priority})'

    def get_absolute_url(self):
        # Used primarily for redirection after creating a new assignment
        if self.interface:
            return self.interface.get_absolute_url()
        return None
