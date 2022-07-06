from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from ipam.choices import L2VPNTypeChoices
from ipam.constants import L2VPN_ASSIGNMENT_MODELS
from netbox.models import NetBoxModel


class L2VPN(NetBoxModel):
    name = models.CharField(
        max_length=100,
        unique=True
    )
    slug = models.SlugField()
    type = models.CharField(max_length=50, choices=L2VPNTypeChoices)
    identifier = models.BigIntegerField(
        null=True,
        blank=True,
        unique=True
    )
    import_targets = models.ManyToManyField(
        to='ipam.RouteTarget',
        related_name='importing_l2vpns',
        blank=True,
    )
    export_targets = models.ManyToManyField(
        to='ipam.RouteTarget',
        related_name='exporting_l2vpns',
        blank=True
    )
    description = models.TextField(null=True, blank=True)
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='l2vpns',
        blank=True,
        null=True
    )
    contacts = GenericRelation(
        to='tenancy.ContactAssignment'
    )

    class Meta:
        ordering = ('identifier', 'name')
        verbose_name = 'L2VPN'

    def __str__(self):
        if self.identifier:
            return f'{self.name} ({self.identifier})'
        return f'{self.name}'

    def get_absolute_url(self):
        return reverse('ipam:l2vpn', args=[self.pk])


class L2VPNTermination(NetBoxModel):
    l2vpn = models.ForeignKey(
        to='ipam.L2VPN',
        on_delete=models.CASCADE,
        related_name='terminations'
    )
    assigned_object_type = models.ForeignKey(
        to=ContentType,
        limit_choices_to=L2VPN_ASSIGNMENT_MODELS,
        on_delete=models.PROTECT,
        related_name='+'
    )
    assigned_object_id = models.PositiveBigIntegerField()
    assigned_object = GenericForeignKey(
        ct_field='assigned_object_type',
        fk_field='assigned_object_id'
    )

    class Meta:
        ordering = ('l2vpn',)
        verbose_name = 'L2VPN Termination'
        constraints = (
            models.UniqueConstraint(
                fields=('assigned_object_type', 'assigned_object_id'),
                name='ipam_l2vpntermination_assigned_object'
            ),
        )

    def __str__(self):
        if self.pk is not None:
            return f'{self.assigned_object} <> {self.l2vpn}'
        return super().__str__()

    def get_absolute_url(self):
        return reverse('ipam:l2vpntermination', args=[self.pk])

    def clean(self):
        # Only check is assigned_object is set.  Required otherwise we have an Integrity Error thrown.
        if self.assigned_object:
            obj_id = self.assigned_object.pk
            obj_type = ContentType.objects.get_for_model(self.assigned_object)
            if L2VPNTermination.objects.filter(assigned_object_id=obj_id, assigned_object_type=obj_type).\
                    exclude(pk=self.pk).count() > 0:
                raise ValidationError(f'L2VPN Termination already assigned ({self.assigned_object})')

        # Only check if L2VPN is set and is of type P2P
        if self.l2vpn and self.l2vpn.type in L2VPNTypeChoices.P2P:
            terminations_count = L2VPNTermination.objects.filter(l2vpn=self.l2vpn).exclude(pk=self.pk).count()
            if terminations_count >= 2:
                l2vpn_type = self.l2vpn.get_type_display()
                raise ValidationError(
                    f'{l2vpn_type} L2VPNs cannot have more than two terminations; found {terminations_count} already '
                    f'defined.'
                )
