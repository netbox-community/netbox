from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Circuit, CircuitTermination


@receiver(post_save, sender=CircuitTermination)
def update_circuit(instance, **kwargs):
    """
    When a CircuitTermination has been modified, update its parent Circuit.
    """
    fields = {
        'last_updated': timezone.now(),
        f'termination_{instance.term_side.lower()}': instance.pk,
    }
    Circuit.objects.filter(pk=instance.circuit_id).update(**fields)
