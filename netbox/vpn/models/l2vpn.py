from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from core.models import ObjectType
from netbox.models import NetBoxModel, PrimaryModel
from netbox.models.features import ContactsMixin
from vpn.choices import L2VPNTypeChoices
from vpn.constants import L2VPN_ASSIGNMENT_MODELS

__all__ = (
    'L2VPN',
    'L2VPNTermination',
)


class L2VPN(ContactsMixin, PrimaryModel):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100,
        unique=True
    )
    slug = models.SlugField(
        verbose_name=_('slug'),
        max_length=100,
        unique=True
    )
    type = models.CharField(
        verbose_name=_('type'),
        max_length=50,
        choices=L2VPNTypeChoices
    )
    identifier = models.BigIntegerField(
        verbose_name=_('identifier'),
        null=True,
        blank=True
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
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='l2vpns',
        blank=True,
        null=True
    )

    clone_fields = ('type',)

    class Meta:
        ordering = ('name', 'identifier')
        verbose_name = _('L2VPN')
        verbose_name_plural = _('L2VPNs')

    def __str__(self):
        if self.identifier:
            return f'{self.name} ({self.identifier})'
        return f'{self.name}'

    @cached_property
    def can_add_termination(self):
        if self.type in L2VPNTypeChoices.P2P and self.terminations.count() >= 2:
            return False
        else:
            return True


class L2VPNTermination(NetBoxModel):
    l2vpn = models.ForeignKey(
        to='vpn.L2VPN',
        on_delete=models.CASCADE,
        related_name='terminations'
    )
    assigned_object_type = models.ForeignKey(
        to='contenttypes.ContentType',
        limit_choices_to=L2VPN_ASSIGNMENT_MODELS,
        on_delete=models.PROTECT,
        related_name='+'
    )
    assigned_object_id = models.PositiveBigIntegerField()
    assigned_object = GenericForeignKey(
        ct_field='assigned_object_type',
        fk_field='assigned_object_id'
    )

    clone_fields = ('l2vpn',)
    prerequisite_models = (
        'vpn.L2VPN',
    )

    class Meta:
        ordering = ('l2vpn',)
        indexes = (
            models.Index(fields=('assigned_object_type', 'assigned_object_id')),
        )
        constraints = (
            models.UniqueConstraint(
                fields=('assigned_object_type', 'assigned_object_id'),
                name='vpn_l2vpntermination_assigned_object'
            ),
        )
        verbose_name = _('L2VPN termination')
        verbose_name_plural = _('L2VPN terminations')

    def __str__(self):
        if self.pk is not None:
            return f'{self.assigned_object} <> {self.l2vpn}'
        return super().__str__()

    def clean(self):
        # Only check is assigned_object is set.  Required otherwise we have an Integrity Error thrown.
        if self.assigned_object:
            obj_id = self.assigned_object.pk
            obj_type = ObjectType.objects.get_for_model(self.assigned_object)
            if L2VPNTermination.objects.filter(assigned_object_id=obj_id, assigned_object_type=obj_type).\
                    exclude(pk=self.pk).count() > 0:
                raise ValidationError(
                    _('L2VPN Termination already assigned ({assigned_object})').format(
                        assigned_object=self.assigned_object
                    )
                )

        # Only check if L2VPN is set and is of type P2P
        if hasattr(self, 'l2vpn') and self.l2vpn.type in L2VPNTypeChoices.P2P:
            terminations_count = L2VPNTermination.objects.filter(l2vpn=self.l2vpn).exclude(pk=self.pk).count()
            if terminations_count >= 2:
                l2vpn_type = self.l2vpn.get_type_display()
                raise ValidationError(
                    _(
                        '{l2vpn_type} L2VPNs cannot have more than two terminations; found {terminations_count} '
                        'already defined.'
                    ).format(l2vpn_type=l2vpn_type, terminations_count=terminations_count))

    @property
    def assigned_object_parent(self):
        obj_type = ObjectType.objects.get_for_model(self.assigned_object)
        if obj_type.model == 'vminterface':
            return self.assigned_object.virtual_machine
        elif obj_type.model == 'interface':
            return self.assigned_object.device
        elif obj_type.model == 'vminterface':
            return self.assigned_object.virtual_machine
        return None

    @property
    def assigned_object_site(self):
        return self.assigned_object_parent.site
