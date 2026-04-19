from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from dcim.constants import PORT_POSITION_MAX, PORT_POSITION_MIN

__all__ = (
    'PortMappingBase',
)


class PortMappingBase(models.Model):
    """
    Base class for PortMapping and PortTemplateMapping
    """
    front_port_position = models.PositiveSmallIntegerField(
        default=1,
        validators=(
            MinValueValidator(PORT_POSITION_MIN),
            MaxValueValidator(PORT_POSITION_MAX),
        ),
    )
    rear_port_position = models.PositiveSmallIntegerField(
        default=1,
        validators=(
            MinValueValidator(PORT_POSITION_MIN),
            MaxValueValidator(PORT_POSITION_MAX),
        ),
    )

    _netbox_private = True

    class Meta:
        abstract = True
        constraints = (
            models.UniqueConstraint(
                fields=('front_port', 'front_port_position'),
                name='%(app_label)s_%(class)s_unique_front_port_position'
            ),
            models.UniqueConstraint(
                fields=('rear_port', 'rear_port_position'),
                name='%(app_label)s_%(class)s_unique_rear_port_position'
            ),
        )

    def clean(self):
        super().clean()
        from netbox.validators import validator_registry
        validator_registry.validate(self)
