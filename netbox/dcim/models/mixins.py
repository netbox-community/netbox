from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from dcim.choices import *
from utilities.utils import to_grams

__all__ = (
    'RenderConfigMixin',
    'WeightMixin',
)


class WeightMixin(models.Model):
    weight = models.DecimalField(
        verbose_name=_('weight'),
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True
    )
    weight_unit = models.CharField(
        verbose_name=_('weight unit'),
        max_length=50,
        choices=WeightUnitChoices,
        blank=True,
    )
    # Stores the normalized weight (in grams) for database ordering
    _abs_weight = models.PositiveBigIntegerField(
        blank=True,
        null=True
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):

        # Store the given weight (if any) in grams for use in database ordering
        if self.weight and self.weight_unit:
            self._abs_weight = to_grams(self.weight, self.weight_unit)
        else:
            self._abs_weight = None

        super().save(*args, **kwargs)

    def clean(self):
        super().clean()

        # Validate weight and weight_unit
        if self.weight and not self.weight_unit:
            raise ValidationError(_("Must specify a unit when setting a weight"))


class RenderConfigMixin(models.Model):
    config_template = models.ForeignKey(
        to='extras.ConfigTemplate',
        on_delete=models.PROTECT,
        related_name='%(class)ss',
        blank=True,
        null=True
    )

    class Meta:
        abstract = True

    def get_config_template(self):
        """
        Return the appropriate ConfigTemplate (if any) for this Device.
        """
        if self.config_template:
            return self.config_template
        if self.role and self.role.config_template:
            return self.role.config_template
        if self.platform and self.platform.config_template:
            return self.platform.config_template
