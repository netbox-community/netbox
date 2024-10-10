from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

__all__ = (
    'RenderConfigMixin',
)


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
