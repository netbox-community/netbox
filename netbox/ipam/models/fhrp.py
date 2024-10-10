from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ipam.choices import *
from ipam.constants import *
from netbox.models import ChangeLoggedModel, PrimaryModel

__all__ = (
    'FHRPGroup',
    'FHRPGroupAssignment',
)


class FHRPGroup(PrimaryModel):
    """
    A grouping of next hope resolution protocol (FHRP) peers. (For instance, VRRP or HSRP.)
    """
    group_id = models.PositiveSmallIntegerField(
        verbose_name=_('group ID')
    )
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        blank=True
    )
    protocol = models.CharField(
        verbose_name=_('protocol'),
        max_length=50,
        choices=FHRPGroupProtocolChoices
    )
    auth_type = models.CharField(
        max_length=50,
        choices=FHRPGroupAuthTypeChoices,
        blank=True,
        verbose_name=_('authentication type')
    )
    auth_key = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('authentication key')
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
        verbose_name = _('FHRP group')
        verbose_name_plural = _('FHRP groups')

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


class FHRPGroupAssignment(ChangeLoggedModel):
    interface_type = models.ForeignKey(
        to='contenttypes.ContentType',
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
        verbose_name=_('priority'),
        validators=(
            MinValueValidator(FHRPGROUPASSIGNMENT_PRIORITY_MIN),
            MaxValueValidator(FHRPGROUPASSIGNMENT_PRIORITY_MAX)
        )
    )

    clone_fields = ('interface_type', 'interface_id')

    class Meta:
        ordering = ('-priority', 'pk')
        indexes = (
            models.Index(fields=('interface_type', 'interface_id')),
        )
        constraints = (
            models.UniqueConstraint(
                fields=('interface_type', 'interface_id', 'group'),
                name='%(app_label)s_%(class)s_unique_interface_group'
            ),
        )
        verbose_name = _('FHRP group assignment')
        verbose_name_plural = _('FHRP group assignments')

    def __str__(self):
        return f'{self.interface}: {self.group} ({self.priority})'

    def get_absolute_url(self):
        # Used primarily for redirection after creating a new assignment
        if self.interface:
            return self.interface.get_absolute_url()
        return None
