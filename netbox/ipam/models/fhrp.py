from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse

from extras.utils import extras_features
from netbox.models import ChangeLoggedModel, PrimaryModel
from ipam.choices import *
from utilities.querysets import RestrictedQuerySet

__all__ = (
    'FHRPGroup',
    'FHRPGroupAssignment',
)


@extras_features('custom_fields', 'custom_links', 'export_templates', 'tags', 'webhooks')
class FHRPGroup(PrimaryModel):
    """
    A grouping of next hope resolution protocol (FHRP) peers. (For instance, VRRP or HSRP.)
    """
    group_id = models.PositiveSmallIntegerField(
        verbose_name='Group ID'
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
    description = models.CharField(
        max_length=200,
        blank=True
    )
    ip_addresses = GenericRelation(
        to='ipam.IPAddress',
        content_type_field='assigned_object_type',
        object_id_field='assigned_object_id',
        related_query_name='nhrp_group'
    )

    objects = RestrictedQuerySet.as_manager()

    clone_fields = [
        'protocol', 'auth_type', 'auth_key'
    ]

    class Meta:
        ordering = ['protocol', 'group_id', 'pk']
        verbose_name = 'FHRP group'

    def __str__(self):
        return f'{self.get_protocol_display()} group {self.group_id}'

    def get_absolute_url(self):
        return reverse('ipam:fhrpgroup', args=[self.pk])


@extras_features('webhooks')
class FHRPGroupAssignment(ChangeLoggedModel):
    content_type = models.ForeignKey(
        to=ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    object = GenericForeignKey(
        ct_field='content_type',
        fk_field='object_id'
    )
    group = models.ForeignKey(
        to='ipam.FHRPGroup',
        on_delete=models.CASCADE
    )
    priority = models.PositiveSmallIntegerField(
        blank=True,
        null=True
    )

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        ordering = ('priority', 'pk')
        unique_together = ('content_type', 'object_id', 'group')
        verbose_name = 'FHRP group assignment'
