from django.utils.translation import gettext_lazy as _

from netbox.models import OrganizationalModel
from utilities.fields import ColorField

__all__ = (
    'BaseCircuitType',
)


class BaseCircuitType(OrganizationalModel):
    """
    Abstract base model to represent a type of physical or virtual circuit.
    Circuits can be organized by their functional role. For example, a user might wish to define CircuitTypes named
    "Long Haul," "Metro," or "Out-of-Band".
    """
    color = ColorField(
        verbose_name=_('color'),
        blank=True
    )

    class Meta:
        abstract = True
